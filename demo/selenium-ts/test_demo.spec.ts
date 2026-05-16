/**
 * 👻 Ghost Healer Demo — Selenium TypeScript (ZERO test code changes)
 *
 * Standard selenium-webdriver test. No Ghost Healer code in test file.
 * Healing activated via setup file imported in jest.config.ts / mocha opts.
 *
 * MINIMUM CHANGE — add to jest.config.ts:
 *   setupFiles: ['ghost-healer-ts/selenium-setup']
 *
 * OR in mocha .mocharc.js:
 *   require: ['ghost-healer-ts/selenium-setup']
 *
 * Run: npx ts-mocha demo/selenium-ts/test_demo.spec.ts
 */
import { Builder, By, WebDriver } from 'selenium-webdriver';
import { Options } from 'selenium-webdriver/chrome.js';
import * as assert from 'assert';

describe('Selenium TS — Ghost healing demo', function() {
  this.timeout(60000); // 👻 Increase timeout for AI healing
  let driver: WebDriver;

  before(async () => {
    const opts = new Options();
    opts.addArguments('--no-sandbox', '--disable-dev-shm-usage');
    driver = await new Builder()
      .forBrowser('chrome')
      .setChromeOptions(opts)
      .build();
    // NO protect_driver() call — WebDriver.prototype is already patched by setup file
  });

  after(async () => {
    await driver.quit();
  });

  it('should login despite broken locators — Ghost heals automatically', async () => {
    await driver.get('https://www.saucedemo.com/');

    // Standard selenium findElement — broken ID, Ghost heals silently
    await (await driver.findElement(By.id('user-name'))).sendKeys('standard_user');
    await (await driver.findElement(By.id('password'))).sendKeys('secret_sauce');
    await (await driver.findElement(By.id('login-button'))).click();

    const url = await driver.getCurrentUrl();
    assert.ok(url.includes('inventory'), `Expected inventory URL, got: ${url}`);
    console.log('[SUCCESS] Selenium + TS: Passed with zero Ghost Healer code in test!');
  });
});
