import telebot
from telebot import apihelper,types
import os
from gtts import gTTS
import logging


logging.basicConfig(filename = 'text2speech.log',
                    level = logging.DEBUG,
                    format = '%(asctime)s:%(levelname)s:%(name)s:%(message)s')

TOKEN="5421466081:AAE-2LHqjhuRv3DA_KlpAb-wpN10HUAo3t4"


proxies={'https':'socks5h://127.0.0.1:9050'}

apihelper.proxy=proxies
bot=telebot.TeleBot(TOKEN)

channels=[
    ["@mht_programing","channel 1"],
    ["@poshtibani_robot_0","channel 2"]
]

pictures_list=[]

def is_joind(channels,user_id):
    joind_check=[]
    for i in channels:
        members=bot.get_chat_member(i[0], user_id)
        if members.status=="left":
            joind_check.append(False)
        else:
            joind_check.append(True)
    if all(joind_check):
        return True
    return False

def join_inline_keyboard_maker(channels):
    inline_keyboard=types.InlineKeyboardMarkup(row_width=2)
    for i in channels:
        inline_keyboard.add(
            types.InlineKeyboardButton(i[1],url=f"https://t.me/{i[0].replace('@','')}")
        )
    return inline_keyboard


@bot.message_handler(commands=['start','help'])
def send_welcome(message):
    chat_id=message.chat.id
    user_id=message.from_user.id
    first_name=message.from_user.first_name
    if is_joind(channels, user_id):
        bot.send_message(chat_id, f"Hello {first_name}, Please Send text please")
    else:
        keyboard=join_inline_keyboard_maker(channels)
        bot.send_message(chat_id,f"Hello {first_name},Please join this channels before using the bot ",reply_markup=keyboard)

@bot.message_handler(func=lambda m : True)
def text_handler(message):
    chat_id=message.chat.id
    user_username=message.from_user.username
    user_id=message.from_user.id
    if is_joind(channels, user_id):
        text=message.text
        lang='en'
        audio=gTTS(text,lang=lang)
        file_name=f"{user_username}__{message.id}__.mp3"
        audio.save(file_name)
        mp3_file=open(f"{user_username}__{message.id}__.mp3",'rb')
        bot.send_audio(chat_id, mp3_file)
        os.system(f"rm {file_name}")
    else:
        keyboard=join_inline_keyboard_maker(channels)
        bot.send_message(chat_id,"Please join the channels",reply_markup=keyboard)

bot.infinity_polling()