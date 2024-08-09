import logging
import datetime

import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


token = "7213571578:AAFZv2dP3rSatmLhFbMqSHetAQzNvKqOLZw"
trans_type =""

async def start(update: Update, context: CallbackQueryHandler)-> None:
    text = """<b>Welcome to Mybirrbot</b> \n
            This bot helps you get banks' rate of foreign currencies in real time, use the menu to list buying and selling of
            different currencies
            """
    await update.message.reply_text(text, parse_mode='html')


async def start1(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    keyboard = [
        [
            InlineKeyboardButton("Option 1", callback_data='1'),
            InlineKeyboardButton("Option 2", callback_data='2'),
        ],
        [InlineKeyboardButton("Option 3", callback_data='3')],
]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text('Please choose:', reply_markup=reply_markup)


def getCurrentRate(trans, currency):
    banks =['cbe','abay','zemen','nib','awash','berhan','abyssinia','amhara','wegagen','enat','ahadu','dashen','coop','gadaa']
    rates={}

    for bank in banks:
        res = requests.get("https://banksethiopia.com/wp-json/graph/v1/all?bankName=" + bank + "&dateRange=ThisMonth")
        data = res.json()
        rates[bank] = data[0][currency][trans][-1]
    x = dict(sorted(rates.items(), key=lambda x: x[1], reverse=True))
    text = ""
    for item in x.keys():
        text = text + "" + item + ":" + str(x[item]) + "\n"
    return text
def getOandaRate(currency):
    res = requests.get(
        "https://fxds-public-exchange-rates-api.oanda.com/cc-api/currencies?base=" + currency + "&quote=ETB&data_type=chart&start_date=2024-07-29&end_date=" + str(
            datetime.date.today()));
    data = res.json()
    return data['response'][-1]['average_bid']

async def getCurrencies(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    trans = trans_type.strip("/")
    currency = update.message.text
    if trans is None or len(trans) == 0:
        trans="buying"
    if trans =="oanda":
        text = getOandaRate(currency)
        await update.message.reply_text(text="Oanda bidding " + currency + " @ \n" + text, parse_mode='html')
    else:
        text=getCurrentRate(trans,currency)
        await update.message.reply_text(text="Banks "+trans+" "+ currency+" @ \n"+ text, parse_mode='html')

async def buying(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    globals()['trans_type'] = update.message.text
    reply_keyboard = [["USD","EUR","GBP"]]
    await update.message.reply_text('you selected buying',reply_markup=ReplyKeyboardMarkup(reply_keyboard))

async def selling(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    globals()['trans_type'] = update.message.text
    reply_keyboard = [["USD","EUR","GBP"]]
    await update.message.reply_text('you selected selling',reply_markup=ReplyKeyboardMarkup(reply_keyboard))

async def oanda(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    globals()['trans_type'] = update.message.text
    reply_keyboard = [["USD","EUR","GBP"]]
    await update.message.reply_text('you selected Oanda',reply_markup=ReplyKeyboardMarkup(reply_keyboard))

if __name__ == "__main__":

    application = ApplicationBuilder().token(token).build()

    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)
    application.add_handler(CommandHandler('buying', buying))
    application.add_handler(CommandHandler('selling', selling))
    application.add_handler(CommandHandler('oanda', oanda))
    application.add_handler(MessageHandler(filters.Regex("^(USD|EUR|GBP)$"), getCurrencies))
    application.run_polling(allowed_updates=Update.ALL_TYPES)

