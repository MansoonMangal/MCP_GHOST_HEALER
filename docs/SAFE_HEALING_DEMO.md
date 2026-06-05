# Safe Healing Demo Guide

Ghost can work mechanically while the Brain suggests **wrong** locators (headers, ad iframes, `#quantity` on another page). That causes **cascading bad patches** if you keep re-running on corrupted page objects.

---

## What went wrong (example)

| Run | Failed locator | Brain "fix" | Reality |
|-----|----------------|-------------|---------|
| 1 | `[data-qa="name-on-card"]` | `div.header-middle` | Site header — not an input |
| 2 | `div.header-middle` | `#name` | Wrong context |
| 3 | `[data-qa="card-number"]` | `#quantity` | Product quantity field |
| 4+ | cvc, expiry | `#quantity` again | Same wrong element |

**Root causes:**
- Full-page DOM snapshot includes ads, headers, wrong-page content during navigation
- High confidence on visible but **wrong** elements
- Multiple broken fields patched in one suite → corruption compounds
- False success when old === new locator or fill targets non-inputs

---

## Safe demo rules

### 1. Break **one** locator at a time

```typescript
// Good demo typo:
'[data-qa="name-on-cardd"]'   // single typo

// Bad demo:
'[data-qa="wrong-attribute"]'   // on payment page with 5 broken fields
```

### 2. Revert after a bad heal

Do **not** keep re-running on corrupted `PaymentPage.ts`. Restore `data-qa` locators from git, then retry.

### 3. Raise confidence threshold

`ghost.yaml`:

```yaml
mcp_server:
  confidence_threshold: 0.95
```

### 4. Reliable demo scenario

Break checkout address only:

```text
#address_delivery  →  #address  (one field)
Run 1: fails
Run 2: Brain patches back to #address_delivery
```

Avoid multi-field payment page healing until Brain context improves.

### 5. Fix timing before blaming locators

Payment page uses real `data-qa` attributes. Initial failures may be **actionTimeout** or navigation — not wrong selectors. Consider:

```typescript
// playwright.config.ts
actionTimeout: 15000,
```

---

## SDK guards (v1.2.3+)

| Guard | Behavior |
|-------|----------|
| Identical locator | Skip patch when `old === new` |
| Fill actions | Reject heals targeting `div`, `header`, non-input tags |
| DOM snapshot | Wait for `domcontentloaded` before capture |
| Action passed to Brain | `failure.action` (`fill`, `click`, …) in heal request |

---

## After bad run — restore locators

```bash
git checkout -- pages/PaymentPage.ts pages/CheckoutPage.ts
npm install ghost-healer-ts-sdk@1.2.3
npx ghost-playwright test
```

---

## When healing is appropriate

| Scenario | Heal? |
|----------|-------|
| Single typo in stable `data-qa` | ✅ Yes |
| UI redesign, same semantic field | ✅ Yes (one field) |
| Timeout / navigation flake | ❌ Fix timing first |
| 5+ fields broken at once | ❌ Restore files first |
| Ad iframe / header in snapshot | ❌ Brain will suggest junk |
