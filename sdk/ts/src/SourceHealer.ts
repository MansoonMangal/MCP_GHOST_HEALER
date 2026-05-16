import * as fs from 'fs';
import * as path from 'path';

/**
 * 👻 Ghost Source Healer (TypeScript)
 * 
 * Permanently rewrites source code files when a locator is healed.
 * Uses stack tracing to find the caller test file.
 */
export class SourceHealer {
  /**
   * Rewrites the caller file to replace oldSelector with newSelector.
   */
  public applyFix(oldSelector: string, newSelector: string): boolean {
    const callerFile = this.findCallerFile();
    if (!callerFile) {
      console.warn(`[GHOST] [SourceHealer] Could not locate source file for '${oldSelector}'`);
      return false;
    }

    try {
      const content = fs.readFileSync(callerFile, 'utf8');
      
      // Regex to match the selector inside any quote type
      const escapedOld = oldSelector.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      const pattern = new RegExp(`(['"\`])${escapedOld}(['"\`])`, 'g');

      if (!pattern.test(content)) {
        console.warn(`[GHOST] [SourceHealer] Selector '${oldSelector}' not found in ${path.basename(callerFile)}`);
        return false;
      }

      const newContent = content.replace(pattern, `$1${newSelector}$2`);
      fs.writeFileSync(callerFile, newContent, 'utf8');
      
      console.log(`[GHOST] [SourceHealer] ✅ Permanently patched: ${path.basename(callerFile)}`);
      return true;
    } catch (err) {
      console.error(`[GHOST] [SourceHealer] Failed to patch ${callerFile}:`, err);
      return false;
    }
  }

  private findCallerFile(): string | null {
    const err = new Error();
    const stack = err.stack;
    if (!stack) return null;

    const lines = stack.split('\n');
    for (const line of lines) {
      // Look for absolute paths that look like test files
      const match = line.match(/\((.*):(\d+):(\d+)\)/) || line.match(/at (.*):(\d+):(\d+)/);
      if (match) {
        const filePath = match[1];
        const fileName = path.basename(filePath);
        if (
          !filePath.includes('node_modules') &&
          !fileName.includes('SourceHealer') &&
          !fileName.includes('GhostLocator') &&
          !fileName.includes('setup') &&
          !fileName.includes('pw-hook') &&
          (filePath.endsWith('.ts') || filePath.endsWith('.js') || filePath.endsWith('.java')) &&
          fs.existsSync(filePath)
        ) {
          return filePath;
        }
      }
    }
    return null;
  }
}

export const sourceHealer = new SourceHealer();
