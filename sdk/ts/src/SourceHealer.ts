/**
 * 👻 Ghost Healer — SourceHealer
 *
 * Runs LOCALLY on the developer's machine.
 * After the AI Brain returns a healed locator, this module opens
 * the actual test source file and rewrites the broken selector in-place.
 *
 * No backup files are created — edits are made directly.
 */

import * as fs from 'fs';
import * as path from 'path';

export interface PatchResult {
  success: boolean;
  file: string | null;
  line: number;
  oldSelector: string;
  newSelector: string;
}

export class SourceHealer {
  /**
   * Physically patch the broken selector in the source file.
   *
   * @param filePath   Absolute path to the test file
   * @param lineNumber Line number where the selector appears (1-indexed)
   * @param oldSelector The broken locator string
   * @param newSelector The AI-healed locator string
   */
  static applyFix(
    filePath: string | null,
    lineNumber: number,
    oldSelector: string,
    newSelector: string
  ): PatchResult {
    const result: PatchResult = {
      success: false,
      file: filePath,
      line: lineNumber,
      oldSelector,
      newSelector,
    };

    if (!filePath || !fs.existsSync(filePath)) {
      return result;
    }

    try {
      const content = fs.readFileSync(filePath, 'utf8');
      const lines = content.split('\n');
      const escapedOld = oldSelector.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      const quoteRe = new RegExp(`(['"])${escapedOld}(['"])`, 'g');

      let fixedLine = lineNumber;
      let fixed = false;

      // ── Step 1: Try exact line ───────────────────────────────────
      if (lineNumber > 0 && lineNumber <= lines.length) {
        const orig = lines[lineNumber - 1];
        let updated = orig.replace(quoteRe, `$1${newSelector}$2`);
        if (updated === orig) updated = orig.split(oldSelector).join(newSelector);
        if (updated !== orig) {
          lines[lineNumber - 1] = updated;
          fixed = true;
        }
      }

      // ── Step 2: Full-file scan fallback ─────────────────────────
      if (!fixed) {
        for (let i = 0; i < lines.length; i++) {
          if (lines[i].includes(oldSelector)) {
            let updated = lines[i].replace(quoteRe, `$1${newSelector}$2`);
            if (updated === lines[i]) updated = lines[i].split(oldSelector).join(newSelector);
            lines[i] = updated;
            fixedLine = i + 1;
            fixed = true;
            break;
          }
        }
      }

      if (fixed) {
        fs.writeFileSync(filePath, lines.join('\n'), 'utf8');
        result.success = true;
        result.line = fixedLine;

        console.log(
          `[GHOST] 📝 SourceHealer patching: ${path.relative(process.cwd(), filePath)}:${fixedLine}`
        );
        console.log(`         OLD → '${oldSelector}'`);
        console.log(`         NEW → '${newSelector}'`);
        console.log(`[GHOST] ✅ Source permanently fixed.\n`);
      }
    } catch (e: any) {
      console.error('[GHOST] SourceHealer error:', e.message);
    }

    return result;
  }
}
