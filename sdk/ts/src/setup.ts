/**
 * 👻 Ghost Healer — Playwright TypeScript Global Setup
 *
 * Patches Playwright's Page.prototype ONCE at startup.
 * Every test in your project gets AI self-healing automatically.
 *
 * HOW TO USE (ONE LINE change in playwright.config.ts):
 *
 *   import { defineConfig } from '@playwright/test';
 *   export default defineConfig({
 *     globalSetup: require.resolve('ghost-healer-ts/setup'),  // ← ADD THIS
 *   });
 *
 * That's it. Your test files stay EXACTLY the same:
 *   await page.click('#broken-selector');  // auto-healed by Ghost
 */

import { Page } from 'playwright';

const BRAIN_URL =
  process.env['GHOST_BRAIN_URL'] || 'https://ghost-healer-brain.onrender.com';
const CONFIDENCE_THRESHOLD = parseFloat(process.env['GHOST_CONFIDENCE'] || '0.5');
const MAX_RETRIES = parseInt(process.env['GHOST_MAX_RETRIES'] || '3');
const FIRST_ATTEMPT_TIMEOUT = 2000;

// ── Brain communication ────────────────────────────────────────────────────────

async function consultBrain(
  selector: string,
  action: string,
  domSnapshot: string,
  pageUrl: string
): Promise<string | null> {
  for (let attempt = 0; attempt < MAX_RETRIES; attempt++) {
    try {
      const resp = await fetch(`${BRAIN_URL}/api/heal-locator`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          selector,
          action,
          dom_snapshot: domSnapshot,
          page_url: pageUrl,
        }),
        signal: AbortSignal.timeout(30000),
      });

      if (!resp.ok) return null;

      const data = (await resp.json()) as any;
      const confidence: number = data.confidence ?? 0;
      const healed: string | null = data.healed_locator ?? null;

      if (healed && confidence >= CONFIDENCE_THRESHOLD) {
        console.log(
          `[GHOST] Healed '${selector}' → '${healed}' ` +
          `(confidence=${(confidence * 100).toFixed(1)}%, action=${action})`
        );
        return healed;
      }
      return null;
    } catch {
      const wait = (attempt + 1) * 5000;
      console.warn(`[GHOST] Brain unreachable, retrying in ${wait / 1000}s...`);
      await new Promise((r) => setTimeout(r, wait));
    }
  }
  return null;
}

import { sourceHealer } from './SourceHealer';

// ... (keep consultBrain as is) ...

// ── Generic heal-and-retry wrapper ───────────────────────────────────────────

function makeHealed(
  original: Function,
  action: string,
  pageGetter: () => Page
): Function {
  return async function (this: any, selector: string, ...args: any[]) {
    // Inject short timeout on first attempt to fail fast
    const firstArgs = [...args];
    if (firstArgs[0] && typeof firstArgs[0] === 'object') {
      firstArgs[0] = { ...firstArgs[0], timeout: FIRST_ATTEMPT_TIMEOUT };
    } else {
      firstArgs.unshift({ timeout: FIRST_ATTEMPT_TIMEOUT });
    }

    try {
      return await original.call(this, selector, ...firstArgs);
    } catch {
      const page = pageGetter();
      const [dom, url] = await Promise.all([page.content(), Promise.resolve(page.url())]);
      const healed = await consultBrain(selector, action, dom, url);
      if (healed) {
        // PERMANENT PATCH: fix the source file
        sourceHealer.applyFix(selector, healed);
        return await original.call(this, healed, ...args);
      }
      // Re-run with original timeout to get the proper error message
      return await original.call(this, selector, ...args);
    }
  };
}

// ── Page.prototype patching ───────────────────────────────────────────────────

function patchPagePrototype(): void {
  const proto = Page.prototype as any;

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
  ];

  for (const [method, action] of actionsToHeal) {
    if (typeof proto[method] === 'function') {
      const original = proto[method];
      proto[method] = makeHealed(original, action, function (this: Page) {
        return this;
      });
    }
  }

  console.log('[GHOST] ✅ Page.prototype patched — AI self-healing active for all tests.');
}

// ── Global setup entry point ──────────────────────────────────────────────────

export default async function ghostGlobalSetup(): Promise<void> {
  patchPagePrototype();
}
