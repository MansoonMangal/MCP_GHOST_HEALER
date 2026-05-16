package demo;

import com.microsoft.playwright.*;
import com.ghosthealer.core.GhostPlaywright;
import org.junit.jupiter.api.*;

/**
 * 👻 Ghost Healer Demo — Playwright Java
 *
 * ONE CHANGE in BaseTest: GhostPlaywright.protect(page)
 * Every test that extends BaseTest gets AI healing automatically.
 *
 * Run: mvn test -Dtest=PlaywrightJavaDemo
 */
public class PlaywrightJavaDemo {

    // ── Base setup (ONE change covers ALL tests) ───────────────────────────────
    static Playwright playwright;
    static Browser browser;
    static BrowserContext context;
    Page page;

    @BeforeAll
    static void launchBrowser() {
        playwright = Playwright.create();
        browser = playwright.chromium().launch(
                new BrowserType.LaunchOptions().setHeadless(false));
    }

    @BeforeEach
    void setUp() {
        context = browser.newContext();
        // ← ONE LINE CHANGE: wrap with GhostPlaywright
        page = GhostPlaywright.protect(context.newPage());
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

    // ── Test (ZERO changes — standard Playwright Java API) ────────────────────

    @Test
    @DisplayName("Login with broken selectors — Ghost heals them")
    void testLoginWithBrokenLocators() {
        page.navigate("https://www.saucedemo.com/");

        // Standard Playwright Java API — broken selectors, Ghost heals silently
        page.fill("#login-button", "standard_user");
        page.fill("#man", "secret_sauce");

        // Correct login button
        page.click("#login-button-WRONG");

        Assertions.assertTrue(page.url().contains("inventory"));

        // 🔴 BROKEN: correct is #add-to-cart-sauce-labs-backpack
        page.click("#item_4_img_link");

        Assertions.assertTrue(page.url().contains("inventory"));
        System.out.println("[SUCCESS] PW + Java: Passed with one-line change in setUp!");
    }
}
