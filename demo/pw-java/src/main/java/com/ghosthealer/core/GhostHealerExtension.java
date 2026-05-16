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
        Class<?> clazz = instance.getClass();

        // Walk up the class hierarchy (covers BaseTest patterns)
        while (clazz != null && clazz != Object.class) {
            for (Field field : clazz.getDeclaredFields()) {
                if (field.isAnnotationPresent(GhostDriver.class)
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
        System.out.println("[GHOST] Wrapping driver with WebDriverListener...");
        return new EventFiringDecorator<>(new GhostListener(driver)).decorate(driver);
    }

    private static class GhostListener implements WebDriverListener {
        private final WebDriver driver;
        private final GhostHealerExtension healer = new GhostHealerExtension();

        public GhostListener(WebDriver driver) {
            this.driver = driver;
        }

        @Override
        public void onError(Object target, Method method, Object[] args, InvocationTargetException e) {
            Throwable cause = e.getCause();
            String msg = "[GHOST] onError: " + method.getName();
            if (cause != null) msg += " threw " + cause.getClass().getName();
            
            try {
                java.nio.file.Files.write(java.nio.file.Paths.get("ghost_debug.txt"), 
                    (msg + "\n").getBytes(), 
                    java.nio.file.StandardOpenOption.CREATE, 
                    java.nio.file.StandardOpenOption.APPEND);
            } catch (Exception ex) {}

            if (cause != null && cause.getClass().getName().contains("NoSuchElementException")) {
                if ("findElement".equals(method.getName()) && args != null && args.length == 1) {
                    By by = (By) args[0];
                    healer.healingFindElement(driver, by); // Trigger healing
                }
            }
        }
    }

    // ── Healing logic ─────────────────────────────────────────────────────────

    private WebElement healingFindElement(WebDriver driver, By by) {
        try {
            return driver.findElement(by);
        } catch (Exception originalError) {
            String selectorStr = by.toString();
            // Handle By.id: iron -> iron
            String rawSelector = selectorStr;
            if (selectorStr.contains(": ")) {
                rawSelector = selectorStr.substring(selectorStr.indexOf(": ") + 2);
            }
            
            System.out.println("[GHOST] findElement failed for: " + selectorStr + ". Consulting AI Brain...");

            try {
                String dom = driver.getPageSource();
                String url = driver.getCurrentUrl();
                String healed = consultBrain(rawSelector, "click", dom, url);

                if (healed != null) {
                    System.out.println("[GHOST] Healed: " + rawSelector + " → " + healed);
                    applySourcePatch(rawSelector, healed);
                    return driver.findElement(By.cssSelector(healed));
                }
            } catch (Exception brainError) {
                System.err.println("[GHOST] Brain error: " + brainError.getMessage());
            }

            throw originalError;
        }
    }

    private void applySourcePatch(String oldSelector, String newSelector) {
        try {
            StackTraceElement[] stack = Thread.currentThread().getStackTrace();
            String testFileName = null;
            for (StackTraceElement element : stack) {
                String fileName = element.getFileName();
                String className = element.getClassName();
                if (fileName != null && fileName.endsWith(".java") 
                    && !className.startsWith("java.") 
                    && !className.startsWith("jdk.")
                    && !className.startsWith("com.ghosthealer.core.GhostHealerExtension")
                    && !className.startsWith("com.ghosthealer.core.GhostDriver")
                    && !className.startsWith("com.sun.proxy")) {
                    testFileName = fileName;
                    break;
                }
            }

            if (testFileName == null) {
                System.out.println("[GHOST] [SourceHealer] Could not determine test file from stack trace.");
                return;
            }

            java.nio.file.Path projectRoot = java.nio.file.Paths.get("").toAbsolutePath();
            System.out.println("[GHOST] [SourceHealer] Searching for " + testFileName + " in " + projectRoot);
            final String finalName = testFileName;
            java.nio.file.Path found = java.nio.file.Files.walk(projectRoot)
                .filter(p -> p.getFileName().toString().equals(finalName))
                .findFirst()
                .orElse(null);

            if (found != null) {
                System.out.println("[GHOST] [SourceHealer] Found file: " + found.toAbsolutePath());
                String content = new String(java.nio.file.Files.readAllBytes(found), java.nio.charset.StandardCharsets.UTF_8);
                String pattern1 = "\"" + oldSelector + "\"";
                String replace1 = "\"" + newSelector + "\"";
                
                if (content.contains(pattern1)) {
                    content = content.replace(pattern1, replace1);
                    java.nio.file.Files.write(found, content.getBytes(java.nio.charset.StandardCharsets.UTF_8));
                    System.out.printf("[GHOST] ✅ Permanently patched: %s ('%s' -> '%s')%n", 
                        found.getFileName(), oldSelector, newSelector);
                } else {
                    System.out.println("[GHOST] [SourceHealer] Pattern " + pattern1 + " not found in file content.");
                }
            } else {
                System.out.println("[GHOST] [SourceHealer] File " + testFileName + " not found on disk.");
            }
        } catch (Exception e) {
            System.out.println("[GHOST] [SourceHealer] Patching failed: " + e.getMessage());
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
                String healed = extractJson(respBody, "healed_locator");
                String confStr = extractJson(respBody, "confidence");
                double confidence = confStr != null ? Double.parseDouble(confStr) : 0;
                if (healed != null && !healed.equals("null") && confidence >= 0.0) {
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
        while (start < json.length() && Character.isWhitespace(json.charAt(start))) start++;
        if (start >= json.length()) return null;
        char first = json.charAt(start);
        if (first == '"') {
            int end = json.indexOf('"', start + 1);
            return json.substring(start + 1, end);
        } else if (first == 'n') {
            return "null";
        } else {
            int end = start;
            while (end < json.length() && json.charAt(end) != ',' && json.charAt(end) != '}' && json.charAt(end) != ']') end++;
            return json.substring(start, end).trim();
        }
    }
}
