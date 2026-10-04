import os
import json
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import requests

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        query_params = parse_qs(parsed_path.query)
        time_slot = query_params.get("time", ["morning"])[0]
        
        messages = {
            "morning": "☀️ Morning Trading Broadcast: Check out today's key setups!",
            "night": "🌙 Night Trading Broadcast: Reviewing today's market performance."
        }
        
        text_to_send = messages.get(time_slot, messages["morning"])
        target_chats = [] # Add your public group IDs here or bind to a persistent datastore
        
        success_count = 0
        for chat_id in target_chats:
            url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
            payload = {"chat_id": chat_id, "text": text_to_send}
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                success_count += 1

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"success": True, "sent_to": success_count}).encode('utf-8'))
