/**
 * GhostLocator — Universal AI Self-Healing Wrapper for Playwright
 *
 * Usage:
 *   import { GhostLocator } from 'ghost-healer-ts';
 *   const ghost = new GhostLocator(page, { brainUrl: process.env.GHOST_BRAIN_URL });
 *   await ghost.click('#login-btn');
 */
import { Page } from '@playwright/test';

export interface GhostConfig {
  brainUrl?: string;
  confidenceThreshold?: number;
  timeoutMs?: number;
  maxRetries?: number;
  framework?: string;
}

export interface HealResult {
  healedLocator: string | null;
  confidence: number;
  decision: string;
  analysis: string;
}

export class GhostLocator {
  private page: Page;
  private brainUrl: string;
  private confidenceThreshold: number;
  private timeoutMs: number;
  private maxRetries: number;
  private framework: string;

  constructor(page: Page, config: GhostConfig = {}) {
    this.page = page;
    this.brainUrl = config.brainUrl
      || process.env['GHOST_BRAIN_URL']
      || 'http://localhost:8000';
    this.confidenceThreshold = config.confidenceThreshold ?? 0.5;
    this.timeoutMs = config.timeoutMs ?? 30000;
    this.maxRetries = config.maxRetries ?? 3;
    this.framework = config.framework ?? 'playwright-ts';
  }

  // ── Public action methods ──────────────────────────────────────────────────

  async click(selector: string, options?: Parameters<Page['click']>[1]): Promise<void> {
    await this._healAndRetry(selector, 'click', async (sel) => {
      await this.page.click(sel, { ...options, timeout: 2000 });
    });
  }

  async fill(selector: string, value: string, options?: Parameters<Page['fill']>[2]): Promise<void> {
    await this._healAndRetry(selector, 'fill', async (sel) => {
      await this.page.fill(sel, value, { ...options, timeout: 2000 } as any);
    });
  }

  async hover(selector: string, options?: Parameters<Page['hover']>[1]): Promise<void> {
    await this._healAndRetry(selector, 'hover', async (sel) => {
      await this.page.hover(sel, { ...options, timeout: 2000 } as any);
    });
  }

  async check(selector: string, options?: Parameters<Page['check']>[1]): Promise<void> {
    await this._healAndRetry(selector, 'check', async (sel) => {
      await this.page.check(sel, { ...options, timeout: 2000 } as any);
    });
  }

  async selectOption(selector: string, value: string | string[]): Promise<string[]> {
    return await this._healAndRetry(selector, 'select', async (sel) => {
      return await this.page.selectOption(sel, value as any);
    }) as string[];
  }

  async waitForSelector(selector: string, options?: Parameters<Page['waitForSelector']>[1]): Promise<any> {
    return await this._healAndRetry(selector, 'wait', async (sel) => {
      return await this.page.waitForSelector(
        sel,
        options || {}
      );
    });
  }

  // ── Core heal-and-retry engine ────────────────────────────────────────────

  private async _healAndRetry<T>(
    selector: string,
    action: string,
    fn: (selector: string) => Promise<T>
  ): Promise<T | void> {
    try {
      return await fn(selector);
    } catch (originalError) {
      console.log(`[GHOST] ${action} failed for '${selector}'. Requesting AI heal...`);

      const healResult = await this._consultBrain(selector, action);

      if (healResult?.healedLocator && healResult.confidence >= this.confidenceThreshold) {
        console.log(`[GHOST] Healed '${selector}' → '${healResult.healedLocator}' `
          + `(confidence=${(healResult.confidence * 100).toFixed(1)}%)`);
        return await fn(healResult.healedLocator);
      }

      console.error(`[GHOST] Could not heal '${selector}'. decision=${healResult?.decision}`);
      throw originalError;
    }
  }

  private async _consultBrain(selector: string, action: string): Promise<HealResult | null> {
    for (let attempt = 0; attempt < this.maxRetries; attempt++) {
      try {
        const dom = await this.page.content();
        const response = await fetch(`${this.brainUrl}/api/heal-locator`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            selector,
            action,
            dom_snapshot: dom,
            page_url: this.page.url(),
            framework: this.framework,
          }),
          signal: AbortSignal.timeout(this.timeoutMs),
        });

        if (!response.ok) {
          console.warn(`[GHOST] Brain returned ${response.status}`);
          return null;
        }

        const data = await response.json() as any;
        return {
          healedLocator: data.healed_locator ?? null,
          confidence: data.confidence ?? 0,
          decision: data.decision ?? 'FAIL',
          analysis: data.analysis ?? '',
        };

      } catch (e) {
        const wait = (attempt + 1) * 5000;
        console.warn(`[GHOST] Brain unreachable. Retrying in ${wait / 1000}s... (attempt ${attempt + 1})`);
        await new Promise((r) => setTimeout(r, wait));
      }
    }
    return null;
  }
}
