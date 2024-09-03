import yaml
import aiohttp
import logging
from aiohttp import web
from logging.handlers import TimedRotatingFileHandler

# Load YAML configuration
async def load_config(config_file):
    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)
    return config['routes']

# Send message to Telegram
async def send_telegram_message(bot_token, chat_id, message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {"chat_id": chat_id, "text": message}
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, data=data) as response:
                response.raise_for_status()
        except aiohttp.ClientError as e:
            logging.error(f"Failed to send message to Telegram: {e}")

# HTTP request handler
async def handle_request(request, routes, bot_token, chat_id):
    path = request.path
    ip_address = request.remote
    user_agent = request.headers.get('User-Agent', 'Unknown')

    # Log all incoming requests
    log_message = f"Incoming request | Path: {path} | IP: {ip_address} | User-Agent: {user_agent}"
    logging.info(log_message)
    
    matched_route = next((route for route in routes if route['path'] == path), None)
    
    if matched_route:
        log_message = (f"Matched route | Path: {path} | Response: {matched_route['response']} | "
                       f"Code: {matched_route['response_code']} | IP: {ip_address} | "
                       f"User-Agent: {user_agent}")
        logging.info(log_message)
        # await send_telegram_message(bot_token, chat_id, log_message)
        
        return web.Response(
            text=matched_route['response'], 
            status=matched_route['response_code']
        )
    else:
        log_message = f"404 Not Found | Path: {path} | IP: {ip_address} | User-Agent: {user_agent}"
        logging.info(log_message)
        # await send_telegram_message(bot_token, chat_id, log_message)
        return web.Response(text="404 Not Found", status=404)

# Configure logging with daily rotation
def configure_logging(log_file):
    handler = TimedRotatingFileHandler(log_file, when='midnight', interval=1, backupCount=30)
    handler.suffix = "%Y-%m-%d"
    logging.basicConfig(level=logging.INFO, handlers=[handler], format='%(asctime)s - %(message)s')

# Main function to start the server
async def run_server(config_file, bot_token, chat_id, host="0.0.0.0", port=8080, log_file='server.log'):
    configure_logging(log_file)
    routes = await load_config(config_file)
    
    app = web.Application()
    app.add_routes([web.get("/{tail:.*}", lambda request: handle_request(request, routes, bot_token, chat_id))])
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host, port)
    logging.info(f"Starting server on {host}:{port}")
    await site.start()

if __name__ == "__main__":
    CONFIG_FILE = "config.yaml"
    TELEGRAM_BOT_TOKEN = "your_bot_token_here"
    TELEGRAM_CHAT_ID = "your_chat_id_here"
    LOG_FILE = "server.log"  # Log file name

    # Run the server
    import asyncio
    asyncio.run(run_server(CONFIG_FILE, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, log_file=LOG_FILE))

