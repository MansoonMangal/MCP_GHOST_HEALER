package com.ghosthealer.core;

import java.lang.instrument.Instrumentation;

/**
 * JVM javaagent for absolute zero-change Selenium healing.
 *
 * Usage (Maven Surefire / Gradle):
 *   -javaagent:path/to/ghost-healer-agent.jar
 *
 * Or environment:
 *   export JAVA_TOOL_OPTIONS="-javaagent:ghost-healer-agent.jar"
 */
public class GhostHealerAgent {

    public static void premain(String agentArgs, Instrumentation inst) {
        System.out.println("[GHOST] GhostHealerAgent premain — registering JUnit 5 auto-extension");
        System.setProperty("junit.jupiter.extensions.autodetection.enabled", "true");
        System.setProperty("ghost.healer.agent.enabled", "true");
    }

    public static void agentmain(String agentArgs, Instrumentation inst) {
        premain(agentArgs, inst);
    }
}
