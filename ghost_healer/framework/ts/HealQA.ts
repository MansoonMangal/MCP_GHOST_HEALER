import { By, WebDriver, WebElement, until } from 'selenium-webdriver';
import axios from 'axios';
import * as fs from 'fs';
import * as path from 'path';

/**
 * 👻 HealQA Ghost Engine (TypeScript)
 * This utility "decorates" a normal Selenium driver with AI healing.
 */
export class HealQA {
    /**
     * Wraps a native driver to make it self-healing.
     */
    static getGhostDriver(driver: WebDriver): WebDriver {
        return new Proxy(driver, {
            get(target: any, prop: string) {
                const value = target[prop];
                if (prop === 'findElement') {
                    return async (...args: any[]) => {
                        const selector = args[0].value; // Get CSS selector
                        try {
                            const el = await value.apply(target, args);
                            return HealQA.wrapElement(driver, el, selector);
                        } catch (err) {
                            return HealQA.healAndGetElement(driver, selector);
                        }
                    };
                }
                return typeof value === 'function' ? value.bind(target) : value;
            }
        });
    }

    private static wrapElement(driver: WebDriver, element: WebElement, selector: string): WebElement {
        return new Proxy(element, {
            get(target: any, prop: string) {
                const value = target[prop];
                if (['click', 'sendKeys', 'clear'].includes(prop)) {
                    return async (...args: any[]) => {
                        try {
                            return await value.apply(target, args);
                        } catch (err) {
                            console.warn(`👻 Ghost Mode: Element failure. Healing...`);
                            const healed = await HealQA.healAndGetElement(driver, selector);
                            return await (healed as any)[prop](...args);
                        }
                    };
                }
                return typeof value === 'function' ? value.bind(target) : value;
            }
        });
    }

    private static async healAndGetElement(driver: WebDriver, selector: string): Promise<WebElement> {
        // AI HEALING LOGIC
        const agentPath = path.join(__dirname, '..', '..', 'assets', 'heal_qa_agent.js');
        const agentJs = fs.readFileSync(agentPath, 'utf8');
        await driver.executeScript(agentJs);
        const snapshot: any = await driver.executeScript('return HealQA.getDomSnapshot()');

        const response = await axios.post('http://localhost:8000/api/heal-locator', {
            selector: selector,
            dom_snapshot: snapshot.html,
            page_url: snapshot.url,
            action: 'click',
            test_name: 'Ghost_Mode_TS'
        });

        const healed = response.data.healed_locator;
        if (healed) {
            await driver.executeScript(`HealQA.highlight('${healed}')`);
            return await driver.findElement(By.css(healed));
        }
        throw new Error(`[HealQA] Failed to find or heal element: ${selector}`);
    }
}
