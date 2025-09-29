import os
import logging
from datetime import datetime
from urllib.parse import quote_plus
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ========= CONFIG =========
BOT_TOKEN = os.environ.get("BOT_TOKEN")
BLOG_REDIRECT = "https://onlinemoneymakers123.blogspot.com"
LOG_LEVEL = logging.INFO
# ==========================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=LOG_LEVEL
)
logger = logging.getLogger(__name__)

START_YEAR = 2007
CURRENT_YEAR = datetime.now().year

# Latest CBSE SQP pages
CLASS10_LATEST = "https://cbseacademic.nic.in/sqp_classx_2023-24.html"
CLASS12_LATEST = "https://cbseacademic.nic.in/sqp_classxii_2023-24.html"


def main_menu():
    """Return the main menu keyboard."""
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

    # ---- Main menu ----
    if data == "back_main":
        await query.edit_message_text("📚 Back to main menu:", reply_markup=main_menu())

    # ---- JEE Advanced → Year ----
    elif data == "cat_jee_advanced":
        years = [str(y) for y in range(START_YEAR, CURRENT_YEAR + 1)]
        keyboard = [
            [InlineKeyboardButton(year, callback_data=f"year_jee_advanced_{year}")]
            for year in years
        ]
        keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="back_main")])
        await query.edit_message_text(
            "📅 Choose JEE Advanced Year:", reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # ---- JEE Advanced Year → Papers ----
    elif data.startswith("year_jee_advanced_"):
        year = data.split("_")[-1]
        keyboard = [
            [InlineKeyboardButton("Paper 1", callback_data=f"paper_jee_advanced_{year}_1")],
            [InlineKeyboardButton("Paper 2", callback_data=f"paper_jee_advanced_{year}_2")],
            [InlineKeyboardButton("⬅️ Back", callback_data="cat_jee_advanced")],
        ]
        await query.edit_message_text(
            f"📑 Choose Paper ({year}):", reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # ---- JEE Advanced Paper → Redirect ----
    elif data.startswith("paper_jee_advanced_"):
        _, _, _, year, paper = data.split("_")
        url = f"https://jeeadv.ac.in/past_qps/{year}_{paper}_English.pdf"
        redirect_link = f"{BLOG_REDIRECT.rstrip('/')}/?target={quote_plus(url)}"
        keyboard = [[InlineKeyboardButton("⬅️ Back", callback_data=f"year_jee_advanced_{year}")]]
        await query.edit_message_text(
            f"✅ JEE Advanced {year} - Paper {paper}\n"
            f"🔗 Redirect link: {redirect_link}",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

    # ---- Class 10 → Latest SQP Redirect ----
    elif data == "cat_class_10":
        redirect_link = f"{BLOG_REDIRECT.rstrip('/')}/?target={quote_plus(CLASS10_LATEST)}"
        keyboard = [[InlineKeyboardButton("⬅️ Back", callback_data="back_main")]]
        await query.edit_message_text(
            f"✅ Class 10 Latest SQPs\n🔗 Redirect link: {redirect_link}",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

    # ---- Class 12 → Latest SQP Redirect ----
    elif data == "cat_class_12":
        redirect_link = f"{BLOG_REDIRECT.rstrip('/')}/?target={quote_plus(CLASS12_LATEST)}"
        keyboard = [[InlineKeyboardButton("⬅️ Back", callback_data="back_main")]]
        await query.edit_message_text(
            f"✅ Class 12 Latest SQPs\n🔗 Redirect link: {redirect_link}",
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


if __name__ == "__main__":
    main()
