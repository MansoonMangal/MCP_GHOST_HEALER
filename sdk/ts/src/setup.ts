/**
 * 👻 Ghost Healer — Playwright TypeScript Global Setup
 */

import { chromium, Page, Locator } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

const BRAIN_URL = process.env['GHOST_BRAIN_URL'] || 'https://ghost-healer-brain.onrender.com';
const CONFIDENCE_THRESHOLD = parseFloat(process.env['GHOST_CONFIDENCE'] || '0.5');
const MAX_RETRIES = parseInt(process.env['GHOST_MAX_RETRIES'] || '3');
const FIRST_ATTEMPT_TIMEOUT = 2000;

// ─────────────────────────────────────────────────────────────
// Stack Parser & Reporter
// ─────────────────────────────────────────────────────────────

function findCallerFile(): { file: string | null; line: number } {
  const err = new Error();
  const stack = err.stack;
  if (!stack) return { file: null, line: 0 };
  const lines = stack.split('\n');
  for (const line of lines) {
    const match = line.match(/\((.*):(\d+):(\d+)\)/) || line.match(/at (.*):(\d+):(\d+)/);
    if (match) {
      const filePath = match[1];
      const lineNo = parseInt(match[2], 10) || 0;
      const isInternal =
        filePath.includes('node_modules') ||
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

function writeToReport(
  oldSelector: string,
  newSelector: string,
  action: string,
  fileInfo: { file: string | null; line: number },
  url: string,
  confidence: number
) {
  const reportDir = path.join(process.cwd(), 'reports', 'ghost');
  fs.mkdirSync(reportDir, { recursive: true });
  const reportFile = path.join(reportDir, 'suggested-fixes.json');
  let data: any[] = [];
  if (fs.existsSync(reportFile)) {
    try {
      data = JSON.parse(fs.readFileSync(reportFile, 'utf8'));
    } catch (e) {}
  }
  data.push({
    timestamp: new Date().toISOString(),
    framework: 'playwright-ts',
    language: 'typescript',
    file: fileInfo.file,
    line: fileInfo.line,
    action: action,
    old_locator: oldSelector,
    suggested_locator: newSelector,
    confidence: confidence,
    page_url: url,
  });
  fs.writeFileSync(reportFile, JSON.stringify(data, null, 2), 'utf8');
}

// ─────────────────────────────────────────────────────────────
// Brain Communication
// ─────────────────────────────────────────────────────────────

async function consultBrain(
  selector: string,
  action: string,
  domSnapshot: string,
  pageUrl: string
): Promise<{ healed_locator: string; confidence: number } | null> {
  for (let attempt = 0; attempt < MAX_RETRIES; attempt++) {
    try {
      const resp = await fetch(`${BRAIN_URL}/api/heal-locator`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          selector,
          action,
          dom_snapshot: domSnapshot,
          page_url: pageUrl,
          framework: 'playwright-ts',
        }),
        signal: AbortSignal.timeout(30000),
      });

      if (!resp.ok) {
        return null;
      }

      const data = (await resp.json()) as any;
      const confidence: number = data.confidence ?? 0;
      const healed: string | null = data.healed_locator ?? null;

      if (healed && confidence >= CONFIDENCE_THRESHOLD) {
        console.log(
          `[GHOST] Healed '${selector}' → '${healed}' ` +
            `(confidence=${(confidence * 100).toFixed(1)}%)`
        );
        return { healed_locator: healed, confidence };
      }
      return null;
    } catch {
      const wait = (attempt + 1) * 5000;
      console.warn(`[GHOST] Brain unreachable. Retrying in ${wait / 1000}s...`);
      await new Promise((r) => setTimeout(r, wait));
    }
  }
  return null;
}

// ─────────────────────────────────────────────────────────────
// Generic Heal Wrapper for Page
// ─────────────────────────────────────────────────────────────

function makeHealedPage(original: Function, action: string): Function {
  return async function (this: any, selector: string, ...args: any[]) {
    const firstArgs = [...args];
    let optionsIndex = 0;
    if (action === 'fill' || action === 'select' || action === 'press') {
      optionsIndex = 1;
    }

    if (firstArgs[optionsIndex] && typeof firstArgs[optionsIndex] === 'object') {
      firstArgs[optionsIndex] = { ...firstArgs[optionsIndex], timeout: FIRST_ATTEMPT_TIMEOUT };
    } else {
      while (firstArgs.length < optionsIndex) {
        firstArgs.push(undefined);
      }
      firstArgs[optionsIndex] = { timeout: FIRST_ATTEMPT_TIMEOUT };
    }

    try {
      return await original.call(this, selector, ...firstArgs);
    } catch {
      const page = this as Page;
      const [dom, url] = await Promise.all([
        page.content(),
        Promise.resolve(page.url()),
      ]);

      const result = await consultBrain(selector, action, dom, url);
      if (result) {
        const { healed_locator, confidence } = result;
        console.log(`[GHOST] Retrying with healed locator: ${healed_locator}`);
        writeToReport(selector, healed_locator, action, findCallerFile(), url, confidence);
        return await original.call(this, healed_locator, ...args);
      }
      return await original.call(this, selector, ...args);
    }
  };
}

// ─────────────────────────────────────────────────────────────
// Generic Heal Wrapper for Locator
// ─────────────────────────────────────────────────────────────

function makeHealedLocator(original: Function, action: string): Function {
  return async function (this: any, ...args: any[]) {
    const firstArgs = [...args];
    let optionsIndex = 0;
    if (original.name === 'fill' || original.name === 'selectOption' || original.name === 'press' || action === 'fill') {
      optionsIndex = 1;
    }

    if (firstArgs[optionsIndex] && typeof firstArgs[optionsIndex] === 'object') {
      firstArgs[optionsIndex] = { ...firstArgs[optionsIndex], timeout: FIRST_ATTEMPT_TIMEOUT };
    } else {
      while (firstArgs.length < optionsIndex) {
        firstArgs.push(undefined);
      }
      firstArgs[optionsIndex] = { timeout: FIRST_ATTEMPT_TIMEOUT };
    }

    try {
      return await original.apply(this, firstArgs);
    } catch {
      const selector = this.__ghost_selector || this.toString();
      const page = this.__ghost_page;
      
      if (!page) {
          return await original.apply(this, args);
      }

      const [dom, url] = await Promise.all([
        page.content(),
        Promise.resolve(page.url()),
      ]);

      const result = await consultBrain(selector, action, dom, url);
      if (result) {
        const { healed_locator, confidence } = result;
        console.log(`[GHOST] Retrying locator with healed selector: ${healed_locator}`);
        writeToReport(selector, healed_locator, action, findCallerFile(), url, confidence);
        
        const healedLocator = page.locator(healed_locator);
        return await (healedLocator as any)[original.name || action].apply(healedLocator, args);
      }
      return await original.apply(this, args);
    }
  };
}

// ─────────────────────────────────────────────────────────────
// Prototype Patching
// ─────────────────────────────────────────────────────────────

async function patchPrototypes(): Promise<void> {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();
  
  // Patch Page
  const pageProto = Object.getPrototypeOf(page) as any;
  const actionsToHeal: Array<[string, string]> = [
    ['click', 'click'],
    ['fill', 'fill'],
    ['hover', 'hover'],
    ['check', 'check'],
    ['uncheck', 'uncheck'],
    ['dblclick', 'click'],
    ['tap', 'click'],
    ['selectOption', 'select'],
    ['press', 'press'],
    ['waitForSelector', 'wait'],
    ['waitFor', 'wait'],
  ];

  for (const [method, action] of actionsToHeal) {
    if (typeof pageProto[method] === 'function' && !pageProto[method].__ghost_patched) {
      const original = pageProto[method];
      pageProto[method] = makeHealedPage(original, action);
      pageProto[method].__ghost_patched = true;
    }
  }

  // Patch page.locator to inject page and selector references
  const originalPageLocator = pageProto.locator;
  if (originalPageLocator && !pageProto.locator.__ghost_patched) {
      pageProto.locator = function(this: any, selector: string, ...args: any[]) {
          const loc = originalPageLocator.call(this, selector, ...args);
          loc.__ghost_page = this;
          loc.__ghost_selector = selector;
          return loc;
      };
      pageProto.locator.__ghost_patched = true;
  }

  // Patch Locator
  const dummyLocator = page.locator('html');
  const locatorProto = Object.getPrototypeOf(dummyLocator) as any;
  
  for (const [method, action] of actionsToHeal) {
      if (typeof locatorProto[method] === 'function' && !locatorProto[method].__ghost_patched) {
          const original = locatorProto[method];
          locatorProto[method] = makeHealedLocator(original, action);
          locatorProto[method].__ghost_patched = true;
      }
  }

  console.log('[GHOST] ✅ Playwright Page & Locator AI self-healing activated.');
  await browser.close();
}

// ─────────────────────────────────────────────────────────────
// Global Setup Entry
// ─────────────────────────────────────────────────────────────

export default async function ghostGlobalSetup(): Promise<void> {
  await patchPrototypes();
}