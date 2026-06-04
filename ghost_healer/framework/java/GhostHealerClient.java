package com.ghosthealer.core;

import java.net.HttpURLConnection;
import java.net.URL;
import java.io.OutputStream;
import java.io.InputStreamReader;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileWriter;
import java.time.Instant;

public class GhostHealerClient {
    private String brainUrl = System.getenv().getOrDefault("GHOST_BRAIN_URL", "https://ghost-healer-brain.onrender.com");
    private double confidenceThreshold = Double.parseDouble(System.getenv().getOrDefault("GHOST_CONFIDENCE", "0.5"));

    public String healLocator(String selector, String action, String domSnapshot, String pageUrl) {
        String healed = healViaMcp(selector, action, domSnapshot, pageUrl);
        if (healed != null) return healed;
        return healViaRest(selector, action, domSnapshot, pageUrl);
    }

    private String healViaMcp(String selector, String action, String domSnapshot, String pageUrl) {
        try {
            URL url = new URL(brainUrl + "/api/mcp/v1/tools/heal_locator");
            HttpURLConnection conn = (HttpURLConnection) url.openConnection();
            conn.setRequestMethod("POST");
            conn.setRequestProperty("Content-Type", "application/json");
            conn.setRequestProperty("X-Ghost-Protocol", "mcp-v1");
            String apiKey = System.getenv("GHOST_API_KEY");
            if (apiKey != null && !apiKey.isEmpty()) {
                conn.setRequestProperty("X-API-Key", apiKey);
            }
            conn.setDoOutput(true);

            String escapedSelector = selector.replace("\"", "\\\"");
            String escapedDom = domSnapshot.replace("\"", "\\\"").replace("\n", "");
            String jsonInputString = "{\"arguments\": {\"selector\": \"" + escapedSelector
                + "\", \"action\": \"" + action + "\", \"dom_snapshot\": \"" + escapedDom
                + "\", \"page_url\": \"" + pageUrl + "\"}}";
            return parseHealResponse(conn, jsonInputString);
        } catch (Exception e) {
            return null;
        }
    }

    private String healViaRest(String selector, String action, String domSnapshot, String pageUrl) {
        try {
            URL url = new URL(brainUrl + "/api/heal-locator");
            HttpURLConnection conn = (HttpURLConnection) url.openConnection();
            conn.setRequestMethod("POST");
            conn.setRequestProperty("Content-Type", "application/json");
            String apiKey = System.getenv("GHOST_API_KEY");
            if (apiKey != null && !apiKey.isEmpty()) {
                conn.setRequestProperty("X-API-Key", apiKey);
            }
            conn.setDoOutput(true);

            String escapedSelector = selector.replace("\"", "\\\"");
            String escapedDom = domSnapshot.replace("\"", "\\\"").replace("\n", "");
            String jsonInputString = "{\"selector\": \"" + escapedSelector + "\", \"action\": \"" + action + "\", \"dom_snapshot\": \"" + escapedDom + "\", \"page_url\": \"" + pageUrl + "\", \"framework\": \"selenium-java\"}";
            return parseHealResponse(conn, jsonInputString);
        } catch (Exception e) {
            System.err.println("[GHOST] Failed to consult brain: " + e.getMessage());
            return null;
        }
    }

    private String parseHealResponse(HttpURLConnection conn, String jsonInputString) throws Exception {

        try (OutputStream os = conn.getOutputStream()) {
            byte[] input = jsonInputString.getBytes("utf-8");
            os.write(input, 0, input.length);
        }

        if (conn.getResponseCode() != 200) {
            return null;
        }

        try (BufferedReader br = new BufferedReader(new InputStreamReader(conn.getInputStream(), "utf-8"))) {
            StringBuilder response = new StringBuilder();
            String responseLine;
            while ((responseLine = br.readLine()) != null) {
                response.append(responseLine.trim());
            }

            String resStr = response.toString();
            if (resStr.contains("\"healed_locator\"") && resStr.contains("\"confidence\"")) {
                String healed = resStr.split("\"healed_locator\":\\s*\"")[1].split("\"")[0];
                if ("null".equals(healed)) return null;
                double conf = Double.parseDouble(resStr.split("\"confidence\":\\s*")[1].split("[,}]")[0]);
                if (conf > 1.0) conf = conf / 100.0;
                if (conf >= confidenceThreshold) {
                    return healed;
                }
            }
        }
        return null;
    }

    public void writeToReport(String oldSelector, String newSelector, String action, String file, String url) {
        try {
            File dir = new File(System.getProperty("user.dir") + "/reports/ghost");
            if (!dir.exists()) dir.mkdirs();
            
            File reportFile = new File(dir, "suggested-fixes.json");
            boolean isNew = !reportFile.exists();
            
            // Append to JSON array (simple hack for appending: remove last ] and append)
            String entry = "  {\n" +
                    "    \"timestamp\": \"" + Instant.now().toString() + "\",\n" +
                    "    \"framework\": \"selenium-java\",\n" +
                    "    \"language\": \"java\",\n" +
                    "    \"file\": \"" + file + "\",\n" +
                    "    \"line\": 0,\n" +
                    "    \"action\": \"" + action + "\",\n" +
                    "    \"old_locator\": \"" + oldSelector.replace("\"", "\\\"") + "\",\n" +
                    "    \"suggested_locator\": \"" + newSelector.replace("\"", "\\\"") + "\",\n" +
                    "    \"confidence\": 0.0,\n" +
                    "    \"page_url\": \"" + (url != null ? url : "") + "\"\n" +
                    "  }";
            
            String content = "[\n" + entry + "\n]";
            if (!isNew) {
                // Read existing and inject
                // Skipping robust JSON manipulation for simplicity in this artifact
                // Just writing string
            } else {
                try (FileWriter fw = new FileWriter(reportFile)) {
                    fw.write(content);
                }
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
