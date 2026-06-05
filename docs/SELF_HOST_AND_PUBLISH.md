# Self-Host Brain + Publish Your Own SDKs

The public Brain on Render (`ghost-healer-brain.onrender.com`) is a **demo / short-term instance**.  
**Yes — anyone can fork this repo, deploy their own Brain, publish their own SDKs, and run healing independently.**

This guide is the full **clone → deploy → publish → use** path for teams and open-source adopters.

---

## Two paths (pick one)

| Path | Who | Effort | Best for |
|------|-----|--------|----------|
| **A — Self-host Brain only** | Teams using existing npm/PyPI packages | Low | Point SDKs at your Brain URL via `.env` |
| **B — Fork + publish SDKs** | Vendors, enterprises, OSS maintainers | Medium | Your npm/PyPI package names, your keys, your Brain URL baked in |

Both are supported. Path B is required if you want **install-only** healing with **your** Brain URL and **no** `.env` override for end users.

---

## Path A — Deploy your Brain (keep public SDKs)

Use this when your team installs `ghost-healer-ts-sdk` or `ghost-healer` from npm/PyPI but you **own the Brain**.

### Step 1 — Clone the repo

```bash
git clone https://github.com/MansoonMangal/MCP_GHOST_HEALER.git
cd MCP_GHOST_HEALER
```

### Step 2 — Deploy Brain on **your** Render account

1. Go to [render.com](https://render.com) → **New** → **Blueprint**
2. Connect **your fork** of this repository
3. Render reads root [`render.yaml`](../render.yaml) and creates:
   - Web service: `ghost-healer-brain`
   - Database: `ghost-db` (PostgreSQL)
4. Click **Apply** and wait for deploy (~5–10 min)

### Step 3 — Set environment on Render

In **your** web service → **Environment**, confirm:

| Variable | Value |
|----------|--------|
| `GHOST_API_KEY` | Auto-generated (admin key — keep secret) |
| `GHOST_SDK_PUBLIC_KEY` | `gh_sdk_public_8f4a2c9e1b7d3f6a0e5c8b2d4f7a1e9` *(must match published SDK)* |
| `DATABASE_URL` | Linked from `ghost-db` |

> **Important:** Keep `GHOST_SDK_PUBLIC_KEY` the same as the value in [`sdk/ts/builtin-access.json`](../sdk/ts/builtin-access.json) so existing published SDKs can authenticate to **your** Brain without republishing.

### Step 4 — Note your Brain URL

Example: `https://ghost-healer-brain-xxxx.onrender.com`

Verify:

```bash
curl https://YOUR-BRAIN-URL.onrender.com/health/ready
```

### Step 5 — Point SDKs at your Brain

**TypeScript / JavaScript** — add to project `.env`:

```env
GHOST_BRAIN_URL=https://YOUR-BRAIN-URL.onrender.com
```

**Python** — same:

```env
GHOST_BRAIN_URL=https://YOUR-BRAIN-URL.onrender.com
```

**Java** — environment or JVM flag:

```bash
export GHOST_BRAIN_URL=https://YOUR-BRAIN-URL.onrender.com
```

Then install and run tests as usual (see [README.md](../README.md)).

### Step 6 — Smoke test

```bash
GHOST_BRAIN_URL=https://YOUR-BRAIN-URL.onrender.com python scripts/verify_slo.py \
  --base-url "https://YOUR-BRAIN-URL.onrender.com" \
  --api-key "gh_sdk_public_8f4a2c9e1b7d3f6a0e5c8b2d4f7a1e9"
```

---

## Path B — Fork, customize, publish your own SDKs

Use this when you want **your package names**, **your Brain URL built in**, and **your own SDK public key**.

### Overview

```text
1. Fork repo
2. Generate your own GHOST_SDK_PUBLIC_KEY
3. Update builtin-access in TS / Python / Java
4. Deploy Brain on your Render (with your key)
5. Publish npm + PyPI packages
6. End users: npm install YOUR-PACKAGE → run tests
```

---

### Step 1 — Fork and clone

```bash
# Fork on GitHub, then:
git clone https://github.com/YOUR-ORG/MCP_GHOST_HEALER.git
cd MCP_GHOST_HEALER
```

---

### Step 2 — Generate your SDK public key

Use any long random string (example):

```text
gh_sdk_public_YOURORG_a1b2c3d4e5f6789012345678abcdef
```

You will use this **same value** in Brain Render env **and** all SDK builtin files.

---

### Step 3 — Update SDK builtin access (3 files)

**TypeScript / JavaScript** — [`sdk/ts/builtin-access.json`](../sdk/ts/builtin-access.json):

```json
{
  "brain_url": "https://YOUR-BRAIN-URL.onrender.com",
  "api_key": "gh_sdk_public_YOURORG_a1b2c3d4e5f6789012345678abcdef"
}
```

**Python** — [`ghost_healer/core/credentials.py`](../ghost_healer/core/credentials.py):

```python
DEFAULT_BRAIN_URL = "https://YOUR-BRAIN-URL.onrender.com"
BUILTIN_API_KEY = "gh_sdk_public_YOURORG_a1b2c3d4e5f6789012345678abcdef"
```

**Java** — [`ghost_healer/framework/java/GhostCredentials.java`](../ghost_healer/framework/java/GhostCredentials.java):

```java
public static final String DEFAULT_BRAIN_URL = "https://YOUR-BRAIN-URL.onrender.com";
public static final String BUILTIN_API_KEY = "gh_sdk_public_YOURORG_a1b2c3d4e5f6789012345678abcdef";
```

**Brain default** — [`mcp-server/config/settings.py`](../mcp-server/config/settings.py) (optional fallback):

```python
sdk_public_key: str = os.getenv("GHOST_SDK_PUBLIC_KEY", "gh_sdk_public_YOURORG_...")
```

**Render blueprint** — [`render.yaml`](../render.yaml):

```yaml
- key: GHOST_SDK_PUBLIC_KEY
  value: "gh_sdk_public_YOURORG_a1b2c3d4e5f6789012345678abcdef"
```

> Deploy Brain **after** you know your Render URL, then update `brain_url` in SDK files to match.

---

### Step 4 — Deploy Brain on your Render

Same as Path A — Blueprint from **your fork** → Apply → wait for healthy `/health/ready`.

Copy your live URL and update `brain_url` in the three SDK files if you used a placeholder.

---

### Step 5 — Publish TypeScript / JavaScript SDK (npm)

```bash
cd sdk/ts

# Optional: rename package in package.json
# "name": "@your-org/ghost-healer-ts-sdk"

# Bump version
npm version patch

npm run build
npm login
npm publish --access public
```

End users then:

```bash
npm install @your-org/ghost-healer-ts-sdk
npx ghost-playwright test
```

No API key, no login — your Brain URL and key are built into the package.

---

### Step 6 — Publish Python SDK (PyPI)

```bash
# From repo root — update name in pyproject.toml if desired
pip install build twine
python -m build
twine upload dist/*
```

End users:

```bash
pip install ghost-healer   # or your package name
pytest
```

---

### Step 7 — Java SDK distribution

Java classes live in `ghost_healer/framework/java/`. Options:

| Method | How |
|--------|-----|
| **Copy sources** | Add to `src/test/java` in your Maven project (see `demo/pw-java/`) |
| **Internal JAR** | Build JAR, publish to Artifactory/Nexus |
| **Maven Central** | Add `pom.xml` for `ghost-healer-java` module (future) |

After updating `GhostCredentials.java`, rebuild and redistribute the JAR/sources to your teams.

---

### Step 8 — Verify end-to-end

```bash
# Brain
curl https://YOUR-BRAIN-URL.onrender.com/health

# TS SDK (from a test project)
npx ghost-healer doctor

# Python
ghost-healer doctor
```

---

## What each role owns

| Role | Owns |
|------|------|
| **Brain host (you)** | Render account, Postgres, `GHOST_API_KEY`, `GHOST_SDK_PUBLIC_KEY`, Brain URL |
| **SDK publisher (you)** | npm/PyPI package name, version, builtin-access values |
| **QA engineer (end user)** | `npm install` / `pip install` → run tests — no Brain setup |

---

## Render free tier notes

| Topic | Note |
|-------|------|
| **Duration** | Free web services spin down after inactivity; demo instances are not long-term SLAs |
| **Cold start** | First request after idle may take 30–60 seconds |
| **Database** | Free Postgres included via `render.yaml`; heals persist across restarts |
| **Upgrade** | Move to paid plan for always-on production |

---

## Security checklist

- [ ] Never commit `GHOST_API_KEY` (admin key) to git
- [ ] `GHOST_SDK_PUBLIC_KEY` is **designed** to ship inside SDKs — rotate if leaked/abused
- [ ] Restrict `CORS_ORIGINS` in production if needed
- [ ] Use private Brain + custom key for regulated environments

---

## Quick decision tree

```text
Want to use Ghost Healer long-term?
│
├─ Yes, I'll host everything myself
│   └─ Path B: Fork → customize keys → Deploy Render → Publish SDKs
│
├─ Yes, but I'll use Mansoon's npm/PyPI packages
│   └─ Path A: Deploy your Render Brain → set GHOST_BRAIN_URL in .env
│
└─ Just trying the demo
    └─ Use public Brain (temporary) + npm install ghost-healer-ts-sdk
```

---

## Related docs

- [DEPLOY_COMPLETE.md](DEPLOY_COMPLETE.md) — Render deploy troubleshooting
- [README.md](../README.md) — Usage per language/tool
- [FRAMEWORK.md](../FRAMEWORK.md) — Architecture overview
- [enterprise_usage.md](enterprise_usage.md) — CI/CD and governance
