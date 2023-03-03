import logging
import sqlite3
from uuid import uuid4
from telegram import __version__ as TG_VER, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineQueryResultArticle, \
    InputTextMessageContent, Update
from telegram.ext import Application, CommandHandler, ContextTypes, InlineQueryHandler, MessageHandler, filters, \
    ConversationHandler

# Assigns token number from .txt file to variable
with open('Token.txt') as f:
    token = f.readline()

# Version control
try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )

# Enable logging.
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

ADD, REMOVE, SLEEP, CHOOSING, CANCEL = range(5)


# Function to clean string received from SQL database.
def clean(SQL_str):
    return SQL_str.replace('(', '').replace(')', '').replace('[', '').replace(']', '').replace(',', '').replace("'", '')


# Function that used to find new id when inserting quote into database.
def find_new_id():
    database = sqlite3.connect("quotes.db")
    cur = database.cursor()
    res = cur.execute("SELECT id FROM quotes ORDER BY id DESC LIMIT 1;")
    res = clean(str(res.fetchall()))
    database.close()
    return int(res) + 1


# returns random row from SQL database.
def generate_reply():
    database = sqlite3.connect("quotes.db")
    cur = database.cursor()
    res = cur.execute("SELECT quote FROM quotes ORDER BY RANDOM() LIMIT 1;")
    r = clean(str(res.fetchall()))
    database.close()
    return r


# This function sends random quote to a chat via inline query.
async def inline_query(update, context):
    results = [
        InlineQueryResultArticle(
            id=str(uuid4()),
            title="random",
            input_message_content=InputTextMessageContent(generate_reply())
        )
    ]
    await update.inline_query.answer(results, cache_time=0)


# Creates reply keyboard, allowing to add or remove rows from database
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reply_keyboard = [["Add quote", "Remove quote", "Cancel"]]
    await update.message.reply_text(
        "please chose one of the options.",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    logger.info("admin have been called")
    return CHOOSING


# Sets ConversationHandler state depending on what have been pressed on reply keyboard.
async def choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    if text == "Add quote":
        await update.message.reply_text("Enter new quote")
        return ADD
    if text == "Remove quote":
        await update.message.reply_text("Enter id of quote you wish to remove (you can see it using /inspect command")
        return REMOVE
    else:
        await update.message.reply_text("Canceled")
        return ConversationHandler.END


# Shows all quotes in database
async def inspect(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    database = sqlite3.connect("quotes.db")
    cur = database.cursor()
    res = cur.execute("SELECT * FROM quotes;")
    r = clean(str(res.fetchall()))
    database.close()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=r)
    logger.info("Inspection have been done")
    return ConversationHandler.END


# Inserts quote in database
async def insert(update: Update, context: ContextTypes.DEFAULT_TYPE):
    quote = update.message.text
    database = sqlite3.connect("quotes.db")
    cur = database.cursor()
    cur.execute("INSERT INTO quotes(id, quote) VALUES(?, ?);", (find_new_id(), quote))
    database.commit()
    database.close()
    await update.message.reply_text("Quote " + quote + " have been added.")
    logger.info("insertion have been done")
    return ConversationHandler.END


# Removes quote from database
async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    id_number = int(update.message.text)
    database = sqlite3.connect("quotes.db")
    cur = database.cursor()
    cur.execute("DELETE FROM quotes WHERE id = ?;", [id_number])
    database.commit()
    database.close()
    await update.message.reply_text("Quote number " + str(id_number) + " has been removed.")
    logger.info("deletion have been done")
    return ConversationHandler.END


# Abort operation
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    logger.info("User %s aborted operation.", user.last_name)
    await update.message.reply_text("Operation aborted.", reply_markup=ReplyKeyboardRemove())
    logger.info("cancel has been called")
    return ConversationHandler.END


# Run the bot
def main() -> None:
    # Create the Application and pass it your bot token.
    application = Application.builder().token(token.strip()).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("admin", admin)],
        states={
            CHOOSING: [MessageHandler(filters.TEXT & ~filters.COMMAND, choice)],
            ADD: [MessageHandler(filters.TEXT & ~filters.COMMAND, insert)],
            REMOVE: [MessageHandler(filters.TEXT & ~filters.COMMAND, delete)],
            CANCEL: [CommandHandler("cancel", cancel)]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    application.add_handler(conv_handler)
    application.add_handler(InlineQueryHandler(inline_query))
    application.add_handler(CommandHandler("inspect", inspect))
    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()
