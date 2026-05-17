package com.ghosthealer.core;

import org.openqa.selenium.*;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;

public class GhostWebDriver implements WebDriver {
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
        return driver.findElements(by).stream()
                .map(e -> new GhostWebElement(e, driver, by.toString(), healerClient))
                .collect(Collectors.toList());
    }

    @Override
    public WebElement findElement(By by) {
        try {
            WebElement element = driver.findElement(by);
            return new GhostWebElement(element, driver, by.toString(), healerClient);
        } catch (NoSuchElementException e) {
            System.out.println("[GHOST] findElement failed for locator: " + by.toString() + ". Requesting AI heal...");
            try {
                String dom = (String) ((JavascriptExecutor) driver).executeScript("return document.documentElement.outerHTML");
                String url = driver.getCurrentUrl();
                String healedLocator = healerClient.healLocator(by.toString(), "find", dom, url);
                
                if (healedLocator != null) {
                    System.out.println("[GHOST] Healed locator: " + healedLocator);
                    healerClient.writeToReport(by.toString(), healedLocator, "find", "Unknown", url);
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
}
