#!/bin/bash
set -euxo pipefail

# Log everything for debugging
exec > /var/log/user_data.log 2>&1

echo "=== Starting EC2 Bootstrap ==="

# ──────────────────────────────────────────────
# Install Docker
# ──────────────────────────────────────────────
yum update -y
yum install -y docker git
systemctl start docker
systemctl enable docker
usermod -aG docker ec2-user

# Install Docker Compose
DOCKER_COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep '"tag_name"' | sed 's/.*"v//' | sed 's/".*//')
curl -L "https://github.com/docker/compose/releases/download/v$${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# ──────────────────────────────────────────────
# Clone Backend Repository
# ──────────────────────────────────────────────
cd /home/ec2-user
git clone ${backend_repo_url} adventure-booking-system-backend
cd adventure-booking-system-backend

# ──────────────────────────────────────────────
# Create Environment File
# ──────────────────────────────────────────────
cat > .env.local << 'ENVEOF'
PROJECT_NAME=FastAPI Backend
API_V1_STR=/api/v1
MONGODB_URL=${mongodb_url}
DATABASE_NAME=${database_name}
SECRET_KEY=${secret_key}
ACCESS_TOKEN_EXPIRE_MINUTES=60
STRIPE_SECRET_KEY=${stripe_secret_key}
STRIPE_PUBLISHABLE_KEY=${stripe_publishable_key}
STRIPE_WEBHOOK_SECRET=${stripe_webhook_secret}
ENVEOF

# ──────────────────────────────────────────────
# Build and Start with Docker Compose
# ──────────────────────────────────────────────
docker-compose up -d --build

# Fix ownership so ec2-user can manage later
chown -R ec2-user:ec2-user /home/ec2-user/adventure-booking-system-backend

echo "=== EC2 Bootstrap Complete ==="
