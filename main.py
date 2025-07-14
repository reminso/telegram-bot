import os
from flask import Flask, request
from bot import TelegramBot
from keep_alive import keep_alive, setup_webhook
import threading
import time

app = Flask(__name__)

# Initialize the bot
bot = TelegramBot()

@app.route('/')
def home():
    return "Telegram Bot is running!"

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming Telegram updates"""
    update = request.get_json()
    bot.handle_update(update)
    return 'OK'

if __name__ == '__main__':
    # Start keep-alive service
    keep_alive()
    
    # Setup webhook after a short delay
    def delayed_webhook_setup():
        time.sleep(10)  # Wait for server to start
        setup_webhook()
    
    webhook_thread = threading.Thread(target=delayed_webhook_setup, daemon=True)
    webhook_thread.start()
    
    # Start the Flask app
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
