package com.ghosthealer.core;

import java.lang.annotation.*;

/**
 * 👻 Mark a WebDriver field for Ghost Healer auto-healing.
 *
 * Usage:
 *   @GhostDriver
 *   protected WebDriver driver;
 */
@Target(ElementType.FIELD)
@Retention(RetentionPolicy.RUNTIME)
@Documented
public @interface GhostDriver {
}
