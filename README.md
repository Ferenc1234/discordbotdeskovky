# Discord Bot for Board Games (Deskovky)

A Discord bot that integrates with the zatrolene-hry.cz API to provide board game information and management features.

## Features

- 🎲 Search for board games
- 📊 Get detailed game information
- 📚 Browse game categories
- 🔍 Discover popular games
- 🐳 Runs in Docker container (Proxmox-compatible)
- 🚀 Automated Docker image builds via GitHub Actions

## Commands

- `!ping` - Check if the bot is responsive
- `!info` - Display bot information
- `!games <query>` - Search for board games
- `!gameinfo <game_id>` - Get detailed information about a game
- `!categories` - List available game categories
- `!help` - Show all available commands

## Prerequisites

- Python 3.11 or higher
- Discord Bot Token (from [Discord Developer Portal](https://discord.com/developers/applications))
- Docker and Docker Compose (for containerized deployment)

## Setup

### 1. Create Discord Bot

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name
3. Go to the "Bot" tab and click "Add Bot"
4. Enable the following Privileged Gateway Intents:
   - Message Content Intent
   - Server Members Intent
5. Copy the bot token (you'll need this later)
6. Go to OAuth2 → URL Generator
7. Select scopes: `bot`
8. Select bot permissions: `Send Messages`, `Read Message History`, `Use Slash Commands`
9. Use the generated URL to invite the bot to your server

### 2. Configuration

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit the `.env` file and add your Discord bot token:

```env
DISCORD_TOKEN=your_discord_bot_token_here
DISCORD_COMMAND_PREFIX=!
API_BASE_URL=https://www.zatrolene-hry.cz/api
```

## Running the Bot

### Option 1: Docker Compose (Recommended for Proxmox)

```bash
# Build and start the bot
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the bot
docker-compose down
```

### Option 2: Docker

```bash
# Build the image
docker build -t discord-bot-deskovky .

# Run the container
docker run -d --name discord-bot-deskovky --env-file .env discord-bot-deskovky

# View logs
docker logs -f discord-bot-deskovky

# Stop the container
docker stop discord-bot-deskovky
docker rm discord-bot-deskovky
```

### Option 3: Local Python

```bash
# Install dependencies
pip install -r requirements.txt

# Run the bot
python bot.py
```

## Deployment on Proxmox

### Using Docker Compose

1. **Transfer files to Proxmox container/VM:**
   ```bash
   scp -r . user@proxmox-host:/path/to/bot/
   ```

2. **SSH into Proxmox container/VM:**
   ```bash
   ssh user@proxmox-host
   cd /path/to/bot/
   ```

3. **Configure environment:**
   ```bash
   nano .env  # Add your Discord token
   ```

4. **Start the bot:**
   ```bash
   docker-compose up -d
   ```

5. **Monitor the bot:**
   ```bash
   docker-compose logs -f
   ```

### Using Pre-built Image from GitHub Container Registry

Once the GitHub Actions workflow runs, you can pull the pre-built image:

```bash
# Pull the latest image
docker pull ghcr.io/ferenc1234/discordbotdeskovky:latest

# Run the container
docker run -d \
  --name discord-bot-deskovky \
  --restart unless-stopped \
  -e DISCORD_TOKEN=your_token_here \
  -e DISCORD_COMMAND_PREFIX=! \
  -e API_BASE_URL=https://www.zatrolene-hry.cz/api \
  ghcr.io/ferenc1234/discordbotdeskovky:latest
```

## Development

### Project Structure

```
.
├── bot.py              # Main bot application
├── api_client.py       # API client for zatrolene-hry.cz
├── requirements.txt    # Python dependencies
├── Dockerfile          # Docker image definition
├── docker-compose.yml  # Docker Compose configuration
├── .env.example        # Environment variables template
└── .github/
    └── workflows/
        └── docker-build.yml  # GitHub Actions workflow
```

### Adding New Commands

To add a new command, edit `bot.py` and use the `@bot.command()` decorator:

```python
@bot.command(name='mycommand', help='Description of my command')
async def my_command(ctx, arg: str):
    """Command implementation"""
    await ctx.send(f"You said: {arg}")
```

### API Client

The `api_client.py` module provides methods to interact with the zatrolene-hry.cz API:

- `search_games(query)` - Search for games
- `get_game_details(game_id)` - Get game details
- `get_categories()` - Get categories
- `get_games_by_category(category_id)` - Get games by category
- `get_popular_games()` - Get popular games

## GitHub Actions Workflow

The repository includes a GitHub Actions workflow that automatically builds and pushes Docker images to GitHub Container Registry (GHCR) on:

- Pushes to `main`/`master` branch
- New tags (e.g., `v1.0.0`)
- Pull requests (build only, no push)
- Manual workflow dispatch

The workflow creates multi-platform images and includes attestation for supply chain security.

## Troubleshooting

### Bot doesn't respond to commands

1. Check if the bot is online in Discord
2. Verify Message Content Intent is enabled in Discord Developer Portal
3. Check logs: `docker-compose logs -f`
4. Verify the command prefix in `.env` file

### API errors

1. Check internet connectivity
2. Verify API_BASE_URL in `.env` file
3. Check API availability: `curl https://www.zatrolene-hry.cz/api`

### Docker issues

1. Check Docker service: `systemctl status docker`
2. Rebuild image: `docker-compose build --no-cache`
3. Check container logs: `docker-compose logs`

## License

This project is provided as-is for educational and personal use.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.