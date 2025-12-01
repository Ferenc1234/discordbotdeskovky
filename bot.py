"""
Discord Bot for Board Games (Deskovky)
Integrates with zatrolene-hry.cz API
"""

import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from api_client import ZatroleneHryClient

# Load environment variables
load_dotenv()

# Bot configuration
TOKEN = os.getenv('DISCORD_TOKEN')
COMMAND_PREFIX = os.getenv('DISCORD_COMMAND_PREFIX', '!')
API_BASE_URL = os.getenv('API_BASE_URL', 'https://www.zatrolene-hry.cz/api')

# Bot setup with intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)

# Initialize API client
api_client = ZatroleneHryClient(API_BASE_URL)


@bot.event
async def on_ready():
    """Event handler for when the bot is ready"""
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is in {len(bot.guilds)} guild(s)')
    
    # Set bot status
    await bot.change_presence(
        activity=discord.Game(name=f"{COMMAND_PREFIX}help for commands")
    )


@bot.event
async def on_message(message):
    """Event handler for messages"""
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return
    
    # Process commands
    await bot.process_commands(message)


@bot.command(name='ping', help='Check if the bot is responsive')
async def ping(ctx):
    """Ping command to check bot responsiveness"""
    latency = round(bot.latency * 1000)
    await ctx.send(f'🏓 Pong! Latency: {latency}ms')


@bot.command(name='info', help='Display bot information')
async def info(ctx):
    """Display bot information"""
    embed = discord.Embed(
        title="Discord Bot for Board Games",
        description="A bot for managing and discovering board games",
        color=discord.Color.blue()
    )
    embed.add_field(name="Guilds", value=len(bot.guilds), inline=True)
    embed.add_field(name="Users", value=len(bot.users), inline=True)
    embed.add_field(name="Prefix", value=COMMAND_PREFIX, inline=True)
    embed.set_footer(text="Powered by zatrolene-hry.cz API")
    
    await ctx.send(embed=embed)


@bot.command(name='games', help='Search for board games')
async def search_games(ctx, *, query: str = None):
    """Search for board games using the API"""
    if query is None:
        await ctx.send("❌ Please provide a search query. Usage: `!games <query>`")
        return
    
    await ctx.send(f"🔍 Searching for games matching: {query}...")
    
    try:
        results = await api_client.search_games(query)
        
        if not results:
            await ctx.send("❌ No games found matching your query.")
            return
        
        embed = discord.Embed(
            title=f"Search Results for '{query}'",
            description=f"Found {len(results)} game(s)",
            color=discord.Color.green()
        )
        
        # Display up to 5 results
        for i, game in enumerate(results[:5], 1):
            game_name = game.get('name', 'Unknown')
            game_id = game.get('id', 'N/A')
            embed.add_field(
                name=f"{i}. {game_name}",
                value=f"ID: {game_id}",
                inline=False
            )
        
        if len(results) > 5:
            embed.set_footer(text=f"Showing 5 of {len(results)} results")
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"❌ Error searching for games: {str(e)}")


@bot.command(name='gameinfo', help='Get detailed information about a game')
async def game_info(ctx, game_id: str = None):
    """Get detailed information about a specific game"""
    if game_id is None:
        await ctx.send("❌ Please provide a game ID. Usage: `!gameinfo <game_id>`")
        return
    
    await ctx.send(f"🔍 Fetching information for game ID: {game_id}...")
    
    try:
        game = await api_client.get_game_details(game_id)
        
        if not game:
            await ctx.send(f"❌ Game with ID {game_id} not found.")
            return
        
        embed = discord.Embed(
            title=game.get('name', 'Unknown Game'),
            description=game.get('description', 'No description available'),
            color=discord.Color.blue()
        )
        
        # Add game details
        if 'players' in game:
            embed.add_field(name="Players", value=game['players'], inline=True)
        if 'playtime' in game:
            embed.add_field(name="Playtime", value=game['playtime'], inline=True)
        if 'age' in game:
            embed.add_field(name="Age", value=game['age'], inline=True)
        if 'year' in game:
            embed.add_field(name="Year", value=game['year'], inline=True)
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"❌ Error fetching game information: {str(e)}")


@bot.command(name='categories', help='List available game categories')
async def list_categories(ctx):
    """List available game categories"""
    await ctx.send("📚 Fetching categories...")
    
    try:
        categories = await api_client.get_categories()
        
        if not categories:
            await ctx.send("❌ No categories found.")
            return
        
        embed = discord.Embed(
            title="Board Game Categories",
            description=f"Total: {len(categories)} categories",
            color=discord.Color.purple()
        )
        
        # Display categories (up to 10)
        cat_list = []
        for cat in categories[:10]:
            cat_name = cat.get('name', 'Unknown')
            cat_list.append(f"• {cat_name}")
        
        if cat_list:
            embed.add_field(
                name="Categories",
                value="\n".join(cat_list),
                inline=False
            )
        
        if len(categories) > 10:
            embed.set_footer(text=f"Showing 10 of {len(categories)} categories")
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"❌ Error fetching categories: {str(e)}")


@bot.event
async def on_command_error(ctx, error):
    """Global error handler for commands"""
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"❌ Command not found. Use `{COMMAND_PREFIX}help` to see available commands.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Missing required argument. Use `{COMMAND_PREFIX}help {ctx.command}` for usage.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send(f"❌ Invalid argument provided. Use `{COMMAND_PREFIX}help {ctx.command}` for usage.")
    else:
        print(f"Error: {error}")
        await ctx.send(f"❌ An error occurred while processing the command.")


def main():
    """Main function to run the bot"""
    if not TOKEN:
        print("ERROR: DISCORD_TOKEN not found in environment variables!")
        print("Please create a .env file with your Discord bot token.")
        return
    
    try:
        bot.run(TOKEN)
    except discord.errors.LoginFailure:
        print("ERROR: Invalid Discord token!")
    except Exception as e:
        print(f"ERROR: {e}")


if __name__ == "__main__":
    main()
