package com.ghosthealer.core;

import org.junit.jupiter.api.extension.*;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.By;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.events.EventFiringDecorator;
import org.openqa.selenium.support.events.WebDriverListener;

import java.lang.reflect.*;
import java.net.URI;
import java.net.http.*;
import java.time.Duration;

/**
 * 👻 Ghost Healer — JUnit 5 Extension
 *
 * Automatically wraps ANY WebDriver field annotated with @GhostDriver
 * with AI self-healing. Zero changes to test logic.
 *
 * USAGE — Add ONE annotation to your BaseTest or test class:
 *
 *   @ExtendWith(GhostHealerExtension.class)
 *   public class BaseTest {
 *
 *       @GhostDriver                        // ← mark your driver field
 *       protected WebDriver driver;
 *
 *       @BeforeEach
 *       void setUp() {
 *           driver = new ChromeDriver();    // set it as usual
 *       }
 *   }
 *
 * ALL find_element / find_elements calls in every subclass test
 * are automatically self-healing — NO other changes needed.
 */
public class GhostHealerExtension
        implements BeforeTestExecutionCallback, AfterEachCallback {

    static {
        System.out.println("[GHOST] GhostHealerExtension class loaded.");
    }

    public GhostHealerExtension() {
    }

    private static final String BRAIN_URL =
        System.getenv().getOrDefault(
            "GHOST_BRAIN_URL",
            "https://ghost-healer-brain.onrender.com"
        );

    @Override
    public void beforeTestExecution(ExtensionContext context) throws Exception {
        System.out.println("[GHOST] beforeTestExecution called for: " + context.getDisplayName());
        Object testInstance = context.getRequiredTestInstance();
        wrapAnnotatedDriverFields(testInstance);
    }

    @Override
    public void afterEach(ExtensionContext context) {
        // Could finalize reporting here in future
    }

    // ── Field scanner ─────────────────────────────────────────────────────────

    private void wrapAnnotatedDriverFields(Object instance) throws Exception {
        boolean agentMode = "true".equalsIgnoreCase(
            System.getProperty("ghost.healer.agent.enabled", "false"));
        Class<?> clazz = instance.getClass();

        // Walk up the class hierarchy (covers BaseTest patterns)
        while (clazz != null && clazz != Object.class) {
            for (Field field : clazz.getDeclaredFields()) {
                boolean shouldWrap = field.isAnnotationPresent(GhostDriver.class)
                    || (agentMode && WebDriver.class.isAssignableFrom(field.getType()));
                if (shouldWrap
                        && WebDriver.class.isAssignableFrom(field.getType())) {
                    field.setAccessible(true);
                    WebDriver original = (WebDriver) field.get(instance);
                    if (original != null) {
                        WebDriver wrapped = wrap(original);
                        field.set(instance, wrapped);
                        System.out.println("[GHOST] WebDriver field '" + field.getName() + "' wrapped with AI healing.");
                    }
                }
            }
            clazz = clazz.getSuperclass();
        }
    }

    public static WebDriver wrap(WebDriver driver) {
        if (driver == null) return null;
        System.out.println("[GHOST] Wrapping driver with GhostWebDriver wrapper...");
        return new GhostWebDriver(driver);
    }
}
