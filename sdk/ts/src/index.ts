/**
 * ghost-healer-ts
 * Universal AI Self-Healing SDK for Playwright TypeScript/JavaScript
 */
export { GhostLocator } from './GhostLocator';
export type { GhostConfig, HealResult } from './GhostLocator';

// Global setup — use in playwright.config.ts globalSetup field
export { default as ghostGlobalSetup } from './setup';
