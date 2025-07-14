import threading
import time
import requests
import os
from flask import Flask

def keep_alive():
    """Keep the server alive by pinging it every 5 minutes"""
    def run():
        while True:
            try:
                # Get the current Replit URL
                replit_url = os.getenv('REPL_URL', 'http://localhost:5000')
                response = requests.get(replit_url)
                print(f"Keep-alive ping: {response.status_code}")
            except Exception as e:
                print(f"Keep-alive error: {e}")
            time.sleep(300)  # 5 minutes
    
    thread = threading.Thread(target=run, daemon=True)
    thread.start()

def setup_webhook():
    """Automatically setup webhook when server starts"""
    try:
        # Get the Replit URL
        replit_url = os.getenv('REPL_URL')
        if not replit_url:
            # Try alternative environment variables
            replit_domain = os.getenv('REPLIT_DEV_DOMAIN')
            if replit_domain:
                replit_url = f"https://{replit_domain}"
            else:
                print("REPL_URL not found, skipping webhook setup")
                return
        
        # Bot token
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '7806556716:AAHWEGa3PbYYfYraQBhMrxyVRxxbym_DfZo')
        
        # Set webhook
        webhook_url = f"{replit_url}/webhook"
        api_url = f"https://api.telegram.org/bot{bot_token}/setWebhook"
        
        response = requests.post(api_url, json={'url': webhook_url})
        result = response.json()
        
        if result.get('ok'):
            print(f"✅ Webhook successfully set to: {webhook_url}")
        else:
            print(f"❌ Webhook setup failed: {result}")
            
    except Exception as e:
        print(f"❌ Error setting up webhook: {e}")