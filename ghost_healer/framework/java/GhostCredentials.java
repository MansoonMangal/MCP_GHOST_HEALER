package com.ghosthealer.core;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.attribute.PosixFilePermission;
import java.util.EnumSet;
import java.util.Set;

/**
 * Install-only Brain access — mirrors sdk/ts/src/credentials.js and ghost_healer/core/credentials.py.
 * Provisions ~/.ghost/credentials.json with built-in SDK public key on first use.
 */
public final class GhostCredentials {

    public static final String DEFAULT_BRAIN_URL = "https://ghost-healer-brain.onrender.com";
    public static final String BUILTIN_API_KEY = "gh_sdk_public_8f4a2c9e1b7d3f6a0e5c8b2d4f7a1e9";

    private static volatile boolean initialized = false;

    private GhostCredentials() {}

    public static Path getGhostDir() {
        String home = System.getProperty("user.home", ".");
        return Paths.get(home, ".ghost");
    }

    public static Path getCredentialsPath() {
        return getGhostDir().resolve("credentials.json");
    }

    /** Auto-provision on first SDK use — no manual login or API key. */
    public static void ensureBuiltin() {
        if (initialized) {
            return;
        }
        synchronized (GhostCredentials.class) {
            if (initialized) {
                return;
            }
            Path credPath = getCredentialsPath();
            try {
                if (!Files.exists(credPath)) {
                    Files.createDirectories(getGhostDir());
                    String payload = "{\n"
                        + "  \"api_key\": \"" + BUILTIN_API_KEY + "\",\n"
                        + "  \"brain_url\": \"" + DEFAULT_BRAIN_URL + "\",\n"
                        + "  \"tenant_id\": \"sdk\",\n"
                        + "  \"project_id\": \"default\",\n"
                        + "  \"source\": \"builtin\"\n"
                        + "}\n";
                    Files.write(credPath, payload.getBytes(StandardCharsets.UTF_8));
                    trySetPrivatePermissions(credPath);
                }
            } catch (IOException e) {
                System.err.println("[GHOST] Could not write credentials: " + e.getMessage());
            }
            initialized = true;
        }
    }

    public static String getApiKey() {
        ensureBuiltin();
        String env = System.getenv("GHOST_API_KEY");
        if (env != null && !env.trim().isEmpty()) {
            return env.trim();
        }
        String fromFile = readJsonField(getCredentialsPath(), "api_key");
        if (fromFile != null && !fromFile.isEmpty()) {
            return fromFile;
        }
        return BUILTIN_API_KEY;
    }

    public static String getBrainUrl() {
        ensureBuiltin();
        String env = System.getenv("GHOST_BRAIN_URL");
        if (env != null && !env.trim().isEmpty()) {
            return env.trim();
        }
        String fromFile = readJsonField(getCredentialsPath(), "brain_url");
        if (fromFile != null && !fromFile.isEmpty()) {
            return fromFile;
        }
        return DEFAULT_BRAIN_URL;
    }

    private static String readJsonField(Path path, String field) {
        if (!Files.exists(path)) {
            return null;
        }
        try {
            String content = Files.readString(path, StandardCharsets.UTF_8);
            String search = "\"" + field + "\"";
            int idx = content.indexOf(search);
            if (idx < 0) {
                return null;
            }
            int colon = content.indexOf(':', idx);
            int quoteStart = content.indexOf('"', colon + 1);
            int quoteEnd = content.indexOf('"', quoteStart + 1);
            if (quoteStart < 0 || quoteEnd < 0) {
                return null;
            }
            return content.substring(quoteStart + 1, quoteEnd);
        } catch (IOException e) {
            return null;
        }
    }

    private static void trySetPrivatePermissions(Path path) {
        try {
            Set<PosixFilePermission> perms = EnumSet.of(
                PosixFilePermission.OWNER_READ,
                PosixFilePermission.OWNER_WRITE
            );
            Files.setPosixFilePermissions(path, perms);
        } catch (Exception ignored) {
            /* Windows or unsupported */
        }
    }
}
