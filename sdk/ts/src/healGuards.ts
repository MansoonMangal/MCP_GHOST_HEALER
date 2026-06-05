/**
 * Client-side guards — reject no-op or action-incompatible heals before patching.
 */

export const FILL_ACTIONS = new Set(['fill', 'type', 'press_sequentially', 'inputvalue', 'selectoption']);
export const CLICK_ACTIONS = new Set(['click', 'dblclick', 'tap', 'check', 'uncheck', 'press', 'select']);

export function normalizeLocator(locator: string): string {
  return String(locator || '').trim().replace(/\s+/g, ' ');
}

export function isSameLocator(oldLocator: string, newLocator: string): boolean {
  return normalizeLocator(oldLocator) === normalizeLocator(newLocator);
}

/** Infer HTML tag for a simple CSS locator from a DOM snapshot (structural check). */
export function elementTagForLocator(locator: string, domSnapshot: string): string | null {
  if (!locator || !domSnapshot) return null;
  const loc = locator.trim();

  const idMatch = loc.match(/^#([\w-]+)$/);
  if (idMatch) {
    const re = new RegExp(`<([a-z][a-z0-9]*)[^>]*\\bid=["']${idMatch[1]}["']`, 'i');
    const m = domSnapshot.match(re);
    if (m) return m[1].toLowerCase();
  }

  const attrMatch = loc.match(/^\[([^\]=]+)=["']([^"']+)["']\]$/);
  if (attrMatch) {
    const attr = attrMatch[1];
    const val = attrMatch[2].replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const re = new RegExp(`<([a-z][a-z0-9]*)[^>]*\\b${attr}=["']${val}["']`, 'i');
    const m = domSnapshot.match(re);
    if (m) return m[1].toLowerCase();
  }

  const tagOnly = loc.match(/^([a-z][a-z0-9]*)$/i);
  if (tagOnly) return tagOnly[1].toLowerCase();

  return null;
}

const NON_INPUT_TAG_PATTERNS = [
  /^div\./i,
  /^div$/i,
  /^header/i,
  /^nav/i,
  /^footer/i,
  /^span\./i,
  /^aswift/i,
  /iframe/i,
];

export function validateHealProposal(
  oldLocator: string,
  newLocator: string,
  action: string,
  domSnapshot?: string
): { ok: boolean; reason?: string } {
  if (!newLocator || !String(newLocator).trim()) {
    return { ok: false, reason: 'empty healed locator' };
  }

  if (isSameLocator(oldLocator, newLocator)) {
    return {
      ok: false,
      reason: `healed locator identical to broken locator ('${newLocator}') — skipping patch`,
    };
  }

  const act = String(action || 'click').toLowerCase();

  for (const pat of NON_INPUT_TAG_PATTERNS) {
    if (pat.test(newLocator.trim())) {
      if (FILL_ACTIONS.has(act)) {
        return { ok: false, reason: `fill action cannot target '${newLocator}'` };
      }
    }
  }

  if (FILL_ACTIONS.has(act) && domSnapshot) {
    const tag = elementTagForLocator(newLocator, domSnapshot);
    if (tag && !['input', 'textarea', 'select'].includes(tag)) {
      return {
        ok: false,
        reason: `fill action requires input/textarea/select — '${newLocator}' resolves to <${tag}>`,
      };
    }
  }

  if (FILL_ACTIONS.has(act) && !domSnapshot) {
    if (/^#(quantity|subscribe|aswift)/i.test(newLocator) || /^div[.\[]/i.test(newLocator)) {
      return { ok: false, reason: `fill action rejected suspicious selector '${newLocator}'` };
    }
  }

  return { ok: true };
}
