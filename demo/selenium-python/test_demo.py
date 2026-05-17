"""
👻 Ghost Healer Demo — Selenium Python (ZERO test code changes)

Standard Selenium Python test.
No custom wrappers in test logic.
No locator changes.
No healing API calls.

ONE-LINE ACTIVATION:
    protect_driver(driver)

Ghost Healer patches Selenium internally and heals:
    - find_element()
    - click()
    - send_keys()
    - waits
    - stale locators

The locators below are intentionally WRONG.
Ghost Healer heals them automatically.

Requirements:
    pip install ghost-healer selenium webdriver-manager

Run:
    python demo/selenium-python/test_demo.py
"""

import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

from ghost_healer.adapters.selenium import protect_driver


def run_demo():

    options = webdriver.ChromeOptions()

    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)

    # 👻 ONE-LINE ACTIVATION
    # Patches Selenium WebDriver globally
    protect_driver(driver)

    try:

        # Give AI healing enough retry time
        driver.implicitly_wait(30)

        driver.get("https://www.saucedemo.com/")

        time.sleep(2)

        # 🔴 BROKEN: correct = #user-name
        driver.find_element(
            By.CSS_SELECTOR,
            "#user-name-WRONG"
        ).send_keys("standard_user")

        # 🔴 BROKEN: correct = #password
        driver.find_element(
            By.CSS_SELECTOR,
            "#password-WRONG"
        ).send_keys("secret_sauce")

        # 🔴 BROKEN: correct = #login-button
        driver.find_element(
            By.CSS_SELECTOR,
            "#login-button-WRONG"
        ).click()

        time.sleep(2)

        assert "inventory" in driver.current_url

        # 🔴 BROKEN: correct = #add-to-cart-sauce-labs-backpack
        driver.find_element(
            By.CSS_SELECTOR,
            "#add-to-cart-sauce-labs-backpack-WRONG"
        ).click()

        print(
            "\n[SUCCESS] Selenium Python passed with fully broken locators!"
        )

    finally:

        driver.quit()


if __name__ == "__main__":
    run_demo()