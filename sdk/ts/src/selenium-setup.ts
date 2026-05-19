/**
 * 👻 Ghost Healer — Selenium JS/TS Global Setup
 *
 * Patches WebDriver.prototype.findElement ONCE so every test
 * in your project gets AI self-healing automatically.
 *
 * MINIMUM CHANGE — add ONE require() to your test setup file:
 *
 *   // jest.setup.js / mocha.opts / wdio.conf.js
 *   require('ghost-healer-ts/selenium-setup');
 *
 * That's it. All driver.findElement() calls in all tests heal automatically.
 */

import { WebDriver, By } from 'selenium-webdriver';
import * as fs from 'fs';
import * as path from 'path';

const BRAIN_URL =
  process.env['GHOST_BRAIN_URL'] || 'https://ghost-healer-brain.onrender.com';
const CONFIDENCE_THRESHOLD = parseFloat(process.env['GHOST_CONFIDENCE'] || '0.5');
const MAX_RETRIES = parseInt(process.env['GHOST_MAX_RETRIES'] || '3');

const SESSION_ID = (function() {
  const now = new Date();
  const pad = (n: number) => String(n).padStart(2, '0');
  return `${now.getFullYear()}${pad(now.getMonth() + 1)}${pad(now.getDate())}_${pad(now.getHours())}${pad(now.getMinutes())}${pad(now.getSeconds())}`;
})();

function findCallerFile(): { file: string | null; line: number } {
  const err = new Error();
  const stack = err.stack;
  if (!stack) return { file: null, line: 0 };
  const lines = stack.split('\n');
  for (const line of lines) {
    const match = line.match(/\((.*):(\d+):(\d+)\)/) || line.match(/at (.*):(\d+):(\d+)/);
    if (match) {
      let filePath = match[1];
      const lineNo = parseInt(match[2], 10) || 0;
      
      // Convert file:/// URIs (ESM style under Node/ts-node) to standard local paths
      if (filePath.startsWith('file:///')) {
        filePath = filePath.substring(8);
      }
      try {
        filePath = decodeURIComponent(filePath);
      } catch (e) {}
      if (filePath.startsWith('/') && filePath.match(/^\/[a-zA-Z]:/)) {
        filePath = filePath.substring(1);
      }

      const isInternal = filePath.includes('node_modules') || 
                        filePath.includes('selenium-setup') || 
                        filePath.includes('pw-hook.js') || 
                        filePath.includes('setup.ts');
      
      if (!isInternal && fs.existsSync(filePath)) {
        return { file: filePath, line: lineNo };
      }
    }
  }
  return { file: null, line: 0 };
}

function applySourceFix(filePath: string, lineNumber: number, oldSelector: string, newSelector: string): boolean {
  if (!filePath || !fs.existsSync(filePath)) return false;
  try {
    const lines = fs.readFileSync(filePath, 'utf8').split('\n');
    let fixed = false, fixedLine = lineNumber;

    let cleanOld = oldSelector;
    let cleanNew = newSelector;
    if (oldSelector.startsWith('#') && newSelector.startsWith('#')) {
      cleanOld = oldSelector.substring(1);
      cleanNew = newSelector.substring(1);
    } else if (oldSelector.startsWith('.') && newSelector.startsWith('.')) {
      cleanOld = oldSelector.substring(1);
      cleanNew = newSelector.substring(1);
    }

    const options = [
      { oldS: oldSelector, newS: newSelector },
      { oldS: cleanOld, newS: cleanNew }
    ];

    // Try extracting from *[id="..."] and *[class="..."]
    const idMatch = oldSelector.match(/^\*\[id="(.+?)"\]$/);
    if (idMatch) {
      const rawId = idMatch[1];
      const healedId = newSelector.startsWith('#') ? newSelector.substring(1) : newSelector;
      options.push({ oldS: rawId, newS: healedId });
    }
    const classMatch = oldSelector.match(/^\*\[class="(.+?)"\]$/);
    if (classMatch) {
      const rawClass = classMatch[1];
      const healedClass = newSelector.startsWith('.') ? newSelector.substring(1) : newSelector;
      options.push({ oldS: rawClass, newS: healedClass });
    }

    for (const opt of options) {
      if (fixed) break;
      const esc = opt.oldS.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      const re  = new RegExp(`(['"])${esc}(['"])`, 'g');

      if (lineNumber > 0 && lineNumber <= lines.length) {
        const orig = lines[lineNumber - 1];
        let upd = orig.replace(re, `$1${opt.newS}$2`);
        if (upd === orig) upd = orig.split(opt.oldS).join(opt.newS);
        if (upd !== orig) { lines[lineNumber - 1] = upd; fixed = true; break; }
      }

      if (!fixed) {
        for (let i = 0; i < lines.length; i++) {
          if (lines[i].includes(opt.oldS)) {
            let upd = lines[i].replace(re, `$1${opt.newS}$2`);
            if (upd === lines[i]) upd = lines[i].split(opt.oldS).join(opt.newS);
            lines[i] = upd; fixedLine = i + 1; fixed = true; break;
          }
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
  } catch (e: any) {
    console.error('[GHOST] SourceHealer error:', e.message);
    return false;
  }
}

function getISTTimestamp(): string {
  const date = new Date();
  const istOffset = 5.5 * 60 * 60 * 1000;
  const istDate = new Date(date.getTime() + istOffset);
  return istDate.toISOString().replace('Z', '+05:30');
}

function findWorkspaceRoot(): string {
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

// Clear server log for selenium session
(function clearServerLog() {
  try {
    const workspaceRoot = findWorkspaceRoot();
    const mcpLogPath = path.join(workspaceRoot, 'reports', 'logs', 'mcp_server.log');
    if (fs.existsSync(mcpLogPath)) {
      fs.writeFileSync(mcpLogPath, '');
      console.log('🧹 [GHOST] Cleared mcp_server.log for new run');
    }
  } catch (e) {}
})();

function writeToReport(oldSelector: string, newSelector: string, action: string, fileInfo: { file: string | null; line: number }, url: string, confidence: number, latencyMs: number = 0) {
  try {
    const reportDir = path.join(findWorkspaceRoot(), 'reports', 'ghost');
    fs.mkdirSync(reportDir, { recursive: true });
    
    // 1. Write to global suggested-fixes.json
    const reportFile = path.join(reportDir, 'suggested-fixes.json');
    let data: any[] = [];
    if (fs.existsSync(reportFile)) {
      try { data = JSON.parse(fs.readFileSync(reportFile, 'utf8')); } catch(e){}
    }
    data.unshift({
      timestamp: getISTTimestamp(),
      framework: "selenium",
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
    console.log(`[GHOST] 📄 Logged suggestion to global report: suggested-fixes.json`);

    // 2. Write to session_<session_id>.json
    const sessionFile = path.join(reportDir, `session_${SESSION_ID}.json`);
    let sessionData: any[] = [];
    if (fs.existsSync(sessionFile)) {
      try { sessionData = JSON.parse(fs.readFileSync(sessionFile, 'utf8')); } catch(e){}
    }
    sessionData.unshift({
      timestamp: getISTTimestamp(),
      session_id: SESSION_ID,
      framework: "selenium-js",
      language: "javascript/typescript",
      file: fileInfo.file,
      line: fileInfo.line,
      action: action,
      old_locator: oldSelector,
      suggested_locator: newSelector,
      confidence: confidence || 0.0,
      page_url: url,
      decision: "AUTO_HEAL",
      latency_ms: Number((latencyMs).toFixed(2)),
      retry_count: 0,
      healing_mode: "runtime"
    });
    fs.writeFileSync(sessionFile, JSON.stringify(sessionData, null, 2), 'utf8');
    console.log(`[GHOST] 📂 Logged session details to audit trail: session_${SESSION_ID}.json`);
  } catch (e: any) {
    console.error(`[GHOST] Failed to write report: ${e.message}`);
  }
}

// ── Brain communication ────────────────────────────────────────────────────────

async function consultBrain(
  selector: string,
  action: string,
  dom: string,
  url: string
): Promise<{ healed_locator: string; confidence: number } | null> {
  console.log(`[GHOST] Consulting brain at ${BRAIN_URL}...`);
  for (let attempt = 0; attempt < MAX_RETRIES; attempt++) {
    try {
      const resp = await fetch(`${BRAIN_URL}/api/heal-locator`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ selector, action, dom_snapshot: dom, page_url: url, framework: "selenium-js" }),
        signal: AbortSignal.timeout(30000),
      });
      if (!resp.ok) {
        console.error(`[GHOST] Brain returned ${resp.status}: ${resp.statusText}`);
        return null;
      }
      const data = (await resp.json()) as any;
      console.log(`[GHOST] Brain response: ${JSON.stringify(data)}`);
      if (data.healed_locator && data.confidence >= CONFIDENCE_THRESHOLD) {
        console.log(`[GHOST] Healed '${selector}' → '${data.healed_locator}' (${(data.confidence * 100).toFixed(1)}%)`);
        return { healed_locator: data.healed_locator as string, confidence: data.confidence as number };
      }
      console.log(`[GHOST] Brain rejected heal. Confidence: ${data.confidence}, Threshold: ${CONFIDENCE_THRESHOLD}`);
      return null;
    } catch (e: any) {
      console.error(`[GHOST] Brain request failed (attempt ${attempt + 1}): ${e.message}`);
      await new Promise((r) => setTimeout(r, (attempt + 1) * 2000));
    }
  }
  return null;
}

// ── Locator → CSS string ──────────────────────────────────────────────────────

function locatorToString(locator: any): string {
  if (typeof locator === 'string') return locator;
  // selenium-webdriver By object
  if (locator && locator.using && locator.value) {
    const map: Record<string, string> = {
      id: '#',
      'class name': '.',
      'css selector': '',
      name: '[name="',
    };
    if (locator.using === 'id') return `#${locator.value}`;
    if (locator.using === 'class name') return `.${locator.value}`;
    if (locator.using === 'name') return `[name="${locator.value}"]`;
    if (locator.using === 'css selector') return locator.value;
    if (locator.using === 'xpath') return locator.value;
    if (locator.using === 'link text') return `text=${locator.value}`;
    return locator.value;
  }
  return String(locator);
}

// ── WebDriver.prototype patching ──────────────────────────────────────────────

const proto = WebDriver.prototype as any;

const _originalFindElement = proto.findElement.bind
  ? proto.findElement
  : proto.findElement;

const _originalFindElements = proto.findElements;

proto.findElement = async function (locator: any) {
  try {
    return await _originalFindElement.call(this, locator);
  } catch (originalError) {
    const selector = locatorToString(locator);
    console.log(`[GHOST] findElement failed for '${selector}'. Consulting AI Brain...`);

    try {
      const dom: string = await this.getPageSource();
      const url: string = await this.getCurrentUrl();
      const startTime = Date.now();
      const result = await consultBrain(selector, 'find', dom, url);
      if (result) {
        const latencyMs = Date.now() - startTime;
        const caller = findCallerFile();
        console.log(`[GHOST] [DEBUG] findCallerFile returned: file=${caller.file}, line=${caller.line}`);
        if (caller.file) {
          applySourceFix(caller.file, caller.line, selector, result.healed_locator);
        } else {
          console.log(`[GHOST] [DEBUG] Caller stack: ${new Error().stack}`);
        }
        writeToReport(selector, result.healed_locator, 'click', caller, url, result.confidence, latencyMs);
        return await _originalFindElement.call(this, By.css(result.healed_locator));
      }
    } catch (brainError) {
      console.error(`[GHOST] Brain error: ${brainError}`);
    }

    throw originalError;
  }
};

proto.findElements = async function (locator: any) {
  try {
    const elements = await _originalFindElements.call(this, locator);
    if (elements && elements.length > 0) return elements;
    throw new Error('No elements found');
  } catch (originalError) {
    const selector = locatorToString(locator);
    console.log(`[GHOST] findElements failed for '${selector}'. Consulting AI Brain...`);
    try {
      const dom: string = await this.getPageSource();
      const url: string = await this.getCurrentUrl();
      const startTime = Date.now();
      const result = await consultBrain(selector, 'find', dom, url);
      if (result) {
        const latencyMs = Date.now() - startTime;
        const caller = findCallerFile();
        if (caller.file) {
          applySourceFix(caller.file, caller.line, selector, result.healed_locator);
        }
        writeToReport(selector, result.healed_locator, 'click', caller, url, result.confidence, latencyMs);
        return await _originalFindElements.call(this, By.css(result.healed_locator));
      }
    } catch { /* ignore */ }
    throw originalError;
  }
};

console.log('[GHOST] ✅ WebDriver.prototype patched — Selenium JS/TS self-healing active.');

export {};
