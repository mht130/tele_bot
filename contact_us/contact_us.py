import telebot
from telebot import apihelper
import logging


logging.basicConfig(filename = 'contact.log',
                    level = logging.DEBUG,
                    format = '%(asctime)s:%(levelname)s:%(name)s:%(message)s')

TOKEN="5534653365:AAFxMAB1uV095lnTGkgjGt76QRP1_ZmPwQY"

proxies={'https':'socks5h://127.0.0.1:9050'}

apihelper.proxy=proxies

bot=telebot.TeleBot(TOKEN)
 


admin_id="413859869"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    text=f"سلام \n پیام خود را ارسال کنید"
    bot.send_message(message.chat.id,text)

@bot.message_handler(func=lambda m : True)
def text_handler(message):
    msg_to_admin=f"@{message.from_user.username} \n{message.from_user.id}\n{message.text}"
    bot.send_message(admin_id, msg_to_admin)
    bot.send_message(message.chat.id, "ممنون از بازخورد شما \n /start")


bot.infinity_polling()