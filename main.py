#!/usr/bin/env python
# pylint: disable=unused-argument, wrong-import-position
# This program is dedicated to the public domain under the CC0 license.

"""
Don't forget to enable inline mode with @BotFather

First, a few handler functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic inline bot example. Applies different text transformations.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""
import logging
import sqlite3
from html import escape
import random
from uuid import uuid4
from telegram import __version__ as TG_VER

'''database = sqlite3.connect("quotes.db")
cur = database.cursor()
res = cur.execute("""INSERT INTO quotes VALUES (1, 'quote1'),(2, 'quote2'),(3, 'quote3');""")
database.commit() '''

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )
from telegram import InlineQueryResultArticle, InputTextMessageContent, Update
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes, InlineQueryHandler

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)
def generate_reply():
    replies = """
              Hello
              Goodbye
              Thanks!
              Your welcome!
              See you around!""".splitlines()
    r = random.choice(replies).strip()
    return r
async def inline_query(update, context):
    results = [
        InlineQueryResultArticle(
            id=str(uuid4()),
            title="random",
            input_message_content=InputTextMessageContent(generate_reply())
        )
    ]
    await update.inline_query.answer(results, cache_time=0)

"""async def inline_query(update, context):
    database = sqlite3.connect("quotes.db")
    cur = database.cursor()
    res = cur.execute("SELECT quote FROM quotes ORDER BY RANDOM() LIMIT 1;")
    result = str(res.fetchall())
    database.close()
    results = [
        InlineQueryResultArticle(
            id=str(uuid4()),
            title="random",
            input_message_content=InputTextMessageContent(result)
        )
    ]
    await update.inline_query.answer(results, cache_time=0)"""

def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token("5822167170:AAFDQIpoijIpRR49-CMfkaZ7DNs-m7uLYQU").build()
    application.add_handler(InlineQueryHandler(inline_query))
    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()