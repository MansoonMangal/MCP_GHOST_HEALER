/**
 * ghost-healer-ts
 * Universal AI Self-Healing SDK for Playwright TypeScript/JavaScript
 *
 * Public API surface — everything a developer needs is exported here.
 */

// ── Core Classes ──────────────────────────────────────────────────────────────
export { GhostLocator }        from './GhostLocator';
export { SourceHealer }        from './SourceHealer';
export { GhostReporter }       from './GhostReporter';

// ── Type Exports ──────────────────────────────────────────────────────────────
export type { GhostConfig, HealResult }   from './GhostLocator';
export type { PatchResult }               from './SourceHealer';
export type { HealedEntry }               from './GhostReporter';

// ── Global Lifecycle Hooks ────────────────────────────────────────────────────
// Use these in playwright.config.ts:
//
//   import { ghostGlobalSetup, ghostGlobalTeardown } from 'ghost-healer-ts';
//   export default defineConfig({
//     globalSetup:    ghostGlobalSetup,
//     globalTeardown: ghostGlobalTeardown,
//   });
//
export { default as ghostGlobalSetup, ghostGlobalTeardown } from './setup';
