import os
from http.server import BaseHTTPRequestHandler
import json
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = Bot(token=TOKEN)

# Simple global sets/lists (Note: For persistent production storage across serverless spins, 
# connect a database like Vercel KV. For basic operation, chats are recorded dynamically).
KNOWN_CHATS = set()
STORED_BROADCASTS = {"morning": "Default Morning Broadcast", "night": "Default Night Broadcast"}

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    KNOWN_CHATS.add(chat_id)
    await update.message.reply_text("🤖 Bot is active and connected! Send /setmorning <text> or /setnight <text> to save broadcasts.")

async def handle_my_chat_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Automatically captures group IDs when the bot is added to them
    chat = update.effective_chat
    if chat:
        KNOWN_CHATS.add(chat.id)

async def set_morning(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args)
    if text:
        STORED_BROADCASTS["morning"] = text
        await update.message.reply_text(f"✅ Morning broadcast saved:\n\n{text}")
    else:
        await update.message.reply_text("⚠️ Please provide text. Example: /setmorning Good morning traders!")

async def set_night(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args)
    if text:
        STORED_BROADCASTS["night"] = text
        await update.message.reply_text(f"✅ Night broadcast saved:\n\n{text}")
    else:
        await update.message.reply_text("⚠️ Please provide text. Example: /setnight Good evening market review.")

# Build PTB application
application = Application.builder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start_command))
application.add_handler(CommandHandler("setmorning", set_morning))
application.add_handler(CommandHandler("setnight", set_night))
application.add_handler(MessageHandler(filters.ChatType.GROUPS, handle_my_chat_member))

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            update_data = json.loads(post_data.decode('utf-8'))
            update = Update.de_json(update_data, bot)
            
            # Process update asynchronously via runner loop
            import asyncio
            asyncio.run(application.initialize())
            asyncio.run(application.process_update(update))
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
