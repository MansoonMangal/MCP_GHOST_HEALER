# Ghost Healer — Java Usage (Playwright + Selenium)

**Install framework classes → minimal wiring → run tests. No API key. No login.**

Built-in Brain access is provisioned automatically when Ghost classes load (`~/.ghost/credentials.json`).

---

## Step 1 — Add Ghost Healer to your project

Copy or depend on classes from:

```text
ghost_healer/framework/java/
```

Key classes:

| Class | Purpose |
|-------|---------|
| `GhostCredentials` | Install-only Brain access (automatic) |
| `GhostHealerExtension` | Selenium JUnit 5 extension |
| `GhostPlaywright` | Playwright page protection |
| `GhostHealerAgent` | Optional javaagent for zero-annotation Selenium |

Include in Maven/Gradle test classpath (see `demo/pw-java/pom.xml` for reference).

---

## Step 2 — Selenium (JUnit 5)

**Option A — One annotation on base test (recommended)**

```java
import org.junit.jupiter.api.extension.ExtendWith;
import com.ghosthealer.core.GhostHealerExtension;
import com.ghosthealer.core.GhostDriver;

@ExtendWith(GhostHealerExtension.class)
public class BaseTest {

    @GhostDriver
    protected WebDriver driver;

    @BeforeEach
    void setUp() {
        driver = new ChromeDriver();
    }
}
```

Subclass tests need **no Ghost imports** — `findElement` calls are auto-healed.

**Option B — Javaagent (zero annotations)**

```bash
export JAVA_TOOL_OPTIONS="-javaagent:path/to/ghost-healer-agent.jar"
mvn test
```

---

## Step 3 — Playwright Java

Wrap the page once in setup:

```java
import com.ghosthealer.core.GhostPlaywright;

@BeforeEach
void setUp() {
    page = GhostPlaywright.protect(playwright.chromium().launch().newPage());
}
```

All `page.locator(...).click()` calls are then self-healing.

---

## Step 4 — Run tests

```bash
mvn test
```

No `GHOST_API_KEY` or `.env` required for the hosted Brain.

---

## What is automatic

| Feature | Automatic? |
|---------|------------|
| Brain URL | Yes — `https://ghost-healer-brain.onrender.com` |
| API key | Yes — built-in SDK public key |
| `~/.ghost/credentials.json` | Yes — created on first Ghost class load |
| `X-API-Key` on Brain HTTP calls | Yes |

Console on first run:

```text
[GHOST] Install-only Brain access ready (Java SDK).
```

---

## Healing flow

| Run | Result |
|-----|--------|
| 1st | Locator may fail |
| Runtime | Brain consulted; source patched when confident |
| 2nd | Healed locator used |

---

## CI/CD

```yaml
- run: mvn test
```

No secrets required for hosted Brain.

---

## Optional overrides (enterprise)

| Need | How |
|------|-----|
| Private Brain | Set `GHOST_API_KEY` env in CI |
| Custom URL | Set `GHOST_BRAIN_URL` env |
