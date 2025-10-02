import os
import logging
from datetime import datetime
from urllib.parse import quote_plus
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from flask import Flask
import threading

# ========= CONFIG =========
BOT_TOKEN = os.environ.get("BOT_TOKEN")
BLOG_URL = "https://freejeeresources.blogspot.com"
LOG_LEVEL = logging.INFO
# ==========================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=LOG_LEVEL
)
logger = logging.getLogger(__name__)

START_YEAR = 2007
CURRENT_YEAR = datetime.now().year

# Base URLs for content
JEE_ADV_BASE = "https://jeeadv.ac.in/past_qps"
CLASS10_LATEST = "https://cbseacademic.nic.in/sqp_classx_2023-24.html"
CLASS12_LATEST = "https://cbseacademic.nic.in/sqp_classxii_2023-24.html"

def main_menu():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("📕 JEE Advanced PYQs", callback_data="cat_jee_advanced")],
            [InlineKeyboardButton("📘 Class 10 SQPs", callback_data="cat_class_10")],
            [InlineKeyboardButton("📗 Class 12 SQPs", callback_data="cat_class_12")],
        ]
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📚 Welcome! Choose a category:", reply_markup=main_menu()
    )

async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "back_main":
        await query.edit_message_text("📚 Back to main menu:", reply_markup=main_menu())

    # JEE Advanced Year
    elif data == "cat_jee_advanced":
        years = [str(y) for y in range(START_YEAR, CURRENT_YEAR + 1)]
        keyboard = [[InlineKeyboardButton(year, callback_data=f"year_jee_advanced_{year}")] for year in years]
        keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="back_main")])
        await query.edit_message_text("📅 Choose JEE Advanced Year:", reply_markup=InlineKeyboardMarkup(keyboard))

    # JEE Advanced Papers
    elif data.startswith("year_jee_advanced_"):
        year = data.split("_")[-1]
        keyboard = [
            [InlineKeyboardButton("Paper 1", callback_data=f"paper_jee_advanced_{year}_1")],
            [InlineKeyboardButton("Paper 2", callback_data=f"paper_jee_advanced_{year}_2")],
            [InlineKeyboardButton("⬅️ Back", callback_data="cat_jee_advanced")],
        ]
        await query.edit_message_text(f"📑 Choose Paper ({year}):", reply_markup=InlineKeyboardMarkup(keyboard))

    # Generate redirect links like your example
    elif data.startswith("paper_jee_advanced_"):
        _, _, _, year, paper = data.split("_")
        pdf_url = f"{JEE_ADV_BASE}/{year}_{paper}_English.pdf"
        redirect_link = f"{BLOG_URL}/?target={quote_plus(pdf_url)}"
        keyboard = [[InlineKeyboardButton("⬅️ Back", callback_data=f"year_jee_advanced_{year}")]]
        await query.edit_message_text(
            f"✅ JEE Advanced {year} - Paper {paper}\n🔗 {redirect_link}",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

    # Class 10 SQPs
    elif data == "cat_class_10":
        redirect_link = f"{BLOG_URL}/?target={quote_plus(CLASS10_LATEST)}"
        keyboard = [[InlineKeyboardButton("⬅️ Back", callback_data="back_main")]]
        await query.edit_message_text(
            f"✅ Class 10 Latest SQPs\n🔗 {redirect_link}",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

    # Class 12 SQPs
    elif data == "cat_class_12":
        redirect_link = f"{BLOG_URL}/?target={quote_plus(CLASS12_LATEST)}"
        keyboard = [[InlineKeyboardButton("⬅️ Back", callback_data="back_main")]]
        await query.edit_message_text(
            f"✅ Class 12 Latest SQPs\n🔗 {redirect_link}",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

def main():
    if not BOT_TOKEN:
        print("ERROR: BOT_TOKEN not set in environment variables.")
        return

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(menu_handler))

    print("Bot started ✅ Use /start in Telegram")
    app.run_polling()

# Flask keep-alive
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "🤖 Bot is running ✅"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    flask_app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    main()
