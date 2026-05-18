/**
 * 👻 Ghost Healer — Global Teardown Entry Point
 *
 * Playwright's globalTeardown config expects a file path to a module
 * that exports a default function. This file wraps ghostGlobalTeardown.
 *
 * Usage in playwright.config.ts:
 *   globalTeardown: require.resolve('ghost-healer-ts/dist/teardown')
 */

import { ghostGlobalTeardown } from './setup';

export default ghostGlobalTeardown;
