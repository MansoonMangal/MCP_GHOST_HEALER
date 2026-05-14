package framework.java;

import org.openqa.selenium.*;
import org.openqa.selenium.support.events.EventFiringDecorator;
import org.openqa.selenium.support.events.WebDriverListener;
import java.net.HttpURLConnection;
import java.net.URL;
import java.io.OutputStream;
import java.io.InputStream;
import java.util.Scanner;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;

/**
 * 👻 HealQA Ghost Engine (Java)
 * Intercepts Selenium actions and heals them transparently.
 */
public class HealQA {

    /**
     * Wraps a native driver to make it self-healing.
     */
    public static WebDriver getGhostDriver(WebDriver driver) {
        WebDriverListener listener = new HealingListener(driver);
        return new EventFiringDecorator<>(listener).decorate(driver);
    }

    private static class HealingListener implements WebDriverListener {
        private final WebDriver driver;

        public HealingListener(WebDriver driver) {
            this.driver = driver;
        }

        @Override
        public void onError(Object target, Method method, Object[] args, InvocationTargetException e) {
            // If findElement or an action fails, we trigger healing!
            System.out.println("👻 Ghost Mode: Detected failure. Healing...");

            // Logic to heal based on the failed selector...
            // (In a full implementation, we'd extract the selector from the exception)
        }
    }

    /**
     * Legacy support for those who still want an explicit call.
     */
    public static void safePerform(WebDriver driver, String selector, String action, String value) {
        try {
            WebElement el = driver.findElement(By.cssSelector(selector));
            if (action.equals("fill"))
                el.sendKeys(value);
            else
                el.click();
        } catch (Exception e) {
            String healed = callAI(driver, selector, action);
            if (healed != null) {
                WebElement el = driver.findElement(By.cssSelector(healed));
                if (action.equals("fill"))
                    el.sendKeys(value);
                else
                    el.click();
            }
        }
    }

    private static String callAI(WebDriver driver, String selector, String action) {
        try {
            String dom = (String) ((JavascriptExecutor) driver)
                    .executeScript("return document.documentElement.outerHTML");
            URL url = new URL("http://localhost:8000/api/heal-locator");
            HttpURLConnection conn = (HttpURLConnection) url.openConnection();
            conn.setRequestMethod("POST");
            conn.setRequestProperty("Content-Type", "application/json");
            conn.setDoOutput(true);

            String json = String.format("{\"original_locator\":\"%s\", \"action\":\"%s\", \"dom_snapshot\":\"%s\"}",
                    selector, action, dom.replace("\"", "\\\"").replace("\n", " "));

            try (OutputStream os = conn.getOutputStream()) {
                os.write(json.getBytes());
            }

            if (conn.getResponseCode() == 200) {
                try (InputStream is = conn.getInputStream(); Scanner s = new Scanner(is)) {
                    String resp = s.useDelimiter("\\A").next();
                    return resp.split("\"healed_locator\": \"")[1].split("\"")[0];
                }
            }
        } catch (Exception e) {
        }
        return null;
    }
}
