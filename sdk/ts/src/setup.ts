/**
 * 👻 Ghost Healer — Global Setup & Teardown
 *
 * SETUP   → Patches Playwright prototypes before any test runs.
 * TEARDOWN → After ALL tests finish:
 *             1. Reads healed_*.json from .ghost_queue/
 *             2. Applies SourceHealer patches to local source files
 *             3. Writes reports (suggested-fixes.json, session_*.json)
 *             4. Prints the healing summary banner
 *             5. Cleans up the queue directory
 *
 * In playwright.config.ts:
 *   import { ghostGlobalSetup, ghostGlobalTeardown } from 'ghost-healer-ts';
 *   export default defineConfig({
 *     globalSetup:    ghostGlobalSetup,
 *     globalTeardown: ghostGlobalTeardown,
 *   });
 */

import * as fs   from 'fs';
import * as path from 'path';
import { chromium } from '@playwright/test';
import { SourceHealer } from './SourceHealer';
import { GhostReporter, HealedEntry } from './GhostReporter';

// ── Helpers ───────────────────────────────────────────────────────────────────

function findWorkspaceRoot(): string {
  let dir = process.cwd();
  for (let i = 0; i < 20; i++) {
    if (fs.existsSync(path.join(dir, 'ghost.yaml')) || fs.existsSync(path.join(dir, '.git'))) {
      return dir;
    }
    const parent = path.dirname(dir);
    if (parent === dir) break;
    dir = parent;
  }
  return path.resolve(__dirname, '../../..');
}

// ── Global Setup ──────────────────────────────────────────────────────────────

/**
 * Patches Playwright Page & Locator prototypes so the deferred healing
 * interceptors are active for every test worker.
 *
 * NOTE: The actual heavy lifting (screenshot, brain call, queue) happens
 * inside pw-hook.js which is loaded via require() in playwright.config.ts.
 * This setup function only validates the connection is live.
 */
export default async function ghostGlobalSetup(): Promise<void> {
  const wsRoot   = findWorkspaceRoot();
  const queueDir = path.join(wsRoot, 'reports', 'ghost', '.ghost_queue');

  // Clear any stale queue from a previous run
  if (fs.existsSync(queueDir)) {
    fs.rmSync(queueDir, { recursive: true, force: true });
  }

  console.log('\n[GHOST] 👻 Ghost Healer activated — Deferred Parallel Healing mode.');
  console.log('[GHOST] 🧠 AI Brain URL:', process.env['GHOST_BRAIN_URL'] || 'https://ghost-healer-brain.onrender.com');
  console.log('[GHOST] ℹ️  Failures will be healed after the test suite finishes.\n');
}

// ── Global Teardown ───────────────────────────────────────────────────────────

/**
 * Runs after ALL test workers have exited.
 *
 * Flow:
 *  1. Wait briefly so all worker `beforeExit` brain requests can flush to disk
 *  2. Read every healed_*.json from .ghost_queue/
 *  3. Apply SourceHealer for each successful heal
 *  4. Generate reports
 *  5. Print summary banner
 *  6. Delete queue dir
 */
export async function ghostGlobalTeardown(): Promise<void> {
  const wsRoot   = findWorkspaceRoot();
  const queueDir = path.join(wsRoot, 'reports', 'ghost', '.ghost_queue');
  const reportDir = path.join(wsRoot, 'reports', 'ghost');

  // Give workers a moment to finish writing their healed_*.json files
  await new Promise(r => setTimeout(r, 3000));

  // Count total failures
  let totalFailures = 0;
  let screenshotCount = 0;

  if (fs.existsSync(queueDir)) {
    totalFailures = fs.readdirSync(queueDir)
      .filter(f => f.startsWith('failure_')).length;
  }

  // Count screenshots already saved by workers
  const ssDir = path.join(reportDir, 'screenshots');
  if (fs.existsSync(ssDir)) {
    screenshotCount = fs.readdirSync(ssDir)
      .filter(f => f.endsWith('.png')).length;
  }

  // No failures → clean exit
  if (totalFailures === 0 || !fs.existsSync(queueDir)) {
    GhostReporter.printSummary(0, 0, 0, new Set(), 0, path.relative(process.cwd(), reportDir));
    return;
  }

  // ── Read failures and call Brain ──────────────────────────────────────────
  const failureFiles = fs.readdirSync(queueDir).filter(f => f.startsWith('failure_'));
  const healedEntries: HealedEntry[] = [];
  const brainUrl = process.env['GHOST_BRAIN_URL'] || 'https://ghost-healer-brain.onrender.com';
  const confThreshold = 0.5;

  if (failureFiles.length > 0) {
    console.log(`\n[GHOST] 🧠 Consulting AI Brain for ${failureFiles.length} failure(s)...`);
  }

  // Process failures in parallel
  await Promise.all(failureFiles.map(async (fname) => {
    try {
      const raw = fs.readFileSync(path.join(queueDir, fname), 'utf8');
      const failure = JSON.parse(raw);
      
      let domSnapshot = '';
      if (failure.html_path && fs.existsSync(failure.html_path)) {
        domSnapshot = fs.readFileSync(failure.html_path, 'utf8');
      }

      // Retry up to 3 times
      let healedLocator = null;
      let confidence = 0;
      for (let attempt = 0; attempt < 3; attempt++) {
        try {
          const resp = await fetch(`${brainUrl}/api/heal-locator`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              selector: failure.selector, 
              action: failure.action,
              dom_snapshot: domSnapshot,
              page_url: failure.url,
              framework: 'playwright-ts',
            }),
            signal: AbortSignal.timeout(30000),
          });
          if (resp.ok) {
            const data = (await resp.json()) as { healed_locator?: string; confidence?: number };
            if (data.healed_locator && data.confidence !== undefined && data.confidence >= confThreshold) {
              healedLocator = data.healed_locator;
              confidence = data.confidence;
              break;
            }
          }
        } catch (_) {
          await new Promise(r => setTimeout(r, (attempt + 1) * 3000));
        }
      }

      if (healedLocator) {
        console.log(`[GHOST] 🧠 Brain healed '${failure.selector}' → '${healedLocator}' (${(confidence * 100).toFixed(1)}%)`);
        healedEntries.push({
          uuid: failure.uuid,
          selector: failure.selector,
          action: failure.action,
          url: failure.url,
          file: failure.file,
          line: failure.line,
          healed_locator: healedLocator,
          confidence: confidence,
          timestamp: failure.timestamp,
          session_id: failure.session_id,
          screenshot_path: failure.screenshot_path,
          source_patched: false
        });
      }
    } catch (_) {
      // malformed file — skip
    }
  }));

  // ── Apply source patches ──────────────────────────────────────────────────
  let totalPatched = 0;
  const patchedFiles = new Set<string>();

  if (healedEntries.length > 0) {
    console.log(`\n[GHOST] 🔧 Applying ${healedEntries.length} source patch(es)...\n`);
  }

  for (const entry of healedEntries) {
    const result = SourceHealer.applyFix(
      entry.file,
      entry.line,
      entry.selector,
      entry.healed_locator,
    );
    entry.source_patched = result.success;
    if (result.success) {
      totalPatched++;
      if (entry.file) patchedFiles.add(path.basename(entry.file));
    }
  }

  // ── Write reports ─────────────────────────────────────────────────────────
  fs.mkdirSync(reportDir, { recursive: true });
  GhostReporter.writeReports(healedEntries, wsRoot);

  // ── Print summary banner ──────────────────────────────────────────────────
  GhostReporter.printSummary(
    totalFailures,
    healedEntries.length,
    totalPatched,
    patchedFiles,
    screenshotCount,
    path.relative(process.cwd(), reportDir),
  );

  // ── Cleanup queue dir ─────────────────────────────────────────────────────
  try {
    fs.rmSync(queueDir, { recursive: true, force: true });
  } catch (_) {}
}