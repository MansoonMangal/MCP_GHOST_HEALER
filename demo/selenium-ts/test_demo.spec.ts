/**
 * 👻 Ghost Healer Demo — Selenium TypeScript (ZERO test code changes)
 *
 * Standard selenium-webdriver TypeScript test.
 * No Ghost Healer imports.
 * No wrappers.
 * No custom APIs.
 *
 * Healing activates globally via:
 *
 * jest.config.ts
 * ----------------
 * setupFiles: ['ghost-healer-ts/selenium-setup']
 *
 * OR
 *
 * .mocharc.js
 * ----------------
 * require: ['ghost-healer-ts/selenium-setup']
 *
 * Run:
 *   npx ts-mocha demo/selenium-ts/test_demo.spec.ts
 */

import { Builder, By, WebDriver } from 'selenium-webdriver';
import { Options } from 'selenium-webdriver/chrome.js';
import * as assert from 'assert';

describe('👻 Selenium TS — Ghost healing demo', function () {

  // 👻 Give AI healing enough retry time
  this.timeout(60000);

  let driver: WebDriver;

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

    // 👻 NO protectDriver()
    // 👻 NO wrappers
    // Ghost patches WebDriver.prototype globally
  });

  after(async () => {

    if (driver) {
      await driver.quit();
    }
  });

  it(
    'should login despite fully broken locators',
    async () => {

      await driver.get(
        'https://www.saucedemo.com/'
      );

      // 🔴 BROKEN: correct = user-name
      await (
        await driver.findElement(
          By.id('user-name-WRONG')
        )
      ).sendKeys('standard_user');

      // 🔴 BROKEN: correct = password
      await (
        await driver.findElement(
          By.id('password-WRONG')
        )
      ).sendKeys('secret_sauce');

      // 🔴 BROKEN: correct = login-button
      await (
        await driver.findElement(
          By.id('login-button-WRONG')
        )
      ).click();

      const url = await driver.getCurrentUrl();

      assert.ok(
        url.includes('inventory'),
        `Expected inventory URL, got: ${url}`
      );

      // 🔴 BROKEN: correct = add-to-cart-sauce-labs-backpack
      await (
        await driver.findElement(
          By.css(
            '#add-to-cart-sauce-labs-backpack-WRONG'
          )
        )
      ).click();

      console.log(
        '\n[SUCCESS] Selenium + TS passed with fully broken locators!'
      );
    }
  );
});