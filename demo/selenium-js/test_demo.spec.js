/**
 * 👻 Ghost Healer Demo — Selenium JavaScript (ZERO test code changes)
 *
 * Standard selenium-webdriver JS test. No Ghost Healer imports.
 *
 * MINIMUM CHANGE — add to .mocharc.js or jest.config.js:
 *   require: ['ghost-healer-ts/selenium-setup']
 *
 * Run: npx mocha demo/selenium-js/test_demo.spec.js
 */
const { Builder, By } = require('selenium-webdriver');
const { Options } = require('selenium-webdriver/chrome');
const assert = require('assert');

describe('Selenium JS — Ghost healing demo', () => {
  let driver;

  before(async () => {
    const opts = new Options();
    opts.addArguments('--headless', '--no-sandbox', '--disable-dev-shm-usage');
    driver = await new Builder()
      .forBrowser('chrome')
      .setChromeOptions(opts)
      .build();
    // NO protect_driver() — WebDriver.prototype already patched by setup require
  });

  after(async () => {
    await driver.quit();
  });

  it('should login despite broken locators', async () => {
    await driver.get('https://www.saucedemo.com/');

    // Standard findElement — broken, Ghost heals silently
    await (await driver.findElement(By.id('user-name-WRONG'))).sendKeys('standard_user');
    await (await driver.findElement(By.id('password-WRONG'))).sendKeys('secret_sauce');
    await (await driver.findElement(By.id('login-btn-WRONG'))).click();

    const url = await driver.getCurrentUrl();
    assert.ok(url.includes('inventory'), `Expected inventory, got: ${url}`);
    console.log('✅ Selenium + JS: Passed with zero Ghost Healer code in test!');
  });
});
