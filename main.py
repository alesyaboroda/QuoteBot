import logging
import sqlite3
from uuid import uuid4
from telegram import __version__ as TG_VER
with open('Token.txt') as f:
    token = f.readline()
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
from telegram.ext import Application, CommandHandler, ContextTypes, InlineQueryHandler

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# returns random row from SQL database
def generate_reply():
    database = sqlite3.connect("quotes.db")
    cur = database.cursor()
    res = cur.execute("SELECT quote FROM quotes ORDER BY RANDOM() LIMIT 1;")
    r = str(res.fetchall())
    database.close()
    return r

async def inline_query(update, context):
    results = [
        InlineQueryResultArticle(
            id=str(uuid4()),
            title="random",
            input_message_content=InputTextMessageContent(generate_reply().strip())
        )
    ]
    await update.inline_query.answer(results, cache_time=0)

def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(token.strip()).build()
    application.add_handler(InlineQueryHandler(inline_query))
    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()