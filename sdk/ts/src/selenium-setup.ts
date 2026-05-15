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

const BRAIN_URL =
  process.env['GHOST_BRAIN_URL'] || 'https://ghost-healer-brain.onrender.com';
const CONFIDENCE_THRESHOLD = parseFloat(process.env['GHOST_CONFIDENCE'] || '0.5');
const MAX_RETRIES = parseInt(process.env['GHOST_MAX_RETRIES'] || '3');

// ── Brain communication ────────────────────────────────────────────────────────

async function consultBrain(
  selector: string,
  action: string,
  dom: string,
  url: string
): Promise<string | null> {
  for (let attempt = 0; attempt < MAX_RETRIES; attempt++) {
    try {
      const resp = await fetch(`${BRAIN_URL}/api/heal-locator`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ selector, action, dom_snapshot: dom, page_url: url }),
        signal: AbortSignal.timeout(30000),
      });
      if (!resp.ok) return null;
      const data = (await resp.json()) as any;
      if (data.healed_locator && data.confidence >= CONFIDENCE_THRESHOLD) {
        console.log(`[GHOST] Healed '${selector}' → '${data.healed_locator}' (${(data.confidence * 100).toFixed(1)}%)`);
        return data.healed_locator as string;
      }
      return null;
    } catch {
      await new Promise((r) => setTimeout(r, (attempt + 1) * 5000));
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
      const healed = await consultBrain(selector, 'click', dom, url);
      if (healed) {
        return await _originalFindElement.call(this, By.css(healed));
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
    try {
      const dom: string = await this.getPageSource();
      const url: string = await this.getCurrentUrl();
      const healed = await consultBrain(selector, 'click', dom, url);
      if (healed) {
        return await _originalFindElements.call(this, By.css(healed));
      }
    } catch { /* ignore */ }
    throw originalError;
  }
};

console.log('[GHOST] ✅ WebDriver.prototype patched — Selenium JS/TS self-healing active.');

export {};
