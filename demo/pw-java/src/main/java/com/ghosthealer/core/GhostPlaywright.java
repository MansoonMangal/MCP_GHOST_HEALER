package com.ghosthealer.core;

import com.microsoft.playwright.*;
import java.lang.reflect.*;
import java.net.URI;
import java.net.http.*;
import java.time.Duration;

/**
 * 👻 Ghost Healer — Playwright Java Support (Phase 11)
 *
 * Wraps a Playwright Page AND all nested Locators with AI self-healing using Dynamic Proxies.
 * Synchronized with IST logs and prepends to both global suggested-fixes.json and session_*.json audit trails.
 */
public class GhostPlaywright {

    private static final String BRAIN_URL =
        System.getenv().getOrDefault(
            "GHOST_BRAIN_URL",
            "https://ghost-healer-brain.onrender.com"
        );
    private static final double CONFIDENCE_THRESHOLD = 0.5;
    private static final int MAX_RETRIES = 3;
    
    private static final String SESSION_ID = java.time.LocalDateTime.now()
        .format(java.time.format.DateTimeFormatter.ofPattern("yyyyMMdd_HHmmss"));

    public static Page protect(Page realPage) {
        return (Page) Proxy.newProxyInstance(
            realPage.getClass().getClassLoader(),
            new Class[]{ Page.class },
            new HealingPageHandler(realPage)
        );
    }

    public static Locator protectLocator(Locator realLocator, String selector, Page realPage) {
        return (Locator) Proxy.newProxyInstance(
            realLocator.getClass().getClassLoader(),
            new Class[]{ Locator.class },
            new HealingLocatorHandler(realLocator, selector, realPage)
        );
    }

    // ── Shared Helper Methods ─────────────────────────────────────────────────

    public static String consultBrain(Page page, String selector, String action) {
        String dom = page.content();
        String url = page.url();
        long startTime = System.currentTimeMillis();

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
                    if (confStr == null || confStr.equals("null")) {
                        confStr = extractJson(resp.body(), "confidence_score");
                    }
                    double conf = confStr != null ? Double.parseDouble(confStr) : 0.0;
                    if (conf > 1.0) {
                        conf = conf / 100.0;
                    }
                    if (healed != null && !healed.equals("null") && conf >= CONFIDENCE_THRESHOLD) {
                        long latencyMs = System.currentTimeMillis() - startTime;
                        handleHealingEvent(page, selector, healed, action, conf, latencyMs);
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

    private static void handleHealingEvent(Page page, String oldSelector, String newSelector, String action, double confidence, long latencyMs) {
        try {
            StackTraceElement[] stack = Thread.currentThread().getStackTrace();
            String testFileName = null;
            int lineNo = 0;
            for (StackTraceElement element : stack) {
                String fileName = element.getFileName();
                String className = element.getClassName();
                if (fileName != null && fileName.endsWith(".java") 
                    && !className.startsWith("java.") 
                    && !className.startsWith("jdk.")
                    && !className.startsWith("com.ghosthealer.core.GhostPlaywright")) {
                    testFileName = fileName;
                    lineNo = element.getLineNumber();
                    break;
                }
            }

            String absolutePath = null;
            if (testFileName != null) {
                java.nio.file.Path projectRoot = java.nio.file.Paths.get("").toAbsolutePath();
                while (projectRoot != null && !java.nio.file.Files.exists(projectRoot.resolve("ghost.yaml"))) {
                    projectRoot = projectRoot.getParent();
                }
                if (projectRoot == null) {
                    projectRoot = java.nio.file.Paths.get("").toAbsolutePath();
                }

                final String finalName = testFileName;
                java.nio.file.Path found = java.nio.file.Files.walk(projectRoot)
                    .filter(p -> p.getFileName().toString().equals(finalName))
                    .findFirst()
                    .orElse(null);

                if (found != null) {
                    absolutePath = found.toAbsolutePath().toString();
                    String content = new String(java.nio.file.Files.readAllBytes(found), java.nio.charset.StandardCharsets.UTF_8);
                    
                    String pattern1 = "\"" + oldSelector + "\"";
                    String replace1 = "\"" + newSelector + "\"";
                    String pattern2 = "'" + oldSelector + "'";
                    String replace2 = "'" + newSelector + "'";
                    
                    boolean changed = false;
                    if (content.contains(pattern1)) {
                        content = content.replace(pattern1, replace1);
                        changed = true;
                    } else if (content.contains(pattern2)) {
                        content = content.replace(pattern2, replace2);
                        changed = true;
                    }

                    if (changed) {
                        java.nio.file.Files.write(found, content.getBytes(java.nio.charset.StandardCharsets.UTF_8));
                        System.out.printf("[GHOST] ✅ Permanently patched: %s ('%s' -> '%s')%n", 
                            found.getFileName(), oldSelector, newSelector);
                    } else {
                        System.out.printf("[GHOST] [SourceHealer] Selector '%s' not found in %s%n", 
                            oldSelector, found.getFileName());
                    }
                }
            }
            
            writeToReport(oldSelector, newSelector, action, absolutePath != null ? absolutePath : testFileName, lineNo, page.url(), confidence, latencyMs);

        } catch (Exception e) {
            System.out.println("[GHOST] [SourceHealer] Patching/Reporting failed: " + e.getMessage());
        }
    }

    public static void writeToReport(String oldSelector, String newSelector, String action, String filePath, int lineNo, String pageUrl, double confidence, long latencyMs) {
        try {
            java.nio.file.Path rootDir = java.nio.file.Paths.get("").toAbsolutePath();
            while (rootDir != null && !java.nio.file.Files.exists(rootDir.resolve("ghost.yaml"))) {
                rootDir = rootDir.getParent();
            }
            if (rootDir == null) {
                rootDir = java.nio.file.Paths.get("").toAbsolutePath();
            }
            
            java.nio.file.Path reportDir = rootDir.resolve("reports").resolve("ghost");
            java.nio.file.Files.createDirectories(reportDir);
            
            // 1. Write to global suggested-fixes.json
            java.nio.file.Path reportFile = reportDir.resolve("suggested-fixes.json");
            String content = "[]";
            if (java.nio.file.Files.exists(reportFile)) {
                content = new String(java.nio.file.Files.readAllBytes(reportFile), java.nio.charset.StandardCharsets.UTF_8);
            }
            
            java.time.ZonedDateTime nowIST = java.time.ZonedDateTime.now(java.time.ZoneId.of("Asia/Kolkata"));
            String timestamp = nowIST.format(java.time.format.DateTimeFormatter.ISO_OFFSET_DATE_TIME);
            
            String escapedFilePath = filePath != null ? filePath.replace("\\", "\\\\") : null;

            String newEntryGlobal = String.format(
                "  {\n" +
                "    \"timestamp\": \"%s\",\n" +
                "    \"framework\": \"playwright\",\n" +
                "    \"language\": \"java\",\n" +
                "    \"file\": %s,\n" +
                "    \"line\": %s,\n" +
                "    \"action\": \"%s\",\n" +
                "    \"old_locator\": \"%s\",\n" +
                "    \"suggested_locator\": \"%s\",\n" +
                "    \"confidence\": %.4f,\n" +
                "    \"page_url\": \"%s\"\n" +
                "  }",
                timestamp,
                escapedFilePath != null ? "\"" + escapedFilePath + "\"" : "null",
                lineNo > 0 ? String.valueOf(lineNo) : "null",
                action,
                escape(oldSelector),
                escape(newSelector),
                confidence,
                escape(pageUrl)
            );
            
            content = content.trim();
            if (content.equals("[]") || content.isEmpty()) {
                content = "[\n" + newEntryGlobal + "\n]";
            } else if (content.startsWith("[") && content.endsWith("]")) {
                String inside = content.substring(1, content.length() - 1).trim();
                if (inside.isEmpty()) {
                    content = "[\n" + newEntryGlobal + "\n]";
                } else {
                    content = "[\n" + newEntryGlobal + ",\n" + inside + "\n]";
                }
            }
            
            java.nio.file.Files.write(reportFile, content.getBytes(java.nio.charset.StandardCharsets.UTF_8));
            System.out.printf("[GHOST] 📄 Logged suggestion to global report: %s%n", reportFile.getFileName());

            // 2. Write to session_<session_id>.json
            java.nio.file.Path sessionFile = reportDir.resolve("session_" + SESSION_ID + ".json");
            String sessionContent = "[]";
            if (java.nio.file.Files.exists(sessionFile)) {
                sessionContent = new String(java.nio.file.Files.readAllBytes(sessionFile), java.nio.charset.StandardCharsets.UTF_8);
            }

            String newEntrySession = String.format(
                "  {\n" +
                "    \"timestamp\": \"%s\",\n" +
                "    \"session_id\": \"%s\",\n" +
                "    \"framework\": \"playwright-java\",\n" +
                "    \"language\": \"java\",\n" +
                "    \"file\": %s,\n" +
                "    \"line\": %s,\n" +
                "    \"action\": \"%s\",\n" +
                "    \"old_locator\": \"%s\",\n" +
                "    \"suggested_locator\": \"%s\",\n" +
                "    \"confidence\": %.4f,\n" +
                "    \"page_url\": \"%s\",\n" +
                "    \"decision\": \"AUTO_HEAL\",\n" +
                "    \"latency_ms\": %.2f,\n" +
                "    \"retry_count\": 0,\n" +
                "    \"healing_mode\": \"runtime\"\n" +
                "  }",
                timestamp,
                SESSION_ID,
                escapedFilePath != null ? "\"" + escapedFilePath + "\"" : "null",
                lineNo > 0 ? String.valueOf(lineNo) : "null",
                action,
                escape(oldSelector),
                escape(newSelector),
                confidence,
                escape(pageUrl),
                (double) latencyMs
            );

            sessionContent = sessionContent.trim();
            if (sessionContent.equals("[]") || sessionContent.isEmpty()) {
                sessionContent = "[\n" + newEntrySession + "\n]";
            } else if (sessionContent.startsWith("[") && sessionContent.endsWith("]")) {
                String inside = sessionContent.substring(1, sessionContent.length() - 1).trim();
                if (inside.isEmpty()) {
                    sessionContent = "[\n" + newEntrySession + "\n]";
                } else {
                    sessionContent = "[\n" + newEntrySession + ",\n" + inside + "\n]";
                }
            }
            java.nio.file.Files.write(sessionFile, sessionContent.getBytes(java.nio.charset.StandardCharsets.UTF_8));
            System.out.printf("[GHOST] 📂 Logged session details to audit trail: %s%n", sessionFile.getFileName());

        } catch (Exception e) {
            System.out.println("[GHOST] Failed to write report files: " + e.getMessage());
        }
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
        while (start < json.length() && Character.isWhitespace(json.charAt(start))) start++;
        
        if (start >= json.length()) return null;
        
        char first = json.charAt(start);
        if (first == '"') {
            int end = json.indexOf('"', start + 1);
            return end > start ? json.substring(start + 1, end) : null;
        } else if (first == 'n') {
            return "null";
        } else {
            int end = start;
            while (end < json.length() && 
                   json.charAt(end) != ',' && 
                   json.charAt(end) != '}' && 
                   json.charAt(end) != ']') {
                end++;
            }
            return end > start ? json.substring(start, end).trim() : null;
        }
    }

    // ── Invocation Handlers ──────────────────────────────────────────────────

    static class HealingPageHandler implements InvocationHandler {
        private final Page real;

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

            if ("locator".equals(methodName)
                    && args != null
                    && args.length > 0
                    && args[0] instanceof String) {
                String selector = (String) args[0];
                try {
                    Locator realLocator = (Locator) method.invoke(real, args);
                    return protectLocator(realLocator, selector, real);
                } catch (InvocationTargetException e) {
                    throw e.getCause() != null ? e.getCause() : e;
                }
            }

            if (HEALABLE_METHODS.contains(methodName)
                    && args != null
                    && args.length > 0
                    && args[0] instanceof String) {

                String selector = (String) args[0];

                try {
                    return method.invoke(real, args);
                } catch (InvocationTargetException e) {
                    Throwable cause = e.getCause();
                    System.out.printf("[GHOST] page.%s('%s') failed. Consulting AI Brain...%n",
                        methodName, selector);

                    String healed = consultBrain(real, selector, methodName);
                    if (healed != null) {
                        System.out.printf("[GHOST] Healed '%s' → '%s'%n", selector, healed);
                        Object[] healedArgs = args.clone();
                        healedArgs[0] = healed;
                        return method.invoke(real, healedArgs);
                    }

                    throw cause != null ? cause : e;
                }
            }

            try {
                return method.invoke(real, args);
            } catch (InvocationTargetException e) {
                throw e.getCause() != null ? e.getCause() : e;
            }
        }
    }

    static class HealingLocatorHandler implements InvocationHandler {
        private final Locator real;
        private final String selector;
        private final Page page;

        private static final java.util.Set<String> HEALABLE_METHODS = new java.util.HashSet<>(
            java.util.Arrays.asList(
                "click", "fill", "hover", "check", "uncheck",
                "dblclick", "tap", "selectOption", "press",
                "waitFor", "isVisible", "isEnabled",
                "getAttribute", "textContent", "innerText"
            )
        );

        HealingLocatorHandler(Locator real, String selector, Page page) {
            this.real = real;
            this.selector = selector;
            this.page = page;
        }

        @Override
        public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {
            String methodName = method.getName();

            if (HEALABLE_METHODS.contains(methodName)) {
                try {
                    return method.invoke(real, args);
                } catch (InvocationTargetException e) {
                    Throwable cause = e.getCause();
                    System.out.printf("[GHOST] locator.%s('%s') failed. Consulting AI Brain...%n",
                        methodName, selector);

                    String healed = consultBrain(page, selector, methodName);
                    if (healed != null) {
                        System.out.printf("[GHOST] Healed locator '%s' → '%s'%n", selector, healed);
                        Locator healedLocator = page.locator(healed);
                        return method.invoke(healedLocator, args);
                    }

                    throw cause != null ? cause : e;
                }
            }

            try {
                return method.invoke(real, args);
            } catch (InvocationTargetException e) {
                throw e.getCause() != null ? e.getCause() : e;
            }
        }
    }
}
