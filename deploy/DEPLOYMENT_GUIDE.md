# PolyMetric Server Deployment Guide

This guide outlines the steps to deploy the PolyMetric application on a Linux server using Docker Compose.

## 1. Prerequisites

Ensure the following are installed on your server:
- **Docker**: [Install Guide](https://docs.docker.com/engine/install/)
- **Docker Compose**: [Install Guide](https://docs.docker.com/compose/install/)
- **Git** (Optional, for cloning the repo)

## 2. File Transfer

Transfer the following directories and files to your server (e.g., to `/opt/polymetric` or `~/polymetric`):

- `PolyMetric/` (Contains all backend and frontend source code)
- `deploy/` (Contains Docker configuration and scripts)
- `test_data/` (Optional: Contains test datasets if needed)

You can use `scp` or `rsync` for this. For example:
```bash
rsync -avz --exclude '.git' ./PolyMetric ./deploy ./test_data user@your-server-ip:~/polymetric/
```

## 3. Configuration

1. Navigate to the `deploy` directory:
   ```bash
   cd ~/polymetric/deploy
   ```

2. Create your production environment file from the example:
   ```bash
   cp .env.example .env
   ```

3. **Edit `.env`**:
   Open `.env` with a text editor (like `nano` or `vim`) and configure the following critical variables:
   - `DB_PASSWORD`: Set a strong password for the database.
   - `EMAIL_HOST_PASSWORD`: Your SMTP authorization code (e.g., for QQ Mail).
   - `EMAIL_HOST_USER`: Your email address.
   - `ALLOWED_HOSTS`: Add your server's IP address or domain name (e.g., `*,localhost,123.45.67.89`).
   - `VITE_API_BASE_URL`: Set this to `http://<your-server-ip>:8000/api` if accessing from a remote browser, or keep relative `/api` if using Nginx reverse proxy on the same domain.

## 4. Deployment

### Start the Services
Run the following command to build and start the containers in detached mode:

```bash
docker-compose -f docker/docker-compose.yml --env-file .env up -d --build
```

### Initialize the Backend
Once the containers are running, you must initialize the database and populate it with initial model data and scores.

Run the following command:

```bash
docker-compose -f docker/docker-compose.yml --env-file .env exec backend python init_data.py
```

This script will:
1. Clear existing model data (to prevent duplicates).
2. Insert official models (DeepSeek, Qwen, GLM, etc.).
3. Calculate initial scores (with 0.0 for irrelevant dimensions like 'multimodal' for text-only models).
4. Create a superuser account:
   - **Username**: `admin`
   - **Password**: `admin123456`
   - **Email**: `admin@example.com`

## 5. Maintenance

- **View Logs**:
  ```bash
  docker-compose -f docker/docker-compose.yml --env-file .env logs -f
  ```

- **Restart Services**:
  ```bash
  docker-compose -f docker/docker-compose.yml --env-file .env restart
  ```

- **Stop Services**:
  ```bash
  docker-compose -f docker/docker-compose.yml --env-file .env down
  ```

## 6. Cleanup (Optional)

After deployment, you can remove the `test_data` directory if you do not plan to use the sample datasets.

```bash
rm -rf ../test_data
```
