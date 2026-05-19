package com.ghosthealer.core;

import java.io.File;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

/**
 * 👻 SourceHealer — Dynamically patches Java source files on disk.
 * Walks the execution thread stack trace to locate the caller file name
 * and rewrites the file in-place to update the broken locator.
 */
public class SourceHealer {
    
    public static boolean applyFix(String oldSelector, String newSelector) {
        try {
            StackTraceElement[] stack = Thread.currentThread().getStackTrace();
            String testFileName = null;
            for (StackTraceElement element : stack) {
                String fileName = element.getFileName();
                String className = element.getClassName();
                if (fileName != null && fileName.endsWith(".java") 
                    && !className.startsWith("java.") 
                    && !className.startsWith("jdk.")
                    && !className.startsWith("com.ghosthealer.core.")
                    && !className.startsWith("com.sun.proxy")) {
                    testFileName = fileName;
                    break;
                }
            }

            if (testFileName == null) {
                System.out.println("[GHOST] [SourceHealer] Could not determine caller file from stack trace.");
                return false;
            }

            Path projectRoot = Paths.get("").toAbsolutePath();
            System.out.println("[GHOST] [SourceHealer] Searching for " + testFileName + " under " + projectRoot);
            
            final String finalName = testFileName;
            Path found = Files.walk(projectRoot)
                .filter(p -> p.getFileName().toString().equals(finalName))
                .findFirst()
                .orElse(null);

            if (found != null) {
                System.out.println("[GHOST] [SourceHealer] Found file: " + found.toAbsolutePath());
                String content = new String(Files.readAllBytes(found), StandardCharsets.UTF_8);
                
                String cleanOld = oldSelector;
                String cleanNew = newSelector;
                if (oldSelector.startsWith("#") && newSelector.startsWith("#")) {
                    cleanOld = oldSelector.substring(1);
                    cleanNew = newSelector.substring(1);
                } else if (oldSelector.startsWith(".") && newSelector.startsWith(".")) {
                    cleanOld = oldSelector.substring(1);
                    cleanNew = newSelector.substring(1);
                }

                java.util.List<String[]> optionList = new java.util.ArrayList<>();
                optionList.add(new String[]{oldSelector, newSelector});
                optionList.add(new String[]{cleanOld, cleanNew});

                if (oldSelector.startsWith("*[id=\"") && oldSelector.endsWith("\"]")) {
                    String rawId = oldSelector.substring(6, oldSelector.length() - 2);
                    String healedId = newSelector.startsWith("#") ? newSelector.substring(1) : newSelector;
                    optionList.add(new String[]{rawId, healedId});
                }
                if (oldSelector.startsWith("*[class=\"") && oldSelector.endsWith("\"]")) {
                    String rawClass = oldSelector.substring(9, oldSelector.length() - 2);
                    String healedClass = newSelector.startsWith(".") ? newSelector.substring(1) : newSelector;
                    optionList.add(new String[]{rawClass, healedClass});
                }

                boolean patched = false;
                for (String[] opt : optionList) {
                    String o = opt[0];
                    String n = opt[1];
                    String pattern1 = "\"" + o + "\"";
                    String replace1 = "\"" + n + "\"";
                    String pattern2 = "'" + o + "'";
                    String replace2 = "'" + n + "'";

                    if (content.contains(pattern1)) {
                        content = content.replace(pattern1, replace1);
                        patched = true;
                    } else if (content.contains(pattern2)) {
                        content = content.replace(pattern2, replace2);
                        patched = true;
                    } else if (content.contains(o)) {
                        content = content.replace(o, n);
                        patched = true;
                    }
                    
                    if (patched) {
                        Files.write(found, content.getBytes(StandardCharsets.UTF_8));
                        System.out.printf("[GHOST] ✅ Permanently patched: %s ('%s' -> '%s')%n", 
                            found.getFileName(), oldSelector, newSelector);
                        return true;
                    }
                }
                System.out.println("[GHOST] [SourceHealer] Selector '" + oldSelector + "' not found in file content.");
                }
            } else {
                System.out.println("[GHOST] [SourceHealer] File " + testFileName + " not found on disk.");
            }
        } catch (Exception e) {
            System.out.println("[GHOST] [SourceHealer] Patching failed: " + e.getMessage());
        }
        return false;
    }
}
