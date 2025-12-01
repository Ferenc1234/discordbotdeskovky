# Proxmox Deployment Guide

This guide walks you through deploying the Discord bot on Proxmox.

## Prerequisites

- Proxmox VE installed and running
- A container or VM with Docker and Docker Compose installed
- Discord bot token from Discord Developer Portal

## Option 1: Deploy in LXC Container (Recommended)

### 1. Create LXC Container

In Proxmox web interface:
1. Click "Create CT"
2. Configure:
   - **Hostname**: discord-bot
   - **Template**: debian-12-standard or ubuntu-22.04-standard
   - **CPU**: 1 core (minimum)
   - **Memory**: 512 MB (minimum), 1 GB recommended
   - **Swap**: 512 MB
   - **Disk**: 4 GB (minimum)
   - **Network**: Bridge to vmbr0 with DHCP or static IP

### 2. Install Docker in Container

SSH into the container:
```bash
pct enter <CONTAINER_ID>
# or
ssh root@<CONTAINER_IP>
```

Install Docker:
```bash
# Update package list
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
apt install docker-compose -y

# Verify installation
docker --version
docker-compose --version
```

### 3. Deploy the Bot

```bash
# Create directory for the bot
mkdir -p /opt/discord-bot
cd /opt/discord-bot

# Clone the repository or copy files
# If using git:
apt install git -y
git clone https://github.com/Ferenc1234/discordbotdeskovky.git .

# Create .env file
cp .env.example .env
nano .env
# Add your Discord bot token

# Start the bot
docker-compose up -d

# View logs
docker-compose logs -f
```

### 4. Auto-start on Boot

To ensure the bot starts automatically:

```bash
# Enable Docker service
systemctl enable docker

# The docker-compose.yml already has restart: unless-stopped
# which will auto-restart the container
```

## Option 2: Deploy in VM

### 1. Create VM

In Proxmox web interface:
1. Click "Create VM"
2. Configure:
   - **OS**: Ubuntu Server 22.04 LTS or Debian 12
   - **CPU**: 1 core
   - **Memory**: 1 GB
   - **Disk**: 10 GB
   - **Network**: Bridge to vmbr0

### 2. Install Docker and Deploy

Follow the same steps as Option 1, steps 2-4.

## Option 3: Use Pre-built Docker Image

If you don't want to build locally:

```bash
# Create directory
mkdir -p /opt/discord-bot
cd /opt/discord-bot

# Create .env file
cat > .env << 'EOF'
DISCORD_TOKEN=your_discord_bot_token_here
DISCORD_COMMAND_PREFIX=!
API_BASE_URL=https://www.zatrolene-hry.cz/api
EOF

# Run the pre-built image from GitHub Container Registry
docker run -d \
  --name discord-bot-deskovky \
  --restart unless-stopped \
  --env-file .env \
  ghcr.io/ferenc1234/discordbotdeskovky:latest

# View logs
docker logs -f discord-bot-deskovky
```

## Managing the Bot

### View Logs
```bash
docker-compose logs -f
# or
docker logs -f discord-bot-deskovky
```

### Stop the Bot
```bash
docker-compose down
# or
docker stop discord-bot-deskovky
```

### Restart the Bot
```bash
docker-compose restart
# or
docker restart discord-bot-deskovky
```

### Update the Bot
```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose up -d --build

# Or with pre-built image:
docker pull ghcr.io/ferenc1234/discordbotdeskovky:latest
docker-compose up -d
```

### View Bot Status
```bash
docker-compose ps
# or
docker ps | grep discord-bot
```

## Troubleshooting

### Container won't start
```bash
# Check logs
docker-compose logs

# Check if token is set
docker-compose config | grep DISCORD_TOKEN
```

### Out of memory
```bash
# Increase container memory in Proxmox:
# 1. Stop container: pct stop <CONTAINER_ID>
# 2. Edit config: nano /etc/pve/lxc/<CONTAINER_ID>.conf
# 3. Increase: memory: 1024
# 4. Start container: pct start <CONTAINER_ID>
```

### Docker not starting in LXC
```bash
# Enable nesting in container:
# 1. Stop container
# 2. Edit: nano /etc/pve/lxc/<CONTAINER_ID>.conf
# 3. Add: features: nesting=1
# 4. Start container
```

### Bot not responding to commands
1. Check bot is online in Discord
2. Verify Message Content Intent is enabled in Discord Developer Portal
3. Check command prefix in .env matches what you're typing
4. Review logs: `docker-compose logs -f`

## Security Recommendations

1. **Firewall**: Only expose necessary ports (Discord bot doesn't need inbound ports)
2. **Updates**: Regularly update the container OS and Docker images
3. **Token Security**: Never commit the .env file with real tokens
4. **Backups**: Backup your .env file and configuration
5. **Monitoring**: Set up log monitoring and alerts

## Resource Requirements

### Minimum
- CPU: 1 core
- RAM: 512 MB
- Disk: 2 GB
- Network: Standard internet connection

### Recommended
- CPU: 1-2 cores
- RAM: 1 GB
- Disk: 4 GB
- Network: Low latency connection for better response times

## Monitoring

### Check resource usage
```bash
# In Proxmox host
pct list
pveperf

# In container
docker stats discord-bot-deskovky
```

### Set up log rotation
```bash
# Docker already handles log rotation via docker-compose.yml
# but you can adjust in docker-compose.yml:
# logging:
#   driver: "json-file"
#   options:
#     max-size: "10m"
#     max-file: "3"
```

## Backup and Restore

### Backup
```bash
# Backup configuration
cd /opt/discord-bot
tar -czf discord-bot-backup-$(date +%Y%m%d).tar.gz .env docker-compose.yml

# Copy to safe location
scp discord-bot-backup-*.tar.gz user@backup-server:/backups/
```

### Restore
```bash
# Copy backup to new server
scp user@backup-server:/backups/discord-bot-backup-*.tar.gz /tmp/

# Extract
cd /opt/discord-bot
tar -xzf /tmp/discord-bot-backup-*.tar.gz

# Start bot
docker-compose up -d
```

## Advanced Configuration

### Custom Port Mapping (if needed in future)
```yaml
# In docker-compose.yml, add:
ports:
  - "8080:8080"  # Example if bot adds web interface
```

### Multiple Bots
Run multiple bots by creating separate directories:
```bash
mkdir /opt/discord-bot-1
mkdir /opt/discord-bot-2

# Deploy separately with different .env files
```

### Resource Limits
Add to docker-compose.yml:
```yaml
services:
  discordbot:
    # ... existing config ...
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 512M
        reservations:
          cpus: '0.5'
          memory: 256M
```
