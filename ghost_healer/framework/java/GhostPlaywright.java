package com.ghosthealer.core;

import com.microsoft.playwright.*;
import java.lang.reflect.*;
import java.net.URI;
import java.net.http.*;
import java.time.Duration;

/**
 * 👻 Ghost Healer — Playwright Java Support
 *
 * Wraps a Playwright Page with AI self-healing using Java Dynamic Proxy.
 *
 * MINIMUM CHANGE — ONE LINE where you create the page:
 *
 *   // Before:
 *   Page page = context.newPage();
 *
 *   // After (only change):
 *   Page page = GhostPlaywright.protect(context.newPage());
 *
 * All page.click(), page.fill(), page.hover() etc. automatically
 * self-heal broken selectors. Zero other changes needed.
 *
 * OR for BaseTest pattern (ONE change covers all tests):
 *
 *   public abstract class BaseTest {
 *       protected Page page;
 *
 *       @BeforeEach
 *       void setUp() {
 *           Browser browser = playwright.chromium().launch();
 *           BrowserContext ctx = browser.newContext();
 *           page = GhostPlaywright.protect(ctx.newPage()); // ← only change
 *       }
 *   }
 */
public class GhostPlaywright {

    private static final String BRAIN_URL =
        System.getenv().getOrDefault(
            "GHOST_BRAIN_URL",
            "https://ghost-healer-brain.onrender.com"
        );
    private static final double CONFIDENCE_THRESHOLD = 0.5;
    private static final int MAX_RETRIES = 3;

    /**
     * Wrap a Playwright Page with AI self-healing.
     * Returns a proxied Page — all method calls are intercepted.
     */
    public static Page protect(Page realPage) {
        return (Page) Proxy.newProxyInstance(
            realPage.getClass().getClassLoader(),
            new Class[]{ Page.class },
            new HealingPageHandler(realPage)
        );
    }

    // ── Invocation handler ────────────────────────────────────────────────────

    static class HealingPageHandler implements InvocationHandler {

        private final Page real;

        // Methods that take a selector as first argument
        private static final java.util.Set<String> HEALABLE_METHODS = new java.util.HashSet<>(
            java.util.Arrays.asList(
                "click", "fill", "hover", "check", "uncheck",
                "dblclick", "tap", "selectOption", "press",
                "waitForSelector", "isVisible", "isEnabled",
                "getAttribute", "textContent", "innerText"
            )
        );

        HealingPageHandler(Page real) {
            this.real = real;
        }

        @Override
        public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {
            String methodName = method.getName();

            // Only intercept healable methods that have a selector as first arg
            if (HEALABLE_METHODS.contains(methodName)
                    && args != null
                    && args.length > 0
                    && args[0] instanceof String) {

                String selector = (String) args[0];

                try {
                    return method.invoke(real, args);
                } catch (InvocationTargetException e) {
                    Throwable cause = e.getCause();
                    System.out.printf("[GHOST] %s('%s') failed. Consulting AI Brain...%n",
                        methodName, selector);

                    String healed = consultBrain(selector, methodName);
                    if (healed != null) {
                        System.out.printf("[GHOST] Healed '%s' → '%s'%n", selector, healed);
                        Object[] healedArgs = args.clone();
                        healedArgs[0] = healed;
                        return method.invoke(real, healedArgs);
                    }

                    throw cause != null ? cause : e;
                }
            }

            // Passthrough for non-selector methods
            try {
                return method.invoke(real, args);
            } catch (InvocationTargetException e) {
                throw e.getCause() != null ? e.getCause() : e;
            }
        }

        private String consultBrain(String selector, String action) {
            String dom = real.content();
            String url = real.url();

            for (int attempt = 0; attempt < MAX_RETRIES; attempt++) {
                try {
                    String body = String.format(
                        "{\"selector\":\"%s\",\"action\":\"%s\",\"dom_snapshot\":\"%s\",\"page_url\":\"%s\"}",
                        escape(selector), action,
                        escape(dom.length() > 50000 ? dom.substring(0, 50000) : dom),
                        escape(url)
                    );

                    HttpClient client = HttpClient.newBuilder()
                        .connectTimeout(Duration.ofSeconds(10))
                        .build();

                    HttpRequest req = HttpRequest.newBuilder()
                        .uri(URI.create(BRAIN_URL + "/api/heal-locator"))
                        .header("Content-Type", "application/json")
                        .POST(HttpRequest.BodyPublishers.ofString(body))
                        .timeout(Duration.ofSeconds(30))
                        .build();

                    HttpResponse<String> resp =
                        client.send(req, HttpResponse.BodyHandlers.ofString());

                    if (resp.statusCode() == 200) {
                        String healed = extractJson(resp.body(), "healed_locator");
                        String confStr = extractJson(resp.body(), "confidence");
                        double conf = confStr != null ? Double.parseDouble(confStr) : 0;
                        if (healed != null && !healed.equals("null") && conf >= CONFIDENCE_THRESHOLD) {
                            return healed;
                        }
                    }
                } catch (Exception e) {
                    int wait = (attempt + 1) * 5;
                    System.out.printf("[GHOST] Brain unreachable. Retrying in %ds...%n", wait);
                    try { Thread.sleep(wait * 1000L); } catch (InterruptedException ignored) {}
                }
            }
            return null;
        }

        private static String escape(String s) {
            return s.replace("\\", "\\\\").replace("\"", "\\\"")
                    .replace("\n", " ").replace("\r", "");
        }

        private static String extractJson(String json, String key) {
            String search = "\"" + key + "\":";
            int idx = json.indexOf(search);
            if (idx == -1) return null;
            int start = idx + search.length();
            char first = json.charAt(start);
            if (first == '"') {
                int end = json.indexOf('"', start + 1);
                return end > start ? json.substring(start + 1, end) : null;
            } else if (first == 'n') {
                return "null";
            } else {
                int end = Math.max(json.indexOf(',', start), json.indexOf('}', start));
                return end > start ? json.substring(start, end).trim() : null;
            }
        }
    }
}
