const Module = require('module');
const fs = require('fs');
const path = require('path');
const yaml = require('js-yaml');
const originalLoad = Module._load;

// ── Configuration ──────────────────────────────────────────────────────────
let config = {
  mcp_server: { url: 'https://ghost-healer-brain.onrender.com', confidence_threshold: 0.5 },
  healing: { auto_patch: false }
};

try {
  const ghostYamlPath = process.env.GHOST_CONFIG || path.join(process.cwd(), '../../ghost.yaml');
  if (fs.existsSync(ghostYamlPath)) {
    const fileContent = fs.readFileSync(ghostYamlPath, 'utf8');
    const yamlConfig = yaml.load(fileContent);
    if (yamlConfig) config = { ...config, ...yamlConfig };
  }
} catch (e) {}

const BRAIN_URL = process.env.GHOST_BRAIN_URL || config.mcp_server.url;
const CONFIDENCE_THRESHOLD = config.mcp_server.confidence_threshold;


// ── Stack Parser & Reporter ────────────────────────────────────────────────
function findCallerFile() {
  const err = new Error();
  const stack = err.stack;
  if (!stack) return { file: null, line: 0 };
  const lines = stack.split('\n');
  for (const line of lines) {
    const match = line.match(/\((.*):(\d+):(\d+)\)/) || line.match(/at (.*):(\d+):(\d+)/);
    if (match) {
      const filePath = match[1];
      const lineNo = parseInt(match[2], 10) || 0;
      const isInternal = filePath.includes('node_modules') || 
                        filePath.includes('pw-hook.js') || 
                        filePath.includes('setup.ts') ||
                        filePath.includes('GhostLocator');
      
      if (!isInternal && fs.existsSync(filePath)) {
        return { file: filePath, line: lineNo };
      }
    }
  }
  return { file: null, line: 0 };
}

function getISTTimestamp() {
    const date = new Date();
    const istOffset = 5.5 * 60 * 60 * 1000;
    const istDate = new Date(date.getTime() + istOffset);
    return istDate.toISOString().replace('Z', '+05:30');
}

function findWorkspaceRoot() {
    let currentDir = process.cwd();
    while (true) {
        if (fs.existsSync(path.join(currentDir, 'ghost.yaml')) || fs.existsSync(path.join(currentDir, '.git'))) {
            return currentDir;
        }
        const parentDir = path.dirname(currentDir);
        if (parentDir === currentDir) {
            return path.resolve(__dirname, '../../..');
        }
        currentDir = parentDir;
    }
}

function writeToReport(oldSelector, newSelector, action, fileInfo, url, confidence) {
    const reportDir = path.join(findWorkspaceRoot(), 'reports', 'ghost');
    fs.mkdirSync(reportDir, { recursive: true });
    const reportFile = path.join(reportDir, 'suggested-fixes.json');
    let data = [];
    if (fs.existsSync(reportFile)) {
        try { data = JSON.parse(fs.readFileSync(reportFile, 'utf8')); } catch(e){}
    }
    data.push({
        timestamp: getISTTimestamp(),
        framework: "playwright",
        language: "javascript/typescript",
        file: fileInfo.file,
        line: fileInfo.line,
        action: action,
        old_locator: oldSelector,
        suggested_locator: newSelector,
        confidence: confidence || 0.0,
        page_url: url
    });
    fs.writeFileSync(reportFile, JSON.stringify(data, null, 2), 'utf8');
}


// ── Core Engine ────────────────────────────────────────────────────────────
async function consultBrain(selector, action, domSnapshot, pageUrl) {
  for (let attempt = 0; attempt < 3; attempt++) {
    try {
      const resp = await fetch(`${BRAIN_URL}/api/heal-locator`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ selector, action, dom_snapshot: domSnapshot, page_url: pageUrl, framework: "playwright-ts" }),
        signal: AbortSignal.timeout(30000),
      });
      if (!resp.ok) return null;
      const data = await resp.json();
      if (data.healed_locator && data.confidence >= CONFIDENCE_THRESHOLD) {
        console.log(`\n[GHOST] Healed '${selector}' → '${data.healed_locator}' (${(data.confidence * 100).toFixed(1)}%)`);
        return { healed_locator: data.healed_locator, confidence: data.confidence };
      }
      return null;
    } catch {
      await new Promise(r => setTimeout(r, (attempt + 1) * 3000));
    }
  }
  return null;
}

// ── Patching Logic ─────────────────────────────────────────────────────────
function makeHealed(original, action) {
  return async function(selector, ...args) {
    const firstArgs = [...args];
    let optionsIndex = 0;
    if (action === 'fill' || action === 'select' || action === 'press') {
      optionsIndex = 1;
    }

    if (firstArgs[optionsIndex] && typeof firstArgs[optionsIndex] === 'object') {
      firstArgs[optionsIndex] = { ...firstArgs[optionsIndex], timeout: 2000 };
    } else {
      while (firstArgs.length < optionsIndex) {
        firstArgs.push(undefined);
      }
      firstArgs[optionsIndex] = { timeout: 2000 };
    }

    try {
      return await original.apply(this, [selector, ...firstArgs]);
    } catch (err) {
      console.log(`[GHOST] ${action} failed for '${selector}'. Requesting AI heal...`);
      try {
        const dom = await this.content();
        const url = await this.url();
        const result = await consultBrain(selector, action, dom, url);
        if (result) {
          const { healed_locator, confidence } = result;
          writeToReport(selector, healed_locator, action, findCallerFile(), url, confidence);
          return await original.apply(this, [healed_locator, ...args]);
        }
      } catch (brainErr) {
        console.error('[GHOST] Brain error:', brainErr);
      }
      return await original.apply(this, [selector, ...args]);
    }
  };
}

function patchLocatorPrototype(locator) {
    const proto = Object.getPrototypeOf(locator);
    if (proto.__ghost_patched) return;
    proto.__ghost_patched = true;

    const actions = { click: 'click', fill: 'fill', hover: 'hover', check: 'check', dblclick: 'click', waitFor: 'wait', waitForSelector: 'wait' };

    for (const [method, action] of Object.entries(actions)) {
        if (typeof proto[method] === 'function') {
            const original = proto[method];
            proto[method] = async function(...args) {
                const selector = this.__ghost_selector || this.toString();
                const page = this.__ghost_page;

                const firstArgs = [...args];
                let optionsIndex = 0;
                if (method === 'fill' || method === 'selectOption' || method === 'press') {
                    optionsIndex = 1;
                }

                if (firstArgs[optionsIndex] && typeof firstArgs[optionsIndex] === 'object') {
                    firstArgs[optionsIndex] = { ...firstArgs[optionsIndex], timeout: 2000 };
                } else {
                    while (firstArgs.length < optionsIndex) {
                        firstArgs.push(undefined);
                    }
                    firstArgs[optionsIndex] = { timeout: 2000 };
                }

                try {
                    return await original.apply(this, firstArgs);
                } catch (err) {
                    if (!page) return await original.apply(this, args);

                    console.log(`[GHOST] ${action} failed for locator '${selector}'. Requesting AI heal...`);
                    try {
                        const dom = await page.content();
                        const url = await page.url();
                        const result = await consultBrain(selector, action, dom, url);
                        if (result) {
                            const { healed_locator, confidence } = result;
                            writeToReport(selector, healed_locator, action, findCallerFile(), url, confidence);
                            const healedLocator = page.locator(healed_locator);
                            return await healedLocator[method].apply(healedLocator, args);
                        }
                    } catch (brainErr) {
                        console.error('[GHOST] Brain error:', brainErr);
                    }
                    return await original.apply(this, args);
                }
            };
        }
    }
}

function patchPagePrototype(page) {
  if (page.__ghost_patched) return;
  page.__ghost_patched = true;

  const proto = Object.getPrototypeOf(page);
  const actions = { click: 'click', fill: 'fill', hover: 'hover', check: 'check', dblclick: 'click', waitForSelector: 'wait' };

  for (const [method, action] of Object.entries(actions)) {
    if (typeof proto[method] === 'function' && !proto[method].__ghost_patched) {
      const original = proto[method];
      proto[method] = makeHealed(original, action);
      proto[method].__ghost_patched = true;
    }
  }

  const originalLocator = proto.locator;
  if (originalLocator && !proto.locator.__ghost_patched) {
      proto.locator = function(selector, ...args) {
          const loc = originalLocator.apply(this, [selector, ...args]);
          loc.__ghost_selector = selector;
          loc.__ghost_page = this;
          patchLocatorPrototype(loc);
          return loc;
      };
      proto.locator.__ghost_patched = true;
  }

  console.log('[GHOST] Playwright Page & Locator prototypes successfully patched inside worker!');
}

Module._load = function(request, parent, isMain) {
  const exports = originalLoad.apply(this, arguments);

  if (request === 'playwright-core' || request === 'playwright') {
    if (exports && exports.chromium && !exports.__ghost_patched) {
      exports.__ghost_patched = true;
      const originalLaunch = exports.chromium.launch;
      exports.chromium.launch = async function(...args) {
        const browser = await originalLaunch.apply(this, args);
        const originalNewContext = browser.newContext;
        browser.newContext = async function(...cArgs) {
          const context = await originalNewContext.apply(this, cArgs);
          const originalNewPage = context.newPage;
          context.newPage = async function(...pArgs) {
            const page = await originalNewPage.apply(this, pArgs);
            patchPagePrototype(page);
            return page;
          };
          return context;
        };
        const originalNewPageBrowser = browser.newPage;
        browser.newPage = async function(...pArgs) {
          const page = await originalNewPageBrowser.apply(this, pArgs);
          patchPagePrototype(page);
          return page;
        };
        return browser;
      };
    }
  }
  return exports;
};
