import telebot
from telebot import apihelper,types
from googletrans import Translator
import googletrans
import logging


logging.basicConfig(filename = 'google_translate.log',
                    level = logging.DEBUG,
                    format = '%(asctime)s:%(levelname)s:%(name)s:%(message)s')

TOKEN="5456647357:AAElzvwILKEB4XywbG3_trbEbmbg7yYc3TM"


proxies={'https':'socks5h://127.0.0.1:9050'}

apihelper.proxy=proxies
bot=telebot.TeleBot(TOKEN)

channels=[
    ["@mht_programing","channel 1"],
    ["@poshtibani_robot_0","channel 2"]
]

all_langs=googletrans.LANGUAGES
all_langs1=[i for i in googletrans.LANGUAGES]

translate_to="auto"

def core_msg(translate_to,all_langs):
        if translate_to=="auto":
            target_lang='auto'
        elif translate_to=="Default":
            target_lang='Default'
        else:
            target_lang=all_langs[translate_to]
        core_msg=f"  متن خود را ارسال کنید \nSend your text \n زبان مقصد : {target_lang} \n برای تغییر زبان مقصد :‌\n/change_lang \n زبان مبدا به صورت خودکار شناسایی می شود"
        return core_msg

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


@bot.message_handler(commands=list(all_langs.keys())+['auto','Default'])
def language_handler(message):
    chat_id=message.chat.id
    user_id=message.from_user.id
    if is_joind(channels, user_id):
        global translate_to
        if message.text.replace("/",'')=='Default':
            lang='en'
        else:
            lang=message.text.replace("/",'')
        translate_to=lang
        if translate_to=="auto":
            target_lang='auto'
        elif translate_to=="Default":
            target_lang='Default'
        else:
            target_lang=all_langs[translate_to]
               
        bot.send_message(chat_id,core_msg(translate_to,all_langs))
    else:
        keyboard=join_inline_keyboard_maker(channels)
        bot.send_message(chat_id,f"Hello {first_name},Please join channels before using the bot ",reply_markup=keyboard)


@bot.message_handler(commands=['change_lang'])
def change_lang_handler(message):
    chat_id=message.chat.id
    user_id=message.from_user.id
    first_name=message.from_user.first_name
    if is_joind(channels, user_id):
        change_lang_text="choose the language you want to translate into : \n\n/auto(فارسی را به انگلیسی و انگلیسی را به فارسی تبدیل می کند) \n\n /Default (English) \n "
        for i,j in all_langs.items():
            change_lang_text+=f"/{i} - {j}\n"
        bot.send_message(chat_id, change_lang_text)
    else:
        keyboard=join_inline_keyboard_maker(channels)
        bot.send_message(chat_id,f"Hello {first_name},Please join channels before using the bot ",reply_markup=keyboard)


@bot.message_handler(commands=['start','help'])
def send_welcome(message):
    chat_id=message.chat.id
    user_id=message.from_user.id
    first_name=message.from_user.first_name
    if is_joind(channels, user_id):
        bot.send_message(chat_id, core_msg(translate_to,all_langs))
    else:
        keyboard=join_inline_keyboard_maker(channels)
        bot.send_message(chat_id,f"Hello {first_name},Please join channels before using the bot ",reply_markup=keyboard)


@bot.message_handler(func=lambda m : True)
def text_handler(message):
    chat_id=message.chat.id
    user_username=message.from_user.username
    user_id=message.from_user.id
    if is_joind(channels, user_id):
        text=message.text
        translator=Translator()
        detect=translator.detect(text)
        if translate_to=='auto':
            if detect.lang=='en':
                t=translator.translate(text,dest='fa')
            else:
                t=translator.translate(text,dest='en')
        else:
            t=translator.translate(text,dest=translate_to)

        bot.send_message(chat_id, t.text)       
        bot.send_message(chat_id,core_msg(translate_to,all_langs))

    else:
        keyboard=join_inline_keyboard_maker(channels)
        bot.send_message(chat_id,"Please join the channels",reply_markup=keyboard)

bot.infinity_polling()