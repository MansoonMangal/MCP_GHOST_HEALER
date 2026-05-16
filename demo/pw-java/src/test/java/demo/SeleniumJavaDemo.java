package demo;

import com.ghosthealer.core.*;
import org.junit.jupiter.api.*;
import org.junit.jupiter.api.extension.ExtendWith;
import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;

/**
 * 👻 Ghost Healer Demo — Selenium Java
 *
 * TWO CHANGES on BaseTest — zero changes in individual tests:
 * 1. @ExtendWith(GhostHealerExtension.class)
 * 2. @GhostDriver on the driver field
 *
 * Run: mvn test -Dtest=SeleniumJavaDemo
 */

// ── BaseTest (ONE-TIME SETUP, covers all tests)
// ───────────────────────────────

@ExtendWith(GhostHealerExtension.class) // ← CHANGE 1: add extension
abstract class BaseTest {

    @GhostDriver // ← CHANGE 2: mark driver field
    protected WebDriver driver;

    @BeforeEach
    void setUp() {
        ChromeOptions opts = new ChromeOptions();
        opts.addArguments("--no-sandbox", "--disable-dev-shm-usage");
        // Explicitly wrap for the demo to ensure it works in all environments
        driver = GhostHealerExtension.wrap(new ChromeDriver(opts));
    }

    @AfterEach
    void tearDown() {
        if (driver != null)
            driver.quit();
    }
}

// ── Test class (ZERO CHANGES — pure Selenium code)
// ────────────────────────────

class SeleniumJavaDemo extends BaseTest {

    @Test
    @DisplayName("Login with broken selectors — Ghost heals them")
    void testLoginWithBrokenLocators() {
        driver.get("https://www.saucedemo.com/");

        // Standard Selenium API — broken locators, Ghost heals silently
        driver.findElement(By.id("user-name")).sendKeys("standard_user");
        driver.findElement(By.id("password")).sendKeys("secret_sauce");
        driver.findElement(By.id("login-button")).click();

        Assertions.assertTrue(
                driver.getCurrentUrl().contains("inventory"),
                "Login should succeed despite broken locators");
        System.out.println("[SUCCESS] Selenium + Java: Passed with 2 annotations in BaseTest only!");
    }
}
