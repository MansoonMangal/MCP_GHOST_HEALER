/**
 * 👻 Ghost Healer — pw-hook.js
 *
 * ARCHITECTURE: "Deferred Parallel Healing"
 *
 * When a locator fails:
 *   1. Screenshot + DOM captured instantly (~100-300ms)
 *   2. Brain request fired in BACKGROUND (non-blocking)
 *   3. Failure queued to disk  → reports/ghost/.ghost_queue/
 *   4. Original error re-thrown → Playwright marks step as failed and moves on
 *   5. Rest of test suite continues WITHOUT any delay
 *
 * After ALL tests finish (globalTeardown):
 *   6. All brain results collected from disk
 *   7. SourceHealer patches source files locally
 *   8. Full reports + summary banner printed
 *
 * How to activate (in playwright.config.ts):
 *   require('ghost-healer-ts/pw-hook.js');
 *
 * Natural Playwright timeouts are PRESERVED — no 2s forced intercept.
 */

'use strict';

const Module = require('module');
const fs     = require('fs');
const path   = require('path');
const yaml   = require('js-yaml');
const { loadProjectEnv } = require('./projectEnv');
const originalLoad = Module._load;

loadProjectEnv();

// ── Configuration ────────────────────────────────────────────────────────────

let config = {
  mcp_server: { url: 'https://ghost-healer-brain.onrender.com', confidence_threshold: 0.5 },
  healing: { auto_patch: true },
};

try {
  const ghostYamlPath =
    process.env.GHOST_CONFIG ||
    path.join(process.cwd(), 'ghost.yaml') ||
    path.join(process.cwd(), '../../ghost.yaml');
  const candidates = [
    process.env.GHOST_CONFIG,
    path.join(process.cwd(), 'ghost.yaml'),
    path.join(process.cwd(), '../../ghost.yaml'),
  ].filter(Boolean);
  for (const p of candidates) {
    if (p && fs.existsSync(p)) {
      const loaded = yaml.load(fs.readFileSync(p, 'utf8'));
      if (loaded) { config = { ...config, ...loaded }; break; }
    }
  }
} catch (_) {}

const BRAIN_URL            = process.env.GHOST_BRAIN_URL || config.mcp_server.url;
const CONFIDENCE_THRESHOLD = parseFloat(String(config.mcp_server.confidence_threshold)) || 0.5;
const AUTO_PATCH           = config.healing.auto_patch !== false;

const SESSION_ID = (() => {
  const d = new Date();
  const p = (n) => String(n).padStart(2, '0');
  return `${d.getFullYear()}${p(d.getMonth()+1)}${p(d.getDate())}_${p(d.getHours())}${p(d.getMinutes())}${p(d.getSeconds())}`;
})();

// ── Per-worker in-flight brain promises ──────────────────────────────────────

/** @type {Promise<void>[]} */
const _pendingBrainRequests = [];

// ── Helpers ──────────────────────────────────────────────────────────────────

function genId() {
  return `${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 7)}`;
}

function safeSelector(selector) {
  return String(selector).replace(/[^a-zA-Z0-9_-]/g, '_').slice(0, 40);
}

function getISTTimestamp() {
  const d = new Date();
  return new Date(d.getTime() + 5.5 * 3600000).toISOString().replace('Z', '+05:30');
}

function findWorkspaceRoot() {
  let dir = process.cwd();
  for (let i = 0; i < 20; i++) {
    if (fs.existsSync(path.join(dir, 'ghost.yaml')) || fs.existsSync(path.join(dir, '.git'))) {
      return dir;
    }
    const parent = path.dirname(dir);
    if (parent === dir) break;
    dir = parent;
  }
  return path.resolve(__dirname, '../../..');
}

function findCallerFile() {
  const stack = (new Error()).stack || '';
  for (const line of stack.split('\n')) {
    const m = line.match(/\((.*):(\d+):\d+\)/) || line.match(/at (.*):(\d+):\d+/);
    if (!m) continue;
    let fp = m[1];
    const ln = parseInt(m[2], 10) || 0;

    // Convert file:/// URIs (ESM style under Node/ts-node) to standard local paths
    if (fp.startsWith('file:///')) {
      fp = fp.substring(8);
    }
    try {
      fp = decodeURIComponent(fp);
    } catch (e) {}
    if (fp.startsWith('/') && fp.match(/^\/[a-zA-Z]:/)) {
      fp = fp.substring(1);
    }

    const isInternal =
      fp.includes('node_modules') ||
      fp.includes('pw-hook') ||
      fp.includes('setup.ts') ||
      fp.includes('setup.js') ||
      fp.includes('GhostLocator');
    if (!isInternal && fs.existsSync(fp)) return { file: fp, line: ln };
  }
  return { file: null, line: 0 };
}

function getQueueDir() {
  return path.join(findWorkspaceRoot(), 'reports', 'ghost', '.ghost_queue');
}

// ── Source Healer (inline JS — no TS compilation needed at runtime) ──────────

function applySourceFix(filePath, lineNumber, oldSelector, newSelector) {
  if (!filePath || !fs.existsSync(filePath)) return false;
  try {
    const lines = fs.readFileSync(filePath, 'utf8').split('\n');
    const esc   = oldSelector.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const re    = new RegExp(`(['"])${esc}(['"])`, 'g');
    let fixed = false, fixedLine = lineNumber;

    if (lineNumber > 0 && lineNumber <= lines.length) {
      const orig = lines[lineNumber - 1];
      let upd = orig.replace(re, `$1${newSelector}$2`);
      if (upd === orig) upd = orig.split(oldSelector).join(newSelector);
      if (upd !== orig) { lines[lineNumber - 1] = upd; fixed = true; }
    }

    if (!fixed) {
      for (let i = 0; i < lines.length; i++) {
        if (lines[i].includes(oldSelector)) {
          let upd = lines[i].replace(re, `$1${newSelector}$2`);
          if (upd === lines[i]) upd = lines[i].split(oldSelector).join(newSelector);
          lines[i] = upd; fixedLine = i + 1; fixed = true; break;
        }
      }
    }

    if (fixed) {
      fs.writeFileSync(filePath, lines.join('\n'), 'utf8');
      const rel = path.relative(process.cwd(), filePath);
      console.log(`[GHOST] 📝 SourceHealer patching: ${rel}:${fixedLine}`);
      console.log(`         OLD → '${oldSelector}'`);
      console.log(`         NEW → '${newSelector}'`);
      console.log(`[GHOST] ✅ Source permanently fixed.\n`);
    }
    return fixed;
  } catch (e) {
    console.error('[GHOST] SourceHealer error:', e.message);
    return false;
  }
}

// ── Core: Failure Handler ─────────────────────────────────────────────────────
//
// Called from every intercepted catch block.
// page        — Playwright Page object (for screenshot + content)
// selector    — the broken selector string
// action      — 'click', 'fill', etc.

async function handleFailure(page, selector, action, locator = null) {
  const uuid       = genId();
  let callerInfo   = null;
  if (locator && locator.__ghost_creation_caller) {
    callerInfo = locator.__ghost_creation_caller;
  } else {
    callerInfo = findCallerFile();
  }
  const url        = page.url();
  const wsRoot     = findWorkspaceRoot();
  const queueDir   = getQueueDir();
  const ssDir      = path.join(wsRoot, 'reports', 'ghost', 'screenshots');
  const htmlDir    = path.join(wsRoot, 'reports', 'ghost', 'html');

  fs.mkdirSync(queueDir, { recursive: true });
  fs.mkdirSync(ssDir,    { recursive: true });
  fs.mkdirSync(htmlDir,  { recursive: true });

  let screenshotPath = '';
  let htmlPath = '';
  
  try {
    const ssFile = path.join(ssDir, `${SESSION_ID}_${safeSelector(selector)}_${uuid}.png`);
    htmlPath = path.join(htmlDir, `${SESSION_ID}_${uuid}.html`);
    
    const [rawDom] = await Promise.all([
      page.content(),
      page.screenshot({ path: ssFile, fullPage: true }),
    ]);
    
    screenshotPath = ssFile;
    console.log(`[GHOST] 📸 Diagnostics captured.`);

    // Save HTML snapshot for the brain to use during teardown
    fs.writeFileSync(htmlPath, rawDom, 'utf8');
  } catch (diagErr) {
    console.warn(`[GHOST] ⚠️  Could not capture diagnostics: ${diagErr.message}`);
  }

  // Write failure entry to disk immediately
  const failureFile = path.join(queueDir, `failure_${uuid}.json`);
  fs.writeFileSync(failureFile, JSON.stringify({
    uuid, selector, action, url,
    file: callerInfo.file,
    line: callerInfo.line,
    timestamp: getISTTimestamp(),
    session_id: SESSION_ID,
    screenshot_path: screenshotPath,
    html_path: htmlPath,
  }), 'utf8');

  console.log(`[GHOST] 🔄 Queued for AI healing — brain contacted in background...`);
  console.log(`[GHOST] ⏳ Healing will be applied after the test suite finishes.\n`);
}

// ── Playwright Prototype Patcher ──────────────────────────────────────────────

function patchLocatorProto(locator) {
  const proto = Object.getPrototypeOf(locator);
  if (proto.__ghost_patched) return;
  proto.__ghost_patched = true;

  const methods = {
    click: 'click', fill: 'fill', hover: 'hover',
    check: 'check', uncheck: 'uncheck', dblclick: 'click',
    tap: 'click', selectOption: 'select', press: 'press',
    waitFor: 'wait',
  };

  for (const [method, action] of Object.entries(methods)) {
    if (typeof proto[method] !== 'function') continue;
    const original = proto[method];
    proto[method] = async function (...args) {
      try {
        return await original.apply(this, args);
      } catch (err) {
        const selector = this.__ghost_selector || String(this);
        const page     = this.__ghost_page;
        console.log(`\n[GHOST] ❌ Locator failure! '${selector}' → action '${action}' failed.`);
        if (page) await handleFailure(page, selector, action, this);
        throw err; // ← re-throw so Playwright marks test step as failed
      }
    };
  }

  const subMethods = ['locator', 'first', 'last', 'nth', 'filter'];
  for (const method of subMethods) {
    if (typeof proto[method] !== 'function' || proto[method].__ghost_sub_patched) continue;
    const original = proto[method];
    proto[method] = function (...args) {
      const loc = original.apply(this, args);
      if (loc && typeof loc === 'object') {
        loc.__ghost_page = this.__ghost_page;
        loc.__ghost_selector = this.__ghost_selector || String(this);
        loc.__ghost_creation_caller = this.__ghost_creation_caller;
        patchLocatorProto(loc);
      }
      return loc;
    };
    proto[method].__ghost_sub_patched = true;
  }
}

function patchPageProto(page) {
  if (page.__ghost_patched) return;
  page.__ghost_patched = true;

  const proto = Object.getPrototypeOf(page);

  // Patch direct page actions
  const methods = {
    click: 'click', fill: 'fill', hover: 'hover',
    check: 'check', uncheck: 'uncheck', dblclick: 'click',
    selectOption: 'select', press: 'press', waitForSelector: 'wait',
  };

  for (const [method, action] of Object.entries(methods)) {
    if (typeof proto[method] !== 'function' || proto[method].__ghost_patched) continue;
    const original = proto[method];
    proto[method] = async function (selector, ...args) {
      try {
        return await original.call(this, selector, ...args);
      } catch (err) {
        console.log(`\n[GHOST] ❌ Page.${method} failure! Selector '${selector}' failed.`);
        await handleFailure(this, selector, action);
        throw err;
      }
    };
    proto[method].__ghost_patched = true;
  }

  // Patch page.locator to attach page/selector metadata
  if (typeof proto.locator === 'function' && !proto.locator.__ghost_patched) {
    const origLocator = proto.locator;
    proto.locator = function (selector, ...args) {
      const loc = origLocator.call(this, selector, ...args);
      loc.__ghost_page     = this;
      loc.__ghost_selector = selector;
      loc.__ghost_creation_caller = findCallerFile();
      patchLocatorProto(loc);
      return loc;
    };
    proto.locator.__ghost_patched = true;
  }

  console.log('[GHOST] ✅ Playwright Page & Locator self-healing activated (deferred-parallel mode).');
}

// ── Module._load Intercept ────────────────────────────────────────────────────

Module._load = function (request, parent, isMain) {
  const exports = originalLoad.apply(this, arguments);

  if ((request === 'playwright-core' || request === 'playwright' || request === '@playwright/test') && exports) {
    if (exports.chromium && !exports.__ghost_patched) {
      exports.__ghost_patched = true;

      const origLaunch = exports.chromium.launch;
      exports.chromium.launch = async function (...args) {
        const browser = await origLaunch.apply(this, args);

        const origNewContext = browser.newContext;
        browser.newContext = async function (...cArgs) {
          const ctx = await origNewContext.apply(this, cArgs);
          const origNewPage = ctx.newPage;
          ctx.newPage = async function (...pArgs) {
            const page = await origNewPage.apply(this, pArgs);
            patchPageProto(page);
            return page;
          };
          return ctx;
        };

        const origBrowserNewPage = browser.newPage;
        browser.newPage = async function (...pArgs) {
          const page = await origBrowserNewPage.apply(this, pArgs);
          patchPageProto(page);
          return page;
        };

        return browser;
      };
    }

    if (exports.expect && typeof exports.expect === 'function' && !exports.expect.__ghost_patched) {
      const originalExpect = exports.expect;

      function wrapExpect(expectFn) {
        const newExpect = function (actual, ...args) {
          const matchers = expectFn(actual, ...args);
          if (actual && actual.__ghost_page && actual.__ghost_selector) {
            const page = actual.__ghost_page;
            const selector = actual.__ghost_selector;

            for (const key of Object.keys(matchers)) {
              if (typeof matchers[key] === 'function' && !matchers[key].__ghost_patched) {
                const originalMatcher = matchers[key];
                matchers[key] = async function (...matcherArgs) {
                  try {
                    return await originalMatcher.apply(this, matcherArgs);
                  } catch (err) {
                    console.log(`\n[GHOST] ❌ Assertion failure! '${selector}' → expect(locator).${key}() failed.`);
                    if (page) {
                      await handleFailure(page, selector, 'wait', actual);
                    }
                    throw err;
                  }
                };
                matchers[key].__ghost_patched = true;
              }
            }
          }
          return matchers;
        };
        Object.assign(newExpect, expectFn);
        return newExpect;
      }

      const newExpect = wrapExpect(originalExpect);
      if (typeof originalExpect.soft === 'function') {
        newExpect.soft = wrapExpect(originalExpect.soft);
      }
      exports.expect = newExpect;
      exports.expect.__ghost_patched = true;
    }
  }

  return exports;
};
