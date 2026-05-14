# 🚀 Production Deployment Guide: Ghost Healer

This guide covers the deployment of the **Ghost Healer AI Brain** to a production-ready environment and the distribution of the **Ghost Healer SDK** to your team.

---

## 1. 🧠 Deploying the AI Brain (FastAPI)

The Brain is a centralized service that must be accessible to all CI/CD pipelines.

### Option A: Render Blueprint (One-Click)
1. **Push your code** to a GitHub repository.
2. Log in to [Render](https://dashboard.render.com).
3. Click **New +** -> **Blueprint**.
4. Connect your repository. Render will automatically detect the `render.yaml` file and provision:
   - The FastAPI AI Brain service.
   - A free MongoDB instance for analytics and persistent storage.
5. Once deployed, copy your service URL (e.g., `https://ghost-brain.onrender.com`).

### Option B: AWS App Runner / ECS
1. **Push Image**: Build and push the `mcp-server` image to AWS ECR.
2. **Deploy**: Use AWS App Runner for a managed experience:
   - **Service Type**: Source code repository.
   - **Runtime**: Docker.
   - **Port**: 8000.
3. **IAM**: Ensure the service has permissions to write to CloudWatch for logs.

---

## 2. 📦 Distributing the SDK

### Python Client
To make the framework installable via `pip install ghost-healer`:

1. **Build the package**:
   ```bash
   pip install build
   python -m build
   ```
2. **Publish to PyPI** (or your internal Artifactory/Nexus):
   ```bash
   twine upload dist/*
   ```
3. **Usage**:
   Teams simply run `pip install ghost-healer` and then `ghost-healer init`.

---

## ⚙️ Enterprise Configuration
Once deployed, configure your environment to point to the production Brain:

```bash
# In your CI/CD settings (Jenkins, GitHub Actions, etc.)
export MCP_SERVER_URL="https://your-ghost-brain.onrender.com"
```

### 📈 Health Check
Verify your deployment by visiting:
- **API Docs**: `https://<your-url>/docs` (FastAPI Swagger UI)
- **Health**: `https://<your-url>/health`
- **Analytics**: `https://<your-url>/api/confidence-report`

---

**Built for the Enterprise. Powered by AI.** 🛡️🌍🏆✨
