# 📦 ONRR Container Installation Guide

This guide provides step-by-step instructions for authenticating, pulling, and running the **Open Negative Results Registry (ONRR)** Docker container from the GitHub Container Registry (GHCR).

## ⚠️ Prerequisites
* **Docker Engine** installed and running on your host machine.
* A **GitHub Account**.
* A **Personal Access Token (PAT)** with the `read:packages` scope enabled.

---

## Step 1: Create a Personal Access Token (PAT)
To download packages from GitHub Container Registry, you must authenticate using a PAT instead of your account password.

1. Go to your GitHub profile settings: **Settings > Developer settings > Personal access tokens > Tokens (classic)**.
2. Click **Generate new token (classic)**.
3. Give it a descriptive name (e.g., *"ONRR Docker Pull"*).
4. Under scopes, check the box for `read:packages`.
5. Generate the token and **copy it immediately** (you won't be able to see it again).

---

## Step 2: Authenticate with GHCR
Open your terminal and authenticate your Docker client with the GitHub Container Registry.

```bash
export CR_PAT="YOUR_PERSONAL_ACCESS_TOKEN"
echo $CR_PAT | docker login ghcr.io -u YOUR_GITHUB_USERNAME --password-stdin
```

> **🔒 Security Note:** Avoid pasting the token directly into the `docker login` command to prevent it from being saved in your shell history. Using the environment variable pipe as shown above is the recommended secure method.

---

## Step 3: Pull the Container Image
Once authenticated, pull the latest ONRR package directly from the repository.

```bash
docker pull ghcr.io/ciprian-localpulse/open-negative-results-registry:latest
```

---

## Step 4: Configure and Run the Registry
The ONRR container requires several environment variables to function correctly, particularly for database connections and API security. You can run the container using a standard Docker command.

```bash
docker run -d \
  --name onrr-instance \
  -p 8080:8080 \
  -e DB_HOST=your_database_host \
  -e DB_USER=your_database_user \
  -e DB_PASSWORD=your_database_password \
  -e API_SECRET_KEY=generate_a_secure_random_string \
  -e ENVIRONMENT=production \
  ghcr.io/ciprian-localpulse/open-negative-results-registry:latest
```

### Environment Variables Reference
* `DB_HOST`: The URL or IP address of your PostgreSQL/MongoDB instance.
* `API_SECRET_KEY`: A 64-character string used to encrypt JWT tokens.
* `PORT`: The internal port the app binds to (default is 8080).

---

## Step 5: Verify the Installation
Check if the container is running successfully:

```bash
docker ps
```

To view the startup logs and ensure the entrypoint script executed without errors:

```bash
docker logs onrr-instance
```

If the service is up, navigate to `http://localhost:8080/api/health` in your browser or use `curl` to verify the registry status. It should return a `200 OK` JSON response.

---

## 🧰 Troubleshooting

**Error: unauthenticated: User cannot be authenticated with the token provided.**
> Double-check that your PAT has the `read:packages` scope enabled and that it hasn't expired. If you recently added the scope, try generating a new token.

**Container crashes immediately (Exit 1)**
> Check the logs using `docker logs onrr-instance`. This is usually caused by missing required environment variables or failure to connect to the provided `DB_HOST`.
