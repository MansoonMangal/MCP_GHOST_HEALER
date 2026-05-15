"""
👻 Ghost Healer Demo — Selenium Python

Uses intentionally BROKEN By.ID locators on SauceDemo.
protect_driver() wraps find_element with AI healing.
The test passes despite all broken locators.

Requirements:
    pip install ghost-healer selenium webdriver-manager

Run:
    python demo/selenium-python/test_demo.py
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from ghost_healer.adapters.selenium import protect_driver


def run_demo():
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)

    # 👻 Activate Ghost Healer — one line, zero other changes
    protect_driver(driver)

    try:
        driver.get("https://www.saucedemo.com/")

        # 🔴 BROKEN: correct is By.ID, "user-name"
        driver.find_element(By.ID, "user-name-WRONG").send_keys("standard_user")

        # 🔴 BROKEN: correct is By.ID, "password"
        driver.find_element(By.ID, "password-WRONG").send_keys("secret_sauce")

        # 🔴 BROKEN: correct is By.ID, "login-button"
        driver.find_element(By.ID, "login-btn-WRONG").click()

        assert "inventory" in driver.current_url
        print("✅ Selenium login succeeded despite broken locators — Ghost Healer worked!")

    finally:
        driver.quit()


if __name__ == "__main__":
    run_demo()
