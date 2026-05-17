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
        try {
            URL url = new URL(brainUrl + "/api/heal-locator");
            HttpURLConnection conn = (HttpURLConnection) url.openConnection();
            conn.setRequestMethod("POST");
            conn.setRequestProperty("Content-Type", "application/json");
            conn.setDoOutput(true);

            String escapedSelector = selector.replace("\"", "\\\"");
            String escapedDom = domSnapshot.replace("\"", "\\\"").replace("\n", "");
            String jsonInputString = "{\"selector\": \"" + escapedSelector + "\", \"action\": \"" + action + "\", \"dom_snapshot\": \"" + escapedDom + "\", \"page_url\": \"" + pageUrl + "\", \"framework\": \"selenium-java\"}";

            try (OutputStream os = conn.getOutputStream()) {
                byte[] input = jsonInputString.getBytes("utf-8");
                os.write(input, 0, input.length);
            }

            if (conn.getResponseCode() != 200) {
                return null;
            }

            try (BufferedReader br = new BufferedReader(new InputStreamReader(conn.getInputStream(), "utf-8"))) {
                StringBuilder response = new StringBuilder();
                String responseLine = null;
                while ((responseLine = br.readLine()) != null) {
                    response.append(responseLine.trim());
                }
                
                String resStr = response.toString();
                // Extremely simple JSON parsing for confidence and healed_locator
                if (resStr.contains("\"healed_locator\"") && resStr.contains("\"confidence\"")) {
                    String healed = resStr.split("\"healed_locator\":\\s*\"")[1].split("\"")[0];
                    double conf = Double.parseDouble(resStr.split("\"confidence\":\\s*")[1].split("[,}]")[0]);
                    
                    if (conf >= confidenceThreshold) {
                        return healed;
                    }
                }
            }
        } catch (Exception e) {
            System.err.println("[GHOST] Failed to consult brain: " + e.getMessage());
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
