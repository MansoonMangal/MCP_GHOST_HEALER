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
 * with a dynamic proxy for active AI self-healing interceptors.
 */
public class GhostHealerExtension
        implements BeforeTestExecutionCallback, AfterEachCallback {

    private static final String BRAIN_URL =
        System.getenv().getOrDefault(
            "GHOST_BRAIN_URL",
            "http://localhost:8000"
        );
        
    private static final String SESSION_ID = java.time.LocalDateTime.now()
        .format(java.time.format.DateTimeFormatter.ofPattern("yyyyMMdd_HHmmss"));

    static {
        System.out.println("[GHOST] GhostHealerExtension class loaded.");
    }

    public GhostHealerExtension() {
    }

    @Override
    public void beforeTestExecution(ExtensionContext context) throws Exception {
        System.out.println("[GHOST] beforeTestExecution called for: " + context.getDisplayName());
        Object testInstance = context.getRequiredTestInstance();
        wrapAnnotatedDriverFields(testInstance);
    }

    @Override
    public void afterEach(ExtensionContext context) {
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
                        System.out.println("[GHOST] WebDriver field '" + field.getName() + "' wrapped with active dynamic proxy.");
                    }
                }
            }
            clazz = clazz.getSuperclass();
        }
    }

    public static WebDriver wrap(WebDriver driver) {
        if (driver == null) return null;
        
        java.util.Set<Class<?>> interfaces = new java.util.HashSet<>();
        Class<?> clazz = driver.getClass();
        while (clazz != null) {
            for (Class<?> iface : clazz.getInterfaces()) {
                interfaces.add(iface);
            }
            clazz = clazz.getSuperclass();
        }
        
        System.out.println("[GHOST] Wrapping driver with active dynamic healing proxy...");
        return (WebDriver) Proxy.newProxyInstance(
            driver.getClass().getClassLoader(),
            interfaces.toArray(new Class<?>[0]),
            new HealingDriverHandler(driver)
        );
    }

    static class HealingDriverHandler implements InvocationHandler {
        private final WebDriver realDriver;
        private final GhostHealerExtension healer = new GhostHealerExtension();

        HealingDriverHandler(WebDriver realDriver) {
            this.realDriver = realDriver;
        }

        @Override
        public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {
            String methodName = method.getName();

            if ("findElement".equals(methodName) && args != null && args.length == 1 && args[0] instanceof By) {
                By by = (By) args[0];
                try {
                    return method.invoke(realDriver, args);
                } catch (InvocationTargetException e) {
                    Throwable cause = e.getCause();
                    if (cause != null && cause.getClass().getName().contains("NoSuchElementException")) {
                        System.out.printf("[GHOST] driver.findElement(%s) failed. Consulting AI Brain...%n", by);
                        WebElement healed = healer.healingFindElement(realDriver, by);
                        if (healed != null) {
                            return healed;
                        }
                    }
                    throw cause != null ? cause : e;
                }
            }

            try {
                return method.invoke(realDriver, args);
            } catch (InvocationTargetException e) {
                throw e.getCause() != null ? e.getCause() : e;
            }
        }
    }

    // ── Healing logic ─────────────────────────────────────────────────────────

    private String getNormalizedSelector(By by) {
        String selectorStr = by.toString();
        if (selectorStr.startsWith("By.id: ")) {
            return "#" + selectorStr.substring(7);
        }
        if (selectorStr.startsWith("By.className: ")) {
            return "." + selectorStr.substring(14);
        }
        if (selectorStr.startsWith("By.name: ")) {
            return "[name='" + selectorStr.substring(9) + "']";
        }
        if (selectorStr.startsWith("By.tagName: ")) {
            return selectorStr.substring(12);
        }
        if (selectorStr.contains(": ")) {
            return selectorStr.substring(selectorStr.indexOf(": ") + 2);
        }
        return selectorStr;
    }

    public WebElement healingFindElement(WebDriver driver, By by) {
        String selectorStr = by.toString();
        String originalRawValue = selectorStr;
        if (selectorStr.contains(": ")) {
            originalRawValue = selectorStr.substring(selectorStr.indexOf(": ") + 2);
        }
        
        String normalizedSelector = getNormalizedSelector(by);
        System.out.printf("[GHOST] Normalized selector for AI: %s -> %s%n", selectorStr, normalizedSelector);
        
        try {
            String dom = driver.getPageSource();
            String url = driver.getCurrentUrl();
            long startTime = System.currentTimeMillis();
            HealedInfo healed = consultBrain(normalizedSelector, "find", dom, url);

            if (healed != null) {
                long latencyMs = System.currentTimeMillis() - startTime;
                System.out.println("[GHOST] Healed: " + normalizedSelector + " → " + healed.healedLocator);
                
                String patchedOld = originalRawValue;
                String patchedNew = healed.healedLocator;
                if (selectorStr.startsWith("By.id: ") && patchedNew.startsWith("#")) {
                    patchedNew = patchedNew.substring(1);
                } else if (selectorStr.startsWith("By.className: ") && patchedNew.startsWith(".")) {
                    patchedNew = patchedNew.substring(1);
                }
                
                String absolutePath = applySourcePatch(patchedOld, patchedNew);
                
                writeToReport(driver, originalRawValue, healed.healedLocator, "click", absolutePath, url, healed.confidence, latencyMs);
                
                return driver.findElement(By.cssSelector(healed.healedLocator));
            }
        } catch (Exception brainError) {
            System.err.println("[GHOST] Brain error: " + brainError.getMessage());
        }
        return null;
    }

    private String applySourcePatch(String oldSelector, String newSelector) {
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
                return null;
            }

            java.nio.file.Path projectRoot = java.nio.file.Paths.get("").toAbsolutePath();
            while (projectRoot != null && !java.nio.file.Files.exists(projectRoot.resolve("ghost.yaml"))) {
                projectRoot = projectRoot.getParent();
            }
            if (projectRoot == null) {
                projectRoot = java.nio.file.Paths.get("").toAbsolutePath();
            }

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
                    System.out.println("[GHOST] [SourceHealer] Selector not found in file content.");
                }
                return found.toAbsolutePath().toString();
            } else {
                System.out.println("[GHOST] [SourceHealer] File " + testFileName + " not found on disk.");
            }
        } catch (Exception e) {
            System.out.println("[GHOST] [SourceHealer] Patching failed: " + e.getMessage());
        }
        return null;
    }

    private void writeToReport(WebDriver driver, String oldSelector, String newSelector, String action, String filePath, String pageUrl, double confidence, long latencyMs) {
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
            
            StackTraceElement[] stack = Thread.currentThread().getStackTrace();
            String testFileName = null;
            int lineNo = 0;
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
                    lineNo = element.getLineNumber();
                    break;
                }
            }

            // 1. Write to global suggested-fixes.json
            java.nio.file.Path reportFile = reportDir.resolve("suggested-fixes.json");
            String content = "[]";
            if (java.nio.file.Files.exists(reportFile)) {
                content = new String(java.nio.file.Files.readAllBytes(reportFile), java.nio.charset.StandardCharsets.UTF_8);
            }
            
            java.time.ZonedDateTime nowIST = java.time.ZonedDateTime.now(java.time.ZoneId.of("Asia/Kolkata"));
            String timestamp = nowIST.format(java.time.format.DateTimeFormatter.ISO_OFFSET_DATE_TIME);
            
            String escapedFilePath = filePath != null ? filePath.replace("\\", "\\\\") : (testFileName != null ? testFileName : "null");

            String newEntryGlobal = String.format(
                "  {\n" +
                "    \"timestamp\": \"%s\",\n" +
                "    \"framework\": \"selenium\",\n" +
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
                "\"" + escapedFilePath + "\"",
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
                "    \"framework\": \"selenium-java\",\n" +
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
                "\"" + escapedFilePath + "\"",
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

    private static class HealedInfo {
        String healedLocator;
        double confidence;
        HealedInfo(String healedLocator, double confidence) {
            this.healedLocator = healedLocator;
            this.confidence = confidence;
        }
    }

    private HealedInfo consultBrain(String selector, String action, String dom, String url) {
        try {
            String body = String.format(
                "{\"selector\":\"%s\",\"action\":\"%s\",\"dom_snapshot\":\"%s\",\"page_url\":\"%s\"}",
                escape(selector),
                action,
                escape(dom.length() > 50000 ? dom.substring(0, 50000) : dom),
                escape(url)
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
                if (confStr == null || confStr.equals("null")) {
                    confStr = extractJson(respBody, "confidence_score");
                }
                double confidence = confStr != null ? Double.parseDouble(confStr) : 0.0;
                if (confidence > 1.0) {
                    confidence = confidence / 100.0;
                }
                if (healed != null && !healed.equals("null") && confidence >= 0.5) {
                    return new HealedInfo(healed, confidence);
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
