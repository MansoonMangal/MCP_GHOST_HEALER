# ☕ Ghost Healer: Selenium Java Example

This example demonstrates how to use the Ghost Healer wrapper in a standard Maven-based Selenium project.

## Integration
Add the Ghost Healer client to your project and wrap your `WebDriver` instance.

```java
import org.openqa.selenium.*;
import org.openqa.selenium.chrome.ChromeDriver;
import com.ghosthealer.HealQA;

public class LoginTest {
    public static void main(String[] args) {
        // 👻 Decorate the driver
        WebDriver rawDriver = new ChromeDriver();
        WebDriver driver = HealQA.getGhostDriver(rawDriver);

        try {
            driver.get("https://example.com");

            // 🛡️ Standard Selenium commands now have AI protection
            driver.findElement(By.id("user-email")).sendKeys("admin@example.com");
            driver.findElement(By.id("submit-btn")).click();

        } finally {
            driver.quit();
        }
    }
}
```

## Setup
1. Ensure the Ghost Healer Brain is running at `http://localhost:8000`.
2. The `HealQA` wrapper handles the communication with the Brain and performs DOM analysis on failure.
