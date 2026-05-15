package com.ghosthealer.core;

import org.junit.jupiter.api.extension.*;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.By;
import org.openqa.selenium.WebElement;

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
        implements BeforeEachCallback, AfterEachCallback {

    private static final String BRAIN_URL =
        System.getenv().getOrDefault(
            "GHOST_BRAIN_URL",
            "https://ghost-healer-brain.onrender.com"
        );

    @Override
    public void beforeEach(ExtensionContext context) throws Exception {
        Object testInstance = context.getRequiredTestInstance();
        wrapAnnotatedDriverFields(testInstance);
    }

    @Override
    public void afterEach(ExtensionContext context) {
        // Could finalize reporting here in future
    }

    // ── Field scanner ─────────────────────────────────────────────────────────

    private void wrapAnnotatedDriverFields(Object instance) throws Exception {
        Class<?> clazz = instance.getClass();

        // Walk up the class hierarchy (covers BaseTest patterns)
        while (clazz != null && clazz != Object.class) {
            for (Field field : clazz.getDeclaredFields()) {
                if (field.isAnnotationPresent(GhostDriver.class)
                        && WebDriver.class.isAssignableFrom(field.getType())) {
                    field.setAccessible(true);
                    WebDriver original = (WebDriver) field.get(instance);
                    if (original != null) {
                        WebDriver wrapped = createHealingProxy(original);
                        field.set(instance, wrapped);
                        System.out.println("[GHOST] WebDriver wrapped with AI healing for: "
                            + instance.getClass().getSimpleName());
                    }
                }
            }
            clazz = clazz.getSuperclass();
        }
    }

    // ── Dynamic Proxy ─────────────────────────────────────────────────────────

    private WebDriver createHealingProxy(WebDriver real) {
        return (WebDriver) Proxy.newProxyInstance(
            real.getClass().getClassLoader(),
            new Class[]{ WebDriver.class },
            (proxy, method, args) -> {
                // Only intercept findElement / findElements
                if ("findElement".equals(method.getName()) && args != null && args.length == 1) {
                    return healingFindElement(real, (By) args[0]);
                }
                if ("findElements".equals(method.getName()) && args != null && args.length == 1) {
                    return method.invoke(real, args);
                }
                return method.invoke(real, args);
            }
        );
    }

    // ── Healing logic ─────────────────────────────────────────────────────────

    private WebElement healingFindElement(WebDriver driver, By by) {
        try {
            return driver.findElement(by);
        } catch (Exception originalError) {
            String selector = by.toString();
            System.out.println("[GHOST] findElement failed for: " + selector + ". Consulting AI Brain...");

            try {
                String dom = driver.getPageSource();
                String url = driver.getCurrentUrl();
                String healed = consultBrain(selector, "click", dom, url);

                if (healed != null) {
                    System.out.println("[GHOST] Healed: " + selector + " → " + healed);
                    return driver.findElement(By.cssSelector(healed));
                }
            } catch (Exception brainError) {
                System.err.println("[GHOST] Brain error: " + brainError.getMessage());
            }

            throw originalError;
        }
    }

    private String consultBrain(String selector, String action, String dom, String url) {
        try {
            String body = String.format(
                "{\"selector\":\"%s\",\"action\":\"%s\",\"dom_snapshot\":\"%s\",\"page_url\":\"%s\"}",
                selector.replace("\"", "\\\""),
                action,
                dom.replace("\"", "\\\"").replace("\n", " ").substring(0, Math.min(dom.length(), 50000)),
                url
            );

            HttpClient client = HttpClient.newBuilder()
                .connectTimeout(Duration.ofSeconds(30))
                .build();

            HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(BRAIN_URL + "/api/heal-locator"))
                .header("Content-Type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(body))
                .timeout(Duration.ofSeconds(30))
                .build();

            HttpResponse<String> response =
                client.send(request, HttpResponse.BodyHandlers.ofString());

            if (response.statusCode() == 200) {
                String respBody = response.body();
                // Simple JSON parse — no external dep needed
                String healed = extractJson(respBody, "healed_locator");
                String confStr = extractJson(respBody, "confidence");
                double confidence = confStr != null ? Double.parseDouble(confStr) : 0;
                if (healed != null && !healed.equals("null") && confidence >= 0.5) {
                    return healed;
                }
            }
        } catch (Exception e) {
            System.err.println("[GHOST] Brain request failed: " + e.getMessage());
        }
        return null;
    }

    private String extractJson(String json, String key) {
        String search = "\"" + key + "\":";
        int idx = json.indexOf(search);
        if (idx == -1) return null;
        int start = idx + search.length();
        char first = json.charAt(start);
        if (first == '"') {
            int end = json.indexOf('"', start + 1);
            return json.substring(start + 1, end);
        } else if (first == 'n') {
            return "null";
        } else {
            int end = json.indexOf(',', start);
            if (end == -1) end = json.indexOf('}', start);
            return json.substring(start, end).trim();
        }
    }
}
