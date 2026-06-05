'use strict';

/** Client-side guards — reject no-op or action-incompatible heals before patching. */

const FILL_ACTIONS = new Set(['fill', 'type', 'press_sequentially', 'inputvalue', 'selectoption']);

function normalizeLocator(locator) {
  return String(locator || '').trim().replace(/\s+/g, ' ');
}

function isSameLocator(oldLocator, newLocator) {
  return normalizeLocator(oldLocator) === normalizeLocator(newLocator);
}

function elementTagForLocator(locator, domSnapshot) {
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
  /^div\./i, /^div$/i, /^header/i, /^nav/i, /^footer/i, /^span\./i, /^aswift/i, /iframe/i,
];

function validateHealProposal(oldLocator, newLocator, action, domSnapshot) {
  if (!newLocator || !String(newLocator).trim()) {
    return { ok: false, reason: 'empty healed locator' };
  }
  if (isSameLocator(oldLocator, newLocator)) {
    return { ok: false, reason: `healed locator identical to broken locator ('${newLocator}') — skipping patch` };
  }

  const act = String(action || 'click').toLowerCase();

  for (const pat of NON_INPUT_TAG_PATTERNS) {
    if (pat.test(newLocator.trim()) && FILL_ACTIONS.has(act)) {
      return { ok: false, reason: `fill action cannot target '${newLocator}'` };
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

  return { ok: true };
}

module.exports = {
  FILL_ACTIONS,
  normalizeLocator,
  isSameLocator,
  elementTagForLocator,
  validateHealProposal,
};
