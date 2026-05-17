package demo;

import com.microsoft.playwright.*;
import com.ghosthealer.core.GhostPlaywright;
import org.junit.jupiter.api.*;

/**
 * 👻 Ghost Healer Demo — Playwright Java Locator API Validation
 *
 * PURPOSE:
 * Validate the NEW enterprise Ghost architecture.
 *
 * Old Ghost architecture only intercepted:
 * - page.click()
 * - page.fill()
 *
 * Real enterprise frameworks mostly use:
 * - Locator.click()
 * - Locator.fill()
 * - Locator.waitFor()
 *
 * This demo validates that Locator API healing works correctly.
 *
 * ONE CHANGE REQUIRED:
 * GhostPlaywright.protect(page)
 *
 * EXPECTED RESULT:
 * Ghost silently heals broken locators using the Render AI Brain.
 *
 * Run:
 * mvn test -Dtest=PlaywrightJavaDemo
 */

public class PlaywrightJavaDemo {

    // ─────────────────────────────────────────────
    // Browser Setup
    // ─────────────────────────────────────────────

    static Playwright playwright;
    static Browser browser;
    static BrowserContext context;

    Page page;

    @BeforeAll
    static void launchBrowser() {

        playwright = Playwright.create();

        browser = playwright.chromium().launch(
                new BrowserType.LaunchOptions()
                        .setHeadless(false));
    }

    @BeforeEach
    void setUp() {

        context = browser.newContext();

        // 👻 ONE LINE CHANGE
        page = GhostPlaywright.protect(
                context.newPage());
    }

    @AfterEach
    void tearDown() {

        context.close();
    }

    @AfterAll
    static void closeBrowser() {

        browser.close();

        playwright.close();
    }

    // ─────────────────────────────────────────────
    // Locator API Healing Demo
    // ─────────────────────────────────────────────

    @Test
    @DisplayName("Locator API healing — Ghost heals broken locators silently")
    void testLocatorApiHealing() {

        page.navigate(
                "https://www.saucedemo.com/");

        // ─────────────────────────────────────────
        // 🔴 BROKEN USERNAME LOCATOR
        // Correct = #user-name
        // ─────────────────────────────────────────

        Locator usernameInput = page.locator("#user-name");

        usernameInput.waitFor();

        usernameInput.fill("standard_user");

        // ─────────────────────────────────────────
        // 🔴 BROKEN PASSWORD LOCATOR
        // Correct = #password
        // ─────────────────────────────────────────

        Locator passwordInput = page.locator("#password");

        passwordInput.fill("secret_sauce");

        // ─────────────────────────────────────────
        // 🔴 BROKEN LOGIN BUTTON
        // Correct = #login-button
        // ─────────────────────────────────────────

        Locator loginButton = page.locator("#login-button");

        loginButton.click();

        // ─────────────────────────────────────────
        // Validate login success
        // ─────────────────────────────────────────

        Assertions.assertTrue(
                page.url().contains("inventory"));

        // ─────────────────────────────────────────
        // 🔴 BROKEN ADD TO CART BUTTON
        // Correct = #add-to-cart-sauce-labs-backpack
        // ─────────────────────────────────────────

        Locator addToCart = page.locator(
                "#item_4_img_link");

        addToCart.click();

        Assertions.assertTrue(
                page.url().contains("inventory"));

        System.out.println(
                "[SUCCESS] Ghost Healer Java Locator API validation passed.");
    }
}