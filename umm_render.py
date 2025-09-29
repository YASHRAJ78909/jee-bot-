import os
import io
import logging
from typing import List
import requests
from urllib.parse import quote_plus
from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, ContextTypes

# -------- CONFIG ----------
BOT_TOKEN = os.environ.get("BOT_TOKEN")
BASE = os.environ.get("JEE_BASE", "https://jeeadv.ac.in/past_qps")
BLOG_REDIRECT = os.environ.get("BLOG_REDIRECT", "https://onlinemoneymakers123.blogspot.com")
SEND_DIRECT = os.environ.get("SEND_DIRECT", "false").lower() == "true"
LOG_LEVEL = logging.INFO
# --------------------------

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=LOG_LEVEL
)
logger = logging.getLogger(__name__)


def candidate_urls(year: str, paper: str = None) -> List[str]:
    yr = year.strip()
    patterns = []
    papers = [paper] if paper in ("1", "2") else ["1", "2"]
    suffixes = ["", "_English", "_Hindi"]
    for p in papers:
        for s in suffixes:
            patterns.append(f"{BASE}/{yr}_{p}{s}.pdf")
        patterns.append(f"{BASE}/{yr}{p}.pdf")
    seen = []
    out = []
    for u in patterns:
        if u not in seen:
            seen.append(u)
            out.append(u)
    return out


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✅ JEE-PYQ Bot ready.\n"
        "Usage:\n"
        "/pyq <year>            - sends Paper 1 & 2 (if available), e.g. /pyq 2014\n"
        "/pyq <year> <1|2>      - sends a specific paper, e.g. /pyq 2019 1\n"
        "Available years: official archive goes back to 2007.\n\n"
        f"Redirect target: {BLOG_REDIRECT}\n"
        "Set SEND_DIRECT=true to continue sending PDFs directly to Telegram."
    )


async def pyq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /pyq <year> [paper]\nExample: /pyq 2012 1")
        return

    year = context.args[0].strip()
    paper = context.args[1].strip() if len(context.args) > 1 else None

    if not year.isdigit() or int(year) < 2007 or int(year) > 2100:
        await update.message.reply_text("Please supply a valid year (>=2007). Example: /pyq 2015")
        return

    urls = candidate_urls(year, paper)
    await update.message.reply_text(f"🔎 Looking for official JEE (Advanced) papers for {year}...")

    found_any = False
    tried = []
    for url in urls:
        tried.append(url)
        try:
            resp = requests.get(url, timeout=15)
            if resp.status_code == 200 and resp.headers.get("content-type", "").lower().startswith("application/pdf"):
                fname = url.split("/")[-1]
                redirect_link = f"{BLOG_REDIRECT.rstrip('/')}/?target={quote_plus(url)}"
                await update.message.reply_text(f"✅ Found: {fname}\nRedirect link: {redirect_link}")
                found_any = True

                if SEND_DIRECT:
                    bio = io.BytesIO(resp.content)
                    bio.name = fname
                    bio.seek(0)
                    await update.message.reply_document(document=InputFile(bio, filename=fname))

                if paper in ("1", "2"):
                    return
            else:
                continue
        except Exception as e:
            logger.debug("Error fetching %s : %s", url, e)
            continue

    if not found_any:
        msg = (
            "⚠️ Couldn't find official PDF on the site using common filenames.\n\n"
            "I tried these URLs (some may exist):\n" + "\n".join(tried[:6]) + "\n\n"
            "What you can do:\n"
            f"• If you want to check the link manually, here's a helpful blog redirect template:\n"
            f"  {BLOG_REDIRECT.rstrip('/')}/?target=<url-encoded-pdf-url>\n\n"
            "• Visit the official archive: https://jeeadv.ac.in/archive.html\n"
            "• If you see a working PDF link on that page, paste it here and I can fetch it.\n"
        )
        await update.message.reply_text(msg)


def main():
    if not BOT_TOKEN:
        print("ERROR: BOT_TOKEN not set in environment variables.")
        return
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("pyq", pyq))
    print("Bot started. Use /pyq <year> [paper].")

    # Start Flask keep-alive server in a thread
    from flask import Flask
    from threading import Thread

    flask_app = Flask(__name__)

    @flask_app.route('/')
    def home():
        return "Bot is running!"

    def run():
        flask_app.run(host="0.0.0.0", port=8080)

    Thread(target=run).start()

    app.run_polling()


if __name__ == "__main__":
    main()
