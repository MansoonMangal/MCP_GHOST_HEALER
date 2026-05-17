/**
 * 👻 Ghost Healer Demo — Selenium JavaScript (ZERO test code changes)
 *
 * Standard selenium-webdriver JS test.
 * No Ghost Healer imports.
 * No wrappers.
 * No custom APIs.
 *
 * Healing activates globally via:
 *
 * .mocharc.js
 * ----------------
 * module.exports = {
 *   require: ['ghost-healer-ts/selenium-setup']
 * };
 *
 * Run:
 *   npx mocha demo/selenium-js/test_demo.spec.js
 */

const { Builder, By } = require('selenium-webdriver');
const { Options } = require('selenium-webdriver/chrome');
const assert = require('assert');

describe('👻 Selenium JS — Ghost healing demo', function () {

  // Give AI healing enough retry time
  this.timeout(60000);

  let driver;

  before(async () => {

    const opts = new Options();

    opts.addArguments(
      '--no-sandbox',
      '--disable-dev-shm-usage'
    );

    driver = await new Builder()
      .forBrowser('chrome')
      .setChromeOptions(opts)
      .build();

    // 👻 NO Ghost wrapper
    // 👻 NO protectDriver()
    // Ghost patches WebDriver.prototype automatically
  });

  after(async () => {

    if (driver) {
      await driver.quit();
    }
  });

  it('should login despite broken locators', async () => {

    await driver.get('https://www.saucedemo.com/');

    // 🔴 BROKEN: correct = #user-name
    await (
      await driver.findElement(
        By.css('#user-name-WRONG')
      )
    ).sendKeys('standard_user');

    // 🔴 BROKEN: correct = #password
    await (
      await driver.findElement(
        By.css('#password-WRONG')
      )
    ).sendKeys('secret_sauce');

    // 🔴 BROKEN: correct = #login-button
    await (
      await driver.findElement(
        By.id('login-button-WRONG')
      )
    ).click();

    const url = await driver.getCurrentUrl();

    assert.ok(
      url.includes('inventory'),
      `Expected inventory page, got: ${url}`
    );

    // 🔴 BROKEN: correct = #add-to-cart-sauce-labs-backpack
    await (
      await driver.findElement(
        By.css('#add-to-cart-sauce-labs-backpack-WRONG')
      )
    ).click();

    console.log(
      '\n[SUCCESS] Selenium + JS passed with fully broken locators!'
    );
  });
});