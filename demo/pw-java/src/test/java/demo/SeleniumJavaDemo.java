package demo;

import com.ghosthealer.core.*;
import org.junit.jupiter.api.*;
import org.junit.jupiter.api.extension.ExtendWith;
import org.openqa.selenium.*;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;

/**
 * 👻 Ghost Healer Demo — Selenium Java Locator Healing Validation
 *
 * PURPOSE:
 * Validate the NEW enterprise Ghost architecture.
 *
 * Old Ghost architecture only intercepted:
 * - driver.findElement()
 * - page-level APIs
 *
 * Real enterprise Selenium frameworks mostly use:
 * - WebElement.click()
 * - WebElement.sendKeys()
 * - wrapper layers
 * - Page Object Models
 *
 * This demo validates:
 * - WebElement interception
 * - runtime healing
 * - AI recovery flow
 * - Render Brain integration
 *
 * EXPECTED RESULT:
 * Ghost silently heals broken locators using the cloud AI Brain.
 *
 * ONLY TWO CHANGES REQUIRED:
 *
 * 1.
 * @ExtendWith(GhostHealerExtension.class)
 *
 * 2.
 * 
 * @GhostDriver on WebDriver field
 *
 *              ZERO changes inside actual test logic.
 *
 *              Run:
 *              mvn test -Dtest=SeleniumJavaDemo
 */

// ─────────────────────────────────────────────
// BaseTest
// ONE-TIME setup for all Selenium tests
// ─────────────────────────────────────────────

@ExtendWith(GhostHealerExtension.class)
abstract class BaseTest {

    @GhostDriver
    protected WebDriver driver;

    @BeforeEach
    void setUp() {

        ChromeOptions opts = new ChromeOptions();

        opts.addArguments(
                "--no-sandbox",
                "--disable-dev-shm-usage");

        driver = new ChromeDriver(opts);
    }

    @AfterEach
    void tearDown() {

        if (driver != null) {
            driver.quit();
        }
    }
}

// ─────────────────────────────────────────────
// Test Class
// ZERO Ghost-specific test changes
// ─────────────────────────────────────────────

class SeleniumJavaDemo extends BaseTest {

    @Test
    @DisplayName("WebElement healing — Ghost heals broken locators silently")
    void testLocatorHealing() {

        driver.get(
                "https://www.saucedemo.com/");

        // ─────────────────────────────────────────
        // 🔴 BROKEN USERNAME LOCATOR
        // Correct = user-name
        // ─────────────────────────────────────────

        WebElement usernameInput = driver.findElement(
                By.id("user-name"));

        usernameInput.sendKeys(
                "standard_user");

        // ─────────────────────────────────────────
        // 🔴 BROKEN PASSWORD LOCATOR
        // Correct = password
        // ─────────────────────────────────────────

        WebElement passwordInput = driver.findElement(
                By.id("password"));

        passwordInput.sendKeys(
                "secret_sauce");

        // ─────────────────────────────────────────
        // 🔴 BROKEN LOGIN BUTTON
        // Correct = login-button
        // ─────────────────────────────────────────

        WebElement loginButton = driver.findElement(
                By.id("login-button"));

        loginButton.click();

        // ─────────────────────────────────────────
        // Validate login success
        // ─────────────────────────────────────────

        Assertions.assertTrue(
                driver.getCurrentUrl()
                        .contains("inventory"),
                "Login should succeed despite broken locators");

        // ─────────────────────────────────────────
        // 🔴 BROKEN ADD TO CART BUTTON
        // Correct = add-to-cart-sauce-labs-backpack
        // ─────────────────────────────────────────

        WebElement addToCart = driver.findElement(
                By.id(
                        "item_4_img_link"));

        addToCart.click();

        Assertions.assertTrue(
                driver.getCurrentUrl()
                        .contains("inventory"),
                "Cart interaction should succeed");

        System.out.println(
                "[SUCCESS] Selenium Java Locator API validation passed.");
    }
}
