# 🟦 Ghost Healer: TypeScript Playwright Example

Ghost Healer integrates seamlessly with TypeScript Playwright projects using a simple wrapper.

## Integration
Wrap your `Page` object in your fixtures or at the start of your test.

```typescript
import { test, expect } from '@playwright/test';
import { protectPage } from 'ghost-healer-ts';

test('login test with AI healing', async ({ page }) => {
    // 👻 Protect the page instance
    const ghostPage = protectPage(page);

    await ghostPage.goto('https://example.com');

    // 🛡️ These calls are now self-healing
    await ghostPage.fill('#user-email', 'admin@example.com');
    await ghostPage.click('#login-button');
});
```

## How to Run
1. Install the Ghost Healer TS client: `npm install ghost-healer-ts`
2. Set the `GHOST_BRAIN_URL` environment variable.
3. Run your tests as usual: `npx playwright test`.
