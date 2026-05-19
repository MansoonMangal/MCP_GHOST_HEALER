package com.ghosthealer.core;

import org.openqa.selenium.*;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;

/**
 * 👻 Ghost WebDriver Wrapper
 * Wraps Selenium WebDriver to intercept findElement/findElements calls,
 * trigger AI locator healing, perform automated source-code patching,
 * and implement JavascriptExecutor to support casting safety.
 */
public class GhostWebDriver implements WebDriver, JavascriptExecutor {
    private WebDriver driver;
    private GhostHealerClient healerClient;

    public GhostWebDriver(WebDriver driver) {
        this.driver = driver;
        this.healerClient = new GhostHealerClient();
    }

    @Override
    public void get(String url) {
        driver.get(url);
    }

    @Override
    public String getCurrentUrl() {
        return driver.getCurrentUrl();
    }

    @Override
    public String getTitle() {
        return driver.getTitle();
    }

    @Override
    public List<WebElement> findElements(By by) {
        try {
            List<WebElement> elements = driver.findElements(by);
            if (elements.isEmpty()) {
                throw new NoSuchElementException("No elements found matching: " + by.toString());
            }
            return elements.stream()
                    .map(e -> new GhostWebElement(e, driver, getRawSelector(by), healerClient))
                    .collect(Collectors.toList());
        } catch (Exception e) {
            String rawSelector = getRawSelector(by);
            System.out.println("[GHOST] findElements failed for locator: " + rawSelector + ". Requesting AI heal...");
            try {
                String dom = (String) executeScript("return document.documentElement.outerHTML");
                String url = driver.getCurrentUrl();
                String healedLocator = healerClient.healLocator(rawSelector, "find", dom, url);
                
                if (healedLocator != null) {
                    System.out.println("[GHOST] Healed locator: " + healedLocator);
                    
                    // Source patch!
                    SourceHealer.applyFix(rawSelector, healedLocator);

                    healerClient.writeToReport(rawSelector, healedLocator, "find", "Unknown", url);
                    List<WebElement> healedElements = driver.findElements(By.cssSelector(healedLocator));
                    return healedElements.stream()
                            .map(e -> new GhostWebElement(e, driver, healedLocator, healerClient))
                            .collect(Collectors.toList());
                }
            } catch (Exception ex) {
                // ignore
            }
            throw e;
        }
    }

    @Override
    public WebElement findElement(By by) {
        String rawSelector = getRawSelector(by);
        try {
            WebElement element = driver.findElement(by);
            return new GhostWebElement(element, driver, rawSelector, healerClient);
        } catch (NoSuchElementException e) {
            System.out.println("[GHOST] findElement failed for locator: " + rawSelector + ". Requesting AI heal...");
            try {
                String dom = (String) executeScript("return document.documentElement.outerHTML");
                String url = driver.getCurrentUrl();
                String healedLocator = healerClient.healLocator(rawSelector, "find", dom, url);
                
                if (healedLocator != null) {
                    System.out.println("[GHOST] Healed locator: " + healedLocator);
                    
                    // Source patch!
                    SourceHealer.applyFix(rawSelector, healedLocator);

                    healerClient.writeToReport(rawSelector, healedLocator, "find", "Unknown", url);
                    WebElement healedElement = driver.findElement(By.cssSelector(healedLocator));
                    return new GhostWebElement(healedElement, driver, healedLocator, healerClient);
                } else {
                    throw e;
                }
            } catch (Exception ex) {
                throw new RuntimeException("Heal failed", ex);
            }
        }
    }

    private String getRawSelector(By by) {
        String selectorStr = by.toString();
        if (selectorStr.contains(": ")) {
            return selectorStr.substring(selectorStr.indexOf(": ") + 2);
        }
        return selectorStr;
    }

    @Override
    public String getPageSource() {
        return driver.getPageSource();
    }

    @Override
    public void close() {
        driver.close();
    }

    @Override
    public void quit() {
        driver.quit();
    }

    @Override
    public Set<String> getWindowHandles() {
        return driver.getWindowHandles();
    }

    @Override
    public String getWindowHandle() {
        return driver.getWindowHandle();
    }

    @Override
    public TargetLocator switchTo() {
        return driver.switchTo();
    }

    @Override
    public Navigation navigate() {
        return driver.navigate();
    }

    @Override
    public Options manage() {
        return driver.manage();
    }

    // JavascriptExecutor implementation
    @Override
    public Object executeScript(String script, Object... args) {
        return ((JavascriptExecutor) driver).executeScript(script, args);
    }

    @Override
    public Object executeAsyncScript(String script, Object... args) {
        return ((JavascriptExecutor) driver).executeAsyncScript(script, args);
    }
}
