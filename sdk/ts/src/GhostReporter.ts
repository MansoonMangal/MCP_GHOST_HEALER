/**
 * 👻 Ghost Healer — GhostReporter
 *
 * Responsible for:
 *  1. Writing reports/ghost/suggested-fixes.json
 *  2. Writing per-session audit trail JSON
 *  3. Printing the post-run healing summary banner
 */

import * as fs from 'fs';
import * as path from 'path';

export interface HealedEntry {
  uuid: string;
  selector: string;
  healed_locator: string;
  confidence: number;
  action: string;
  url: string;
  file: string | null;
  line: number;
  screenshot_path: string;
  source_patched: boolean;
  timestamp: string;
  session_id: string;
}

export class GhostReporter {
  static writeReports(entries: HealedEntry[], workspaceRoot: string): void {
    const reportDir = path.join(workspaceRoot, 'reports', 'ghost');
    fs.mkdirSync(reportDir, { recursive: true });

    // ── suggested-fixes.json ────────────────────────────────────────
    const fixesFile = path.join(reportDir, 'suggested-fixes.json');
    let existing: any[] = [];
    if (fs.existsSync(fixesFile)) {
      try { existing = JSON.parse(fs.readFileSync(fixesFile, 'utf8')); } catch (_) {}
    }
    for (const e of entries) {
      existing.unshift({
        timestamp: e.timestamp,
        session_id: e.session_id,
        framework: 'playwright-ts',
        language: 'javascript/typescript',
        file: e.file,
        line: e.line,
        action: e.action,
        old_locator: e.selector,
        suggested_locator: e.healed_locator,
        confidence: e.confidence,
        page_url: e.url,
        screenshot: e.screenshot_path,
        source_patched: e.source_patched,
      });
    }
    fs.writeFileSync(fixesFile, JSON.stringify(existing, null, 2), 'utf8');

    // ── Cumulative ghost-report.json ───────────────────────────────────────────
    if (entries.length > 0) {
      const reportFile = path.join(reportDir, `ghost-report.json`);
      let reportData: any[] = [];
      if (fs.existsSync(reportFile)) {
        try { reportData = JSON.parse(fs.readFileSync(reportFile, 'utf8')); } catch (_) {}
      }
      for (const e of entries) {
        // Prepend new records so they show up at the top
        reportData.unshift({
          timestamp: e.timestamp,
          session_id: e.session_id,
          framework: 'playwright-ts',
          action: e.action,
          old_locator: e.selector,
          suggested_locator: e.healed_locator,
          confidence: e.confidence,
          page_url: e.url,
          file: e.file,
          line: e.line,
          screenshot: e.screenshot_path,
          source_patched: e.source_patched,
          decision: 'AUTO_HEAL',
          healing_mode: 'deferred-parallel',
        });
      }
      fs.writeFileSync(reportFile, JSON.stringify(reportData, null, 2), 'utf8');
    }
  }

  static printSummary(
    totalFailures: number,
    totalHealed: number,
    totalPatched: number,
    patchedFiles: Set<string>,
    screenshotCount: number,
    reportDir: string
  ): void {
    const W = 52;
    const pad = (s: string) => s.padEnd(W - 4);
    const divider = '═'.repeat(W);

    const filesStr =
      totalPatched > 0
        ? `${totalPatched} (${[...patchedFiles].join(', ')})`
        : '0';

    console.log('\n');
    console.log(`╔${divider}╗`);
    console.log(`║  👻 GHOST HEALER — POST-RUN HEALING REPORT${' '.repeat(W - 43)}║`);
    console.log(`╠${divider}╣`);
    console.log(`║  ${pad(`Failures Detected   : ${totalFailures}`)}║`);
    console.log(`║  ${pad(`Successfully Healed : ${totalHealed}`)}║`);
    console.log(`║  ${pad(`Source Files Patched: ${filesStr}`)}║`);
    console.log(`║  ${pad(`Screenshots Saved   : ${screenshotCount}`)}║`);
    console.log(`║  ${pad(`Reports Dir         : ${reportDir}`)}║`);
    console.log(`╚${divider}╝`);
    console.log('');

    if (totalHealed > 0) {
      console.log(
        `[GHOST] 🎉 ${totalHealed} locator(s) permanently fixed! Re-run your tests — they should pass now.\n`
      );
    } else if (totalFailures > 0) {
      console.log(
        `[GHOST] ⚠️  ${totalFailures} failure(s) detected but AI Brain could not heal them. Check reports for details.\n`
      );
    } else {
      console.log(`[GHOST] ✅ All tests passed. No healing needed.\n`);
    }
  }
}
