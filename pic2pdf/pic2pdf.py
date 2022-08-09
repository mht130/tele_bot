import telebot
from telebot import apihelper,types
import os
import requests
from fpdf import FPDF
import cv2
import logging


logging.basicConfig(filename = 'pic2pdf.log',
                    level = logging.DEBUG,
                    format = '%(asctime)s:%(levelname)s:%(name)s:%(message)s')

TOKEN="5015061212:AAGgXg59wVyo6SQx8ED6QfHcui3UQPswayM"


proxies={'https':'socks5h://127.0.0.1:9050'}

apihelper.proxy=proxies
bot=telebot.TeleBot(TOKEN)

channels=[
    ["@mht_programing","channel 1"],
    ["@poshtibani_robot_0","channel 2"]
]

pictures_list=[]

def downloader(url,name):
    file_=requests.get(url,proxies=proxies)
    # os.system(f"touch {name}")
    with open(f"./Download/{name}",'wb') as f:
        f.write(file_.content)

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


def make_pdf(file_path:list,name):
    global pictures_list
    pdf = FPDF()
    for image in file_path:
        img=cv2.imread(f"./Download/{image}")
        shape=img.shape
        if shape[0]>=shape[1]:
            pdf.add_page(orientation="P")
            if shape[0]>297 or shape[1]>210:
                pdf.image(f"./Download/{image}",0,0,210,297)
            else:
                pdf.image(f"./Download/{image}",0,0,shape[1],shape[0])
        else:
            pdf.add_page(orientation="L")
            if shape[1]>297 or shape[0]>210:
                pdf.image(f"./Download/{image}",0,0,297,210)
            else:
                pdf.image(f"./Download/{image}",0,0,shape[1],shape[0])
        os.system(f"rm ./Download/{image}")
    pdf.output(name, "F")
    pictures_list=[]
    # os.system(command)
@bot.message_handler(commands=['start','help'])
def send_welcome(message):
    chat_id=message.chat.id
    user_id=message.from_user.id
    first_name=message.from_user.first_name
    if is_joind(channels, user_id):
        bot.send_message(chat_id, f"Hello {first_name}, Please Send pictures and send '/end' after it completed its processing.")
    else:
        keyboard=join_inline_keyboard_maker(channels)
        bot.send_message(chat_id,f"Hello {first_name},Please join this channels before using the bot ",reply_markup=keyboard)

@bot.message_handler(commands=['end'])
def end_handler(message):
    chat_id=message.from_user.id
    user_username=message.from_user.username
    user_id=message.from_user.id
    message_id=message.id
    name=f"{user_username}__{user_id}__{message_id}.pdf"
    make_pdf(pictures_list,name)
    doc=open(f"{name}",'rb')
    bot.send_document(chat_id, doc)
    os.system(f"rm {name}")

@bot.message_handler(content_types=['photo'])
def photo_handler(message):
    global pictures_list
    user_id=message.from_user.id
    user_username=message.from_user.username
    chat_id=message.chat.id
    if is_joind(channels, user_id):
        res = bot.send_message(message.chat.id, f"Processing...")
        i=message.photo[-1]
        file_path=bot.get_file(i.file_id).file_path
        photo_url=f"https://api.telegram.org/file/bot{TOKEN}/{file_path}"
        file_name=f"{user_username}__{user_id}_{i.file_id}_{file_path.replace('/','*')}"
        downloader(photo_url,file_name)
        bot.edit_message_text("Done",message.chat.id,res.id)
        pictures_list.append(file_name)
    else:
        keyboard=join_inline_keyboard_maker(channels)
        bot.send_message(chat_id,"Please join the channels",reply_markup=keyboard)

bot.infinity_polling()