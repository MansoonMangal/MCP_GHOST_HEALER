package com.ghosthealer.core;

import org.openqa.selenium.*;
import java.util.List;
import java.util.stream.Collectors;

public class GhostWebElement implements WebElement {
    private WebElement element;
    private WebDriver driver;
    private String locator;
    private GhostHealerClient healerClient;

    public GhostWebElement(WebElement element, WebDriver driver, String locator, GhostHealerClient healerClient) {
        this.element = element;
        this.driver = driver;
        this.locator = locator;
        this.healerClient = healerClient;
    }

    private void healAndRetry(String action, Runnable actionToRun) {
        try {
            actionToRun.run();
        } catch (Exception e) {
            System.out.println("[GHOST] Action " + action + " failed for locator: " + locator + ". Requesting AI heal...");
            try {
                String dom = (String) ((JavascriptExecutor) driver).executeScript("return document.documentElement.outerHTML");
                String url = driver.getCurrentUrl();
                String healedLocator = healerClient.healLocator(locator, action, dom, url);
                
                if (healedLocator != null) {
                    System.out.println("[GHOST] Healed locator: " + healedLocator);
                    healerClient.writeToReport(locator, healedLocator, action, "Unknown", url);
                    this.element = driver.findElement(By.cssSelector(healedLocator));
                    this.locator = healedLocator;
                    actionToRun.run(); // retry
                } else {
                    throw e;
                }
            } catch (Exception ex) {
                throw new RuntimeException("Heal failed", ex);
            }
        }
    }

    @Override
    public void click() {
        healAndRetry("click", () -> element.click());
    }

    @Override
    public void submit() {
        healAndRetry("submit", () -> element.submit());
    }

    @Override
    public void sendKeys(CharSequence... keysToSend) {
        healAndRetry("send_keys", () -> element.sendKeys(keysToSend));
    }

    @Override
    public void clear() {
        healAndRetry("clear", () -> element.clear());
    }

    @Override
    public String getTagName() {
        return element.getTagName();
    }

    @Override
    public String getAttribute(String name) {
        return element.getAttribute(name);
    }

    @Override
    public boolean isSelected() {
        return element.isSelected();
    }

    @Override
    public boolean isEnabled() {
        return element.isEnabled();
    }

    @Override
    public String getText() {
        String[] result = new String[1];
        healAndRetry("getText", () -> result[0] = element.getText());
        return result[0];
    }

    @Override
    public List<WebElement> findElements(By by) {
        return element.findElements(by).stream()
                .map(e -> new GhostWebElement(e, driver, by.toString(), healerClient))
                .collect(Collectors.toList());
    }

    @Override
    public WebElement findElement(By by) {
        return new GhostWebElement(element.findElement(by), driver, by.toString(), healerClient);
    }

    @Override
    public boolean isDisplayed() {
        return element.isDisplayed();
    }

    @Override
    public Point getLocation() {
        return element.getLocation();
    }

    @Override
    public Dimension getSize() {
        return element.getSize();
    }

    @Override
    public Rectangle getRect() {
        return element.getRect();
    }

    @Override
    public String getCssValue(String propertyName) {
        return element.getCssValue(propertyName);
    }

    @Override
    public <X> X getScreenshotAs(OutputType<X> target) throws WebDriverException {
        return element.getScreenshotAs(target);
    }
}
