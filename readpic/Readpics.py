import pytesseract
import numpy as np
import os
import cv2
import telebot
from telebot import apihelper
from telebot import types
import requests
import csv
import logging


logging.basicConfig(filename = 'readpics.log',
                    level = logging.DEBUG,
                    format = '%(asctime)s:%(levelname)s:%(name)s:%(message)s')

TOKEN="5476554887:AAGSf3DWkg8_sEruCl8DAZ5NTSqdueRpBVo"
proxies={'https':'socks5h://127.0.0.1:9050'}

apihelper.proxy=proxies
bot=telebot.TeleBot(TOKEN)

lang="fas"

channels=[
    ["@mht_programing","channel 1"],
    ["@poshtibani_robot_0","channel 2"]
]

messages={
    "pls_join_msg":["Plese join these channels","لطفا در کانال های زیر عضو شوید"],
    "send_img":["send image please","عکس را ارسال کنید"],
}


@bot.message_handler(commands=['start','help'])
def send_welcome(message):
    user_id=message.from_user.id
    if is_joind(channels, user_id):
        bot.send_message(user_id, f"Hello {message.from_user.first_name}, Send your image")
    else:
        keyboard=join_inline_keyboard_maker(channels)
        if lang=="eng":
            res_lang=0
        else:
            res_lang=1
        bot.send_message(chat_id,messages["pls_join_msg"][res_lang],reply_markup=keyboard)

@bot.message_handler(func=lambda m : True)
def message_handler(message):
    global lang
    user_id=message.from_user.id
    if is_joind(channels, user_id):
        if message.text=='English':
            lang="eng"
            bot.send_message(message.chat.id, f"Send your image")
        elif message.text=='Farsi':
            lang="fas"
            bot.send_message(message.chat.id, f"تصویر را ارسال کنید ")
        else:
            lang="fas"
            bot.send_message(message.chat.id, f"Invalid input, Default language is Farsi \n ورودی نا معتبر زبان پیشفرض فارسی است")
    else:
        if lang=="eng":
            res_lang=0
        else:
            res_lang=1
        keyboard=join_inline_keyboard_maker(channels)  
        bot.send_message(user_id,messages["pls_join_msg"][res_lang],reply_markup=keyboard)

@bot.message_handler(content_types=['photo'])
def photo_handler(message):
    global lang
    user_id=message.from_user.id
    user_username=message.from_user.username
    if is_joind(channels, user_id):
        res = bot.send_message(message.chat.id, f"Processing...")
        i=message.photo[-1]
        file_path=bot.get_file(i.file_id).file_path
        photo_url=f"https://api.telegram.org/file/bot{TOKEN}/{file_path}"
        file_name=f"{user_username}__{user_id}__{file_path.replace('/','*')}"
        downloader(photo_url,file_name)
        bot.edit_message_text("Done",message.chat.id,res.id)
        result=ReadImage(f"./Download/{file_name}",lang)
        if len(result)<=3:
            result="None"
        bot.send_message(message.chat.id, result)
        os.system(f"rm ./Download/{file_name}")
        os.system(f"rm result_text.txt")
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True,row_width=1,one_time_keyboard=False)
        itembtn1 = types.KeyboardButton('English')
        itembtn2 = types.KeyboardButton('Farsi')
        markup.add(itembtn1, itembtn2)
        bot.send_message(message.chat.id, "زبان ؟", reply_markup=markup)
    else:
        keyboard=join_inline_keyboard_maker(channels)
        bot.send_message(chat_id,"Please join the channels",reply_markup=keyboard)

def downloader(url,name):
    file_=requests.get(url,proxies=proxies)
    # os.system(f"touch {name}")
    with open(f"./Download/{name}",'wb') as f:
        f.write(file_.content)

def ReadImage(location,lang):
    img = cv2.imread(f"{location}")
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    kernel = np.ones((1, 1), np.uint8)
    img = cv2.dilate(img, kernel, iterations=1)
    img = cv2.erode(img, kernel, iterations=1)
    cv2.medianBlur(img, 5)
    details_fas = pytesseract.image_to_data(
        img, lang=lang, output_type=pytesseract.Output.DICT)
    total_boxes = len(details_fas['text'])
    for sequence_number in range(total_boxes):
        if float(details_fas['conf'][sequence_number]) > float(30):
            (x, y, w, h) = (details_fas['left'][sequence_number], details_fas['top'][sequence_number],
                            details_fas['width'][sequence_number],  details_fas['height'][sequence_number])
            img = cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
    parse_text = []
    word_list = []
    last_word = ''
    for word in details_fas['text']:
        if word != '' and word != None and word != " ":
            word_list.append(word)
            last_word = word
        if (last_word != '' and word == '') or (word == details_fas['text'][-1]):
            parse_text.append(word_list)
            word_list = []
        with open("result_text.txt", 'w+', newline="", encoding="utf-8") as file:
            csv.writer(file, delimiter=" ").writerows(parse_text)
    result = open("result_text.txt", 'r', encoding="utf-8").read()
    return result

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


bot.infinity_polling()
