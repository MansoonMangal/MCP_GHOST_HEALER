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

let isPatched = false;

// ── Source Healer ──────────────────────────────────────────────────────────
function findCallerFile() {
  const err = new Error();
  const stack = err.stack;
  if (!stack) return null;
  const lines = stack.split('\n');
  for (const line of lines) {
    const match = line.match(/\((.*):(\d+):(\d+)\)/) || line.match(/at (.*):(\d+):(\d+)/);
    if (match) {
      const filePath = match[1];
      const isInternal = filePath.includes('node_modules') || 
                        filePath.includes('pw-hook.js') || 
                        filePath.includes('setup.ts') ||
                        filePath.includes('GhostLocator');
      
      if (!isInternal && fs.existsSync(filePath)) {
        return filePath;
      }
    }
  }
  return null;
}

function applySourcePatch(oldSelector, newSelector) {
  const file = findCallerFile();
  if (!file) return;
  try {
    const content = fs.readFileSync(file, 'utf8');
    const escapedOld = oldSelector.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const pattern = new RegExp(`(['"\`])${escapedOld}(['"\`])`, 'g');
    if (pattern.test(content)) {
      const newContent = content.replace(pattern, `$1${newSelector}$2`);
      fs.writeFileSync(file, newContent, 'utf8');
      console.log(`[GHOST] ✅ Permanently patched: ${path.basename(file)} ('${oldSelector}' -> '${newSelector}')`);
    }
  } catch (e) {}
}

async function consultBrain(selector, action, domSnapshot, pageUrl) {
  for (let attempt = 0; attempt < 3; attempt++) {
    try {
      const resp = await fetch(`${BRAIN_URL}/api/heal-locator`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ selector, action, dom_snapshot: domSnapshot, page_url: pageUrl }),
        signal: AbortSignal.timeout(30000),
      });
      if (!resp.ok) return null;
      const data = await resp.json();
      if (data.healed_locator && data.confidence >= CONFIDENCE_THRESHOLD) {
        console.log(`\n[GHOST] Healed '${selector}' → '${data.healed_locator}' (${(data.confidence * 100).toFixed(1)}%)`);
        return data.healed_locator;
      }
      return null;
    } catch {
      await new Promise(r => setTimeout(r, (attempt + 1) * 3000));
    }
  }
  return null;
}

function makeHealed(original, action) {
  return async function(selector, ...args) {
    const firstArgs = [...args];
    if (firstArgs[0] && typeof firstArgs[0] === 'object') {
      firstArgs[0] = { ...firstArgs[0], timeout: 2000 };
    } else {
      firstArgs.unshift({ timeout: 2000 });
    }

    try {
      return await original.apply(this, [selector, ...firstArgs]);
    } catch (err) {
      console.log(`[GHOST] ${action} failed for '${selector}'. Requesting AI heal...`);
      try {
        const dom = await this.content();
        const url = await this.url();
        const healed = await consultBrain(selector, action, dom, url);
        if (healed) {
          if (config.healing.auto_patch) {
            applySourcePatch(selector, healed);
          }
          return await original.apply(this, [healed, ...args]);
        }
      } catch (brainErr) {
        console.error('[GHOST] Brain error:', brainErr);
      }
      return await original.apply(this, [selector, ...args]);
    }
  };
}

function patchPagePrototype(page) {
  if (isPatched) return;
  const proto = Object.getPrototypeOf(page);
  const actions = { click: 'click', fill: 'fill', hover: 'hover', check: 'check', dblclick: 'click' };

  for (const [method, action] of Object.entries(actions)) {
    if (typeof proto[method] === 'function') {
      const original = proto[method];
      proto[method] = makeHealed(original, action);
    }
  }
  isPatched = true;
  console.log('[GHOST] Playwright Page prototype successfully patched inside worker!');
}

Module._load = function(request, parent, isMain) {
  const exports = originalLoad.apply(this, arguments);

  // Intercept playwright-core to wrap browser creation
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
