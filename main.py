import telebot
from newsapi import NewsApiClient
from db import *
from config import token
from telebot import types
bot = telebot.TeleBot(token, parse_mode=None)

newsapi = NewsApiClient(api_key='4dd59dab99dd4eadbec05f5b77c34cac')

# блок старт для регистрации и выдачи основного меню
@bot.message_handler(commands=['start'])

def send_welcome(message):
  userid = [message.chat.id]
  connect = sqlite3.connect('base.db')
  cursor = connect.cursor()
  markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

  # делаем кнопочки
  itemNews = types.KeyboardButton('Новости✉️')
  itemSub = types.KeyboardButton('Подписки📱')
  itemCate = types.KeyboardButton('Категории📁')
  # добавляем кнопочки
  markup.add(itemCate, itemNews, itemSub)

  # ищем юзера по тг айди
  user = cursor.execute('SELECT * FROM users WHERE tg_id = ?;', (userid) ).fetchall()

  # если нет то добавляем если есть то он уже готовый
  if not user:
   # запрос на добавление юзера в базу
   cursor.execute('''INSERT INTO users('tg_id') VALUES(?);''', userid)
   connect.commit()
   bot.reply_to(message, "Вы успешно зарегистрированы ", reply_markup=markup)
  else:
   bot.reply_to(message, "Вы уже зарегистрированы", reply_markup=markup)


# и тут начинается
@bot.message_handler(content_types=['text'])
def bot_message(message):
  # нажатие на кнопку категории или же блок с категориями
  print(message.text)
  if message.chat.type == 'private':
    if message.text == 'Категории📁':
      markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
      connect = sqlite3.connect('base.db')
      cursor = connect.cursor()

      # получаем категории из базы
      categories = cursor.execute('SELECT * FROM categories ;').fetchall()

      # думал я как кнопки выводить и решил так их напихивать
      i=0
      while i<len(categories):
          # вот эта строчка вроде как не нужна но оставлю
          name =  str(categories[i][0])
          # а что он будет делать? - подписываться
          name = types.KeyboardButton("подписаться на " + categories[i][1])
          markup.add(name)

          i=i+1
      # кнопка для отката в основное меню
      back = types.KeyboardButton('Вернуться')
      markup.add(back)
      # даем ему команду и предлагаем че у нас есть
      bot.reply_to(message, "Подпишитесь на интересные вам категории:", reply_markup=markup)










  # работа с подписками
  if message.chat.type == 'private':
    # раз добавил подписаться то и будем обрабатывать по этому слову
    subs = "подписаться"
    if message.text.startswith(subs):
        userid = [message.chat.id]
        connect = sqlite3.connect('base.db')
        cursor = connect.cursor()
        # получаем айдишник юзера из базы
        id = cursor.execute('SELECT id FROM users WHERE tg_id=?;', (userid)).fetchone()
        # ту стр
        id=str(id[0])
        # получаем из подписок его
        sub = cursor.execute('SELECT * FROM sub INNER JOIN categories ON categories.id = sub.cate_id WHERE user_id = ?;',(id)).fetchall()
        # массив который не массив на самом деле для подписок
        arrSub = []
        i = 0
        while i <len(sub):
            arrSub.append(sub[i][3])
            i=i+1

        i=0
        count=0
        forWhat = message.text[15:]
        while i<len(arrSub):

            if forWhat == arrSub[i]:
                count=count+1
            i=i+1
        # если до этого не был то подписываем
        if count ==0:
            # получаем категорию по имени
            cate_id = cursor.execute('SELECT id FROM categories WHERE name=?;', (forWhat,)).fetchall()
            # складываем че есть и добавляем
            cursor.execute('''INSERT INTO sub('user_id', 'cate_id') VALUES(?,?);''', (id, cate_id[0][0]))
            connect.commit()

            bot.reply_to(message, "Вы успешно подписаны")
        else:
            # ну раз подписан то зачем
            bot.reply_to(message, "Вы уже подписаны")

















    # работа кнопки подписки
    # получаем подписки и выводим их
    if message.chat.type == 'private':
          if message.text == 'Подписки📱':
              markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
              userid = [message.chat.id]
              connect = sqlite3.connect('base.db')
              cursor = connect.cursor()
              # опять айдишник юзера надо бы это вынести а то че все одно и то же
              id = cursor.execute('SELECT id FROM users WHERE tg_id=?;', (userid)).fetchone()
              id = str(id[0])
              sub = cursor.execute('SELECT * FROM sub INNER JOIN categories ON categories.id = sub.cate_id WHERE user_id = ?;',(id)).fetchall()
              arrSub = []
              i = 0
              while i < len(sub):
                  arrSub.append(sub[i][3])
                  i = i + 1
              i = 0
              while i < len(arrSub):
                  name = str(arrSub[i])

                  name = types.KeyboardButton("отписаться от " + arrSub[i])
                  markup.add(name)

                  i = i + 1
              back = types.KeyboardButton('Вернуться')
              markup.add(back)
              bot.reply_to(message, "Ваши подписки:", reply_markup=markup)




    # при нажатии на отписаться отписываемся и переделываем список
    # все тоже самое но по-другому
    if message.chat.type == 'private':
        subs = "отписаться"
        if message.text.startswith(subs):
            userid = [message.chat.id]
            connect = sqlite3.connect('base.db')
            cursor = connect.cursor()
            id = cursor.execute('SELECT id FROM users WHERE tg_id=?;', (userid)).fetchone()
            id=str(id[0])
            forWhat = message.text[14:]
            cate_id = cursor.execute('SELECT id FROM categories WHERE name=?;', (forWhat,)).fetchall()
            cate_id = cate_id[0][0]
            have = cursor.execute('SELECT * FROM sub WHERE user_id = ? and cate_id = ?;',(id, cate_id)).fetchone()

            if not have:
                # это было для первоначального варианта щас уже обновляется и это не надо, убрать бы тогда или пусть будет?
                bot.reply_to(message, "Вы на нее не подписаны")
            else:
                cursor.execute('DELETE FROM sub WHERE user_id = ? and cate_id = ?;',(id, cate_id))
                connect.commit()

                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                sub = cursor.execute(
                    'SELECT * FROM sub INNER JOIN categories ON categories.id = sub.cate_id WHERE user_id = ?;',
                    (id)).fetchall()
                arrSub = []
                i = 0
                while i < len(sub):
                    arrSub.append(sub[i][3])
                    i = i + 1
                i = 0
                while i < len(arrSub):
                    name = str(arrSub[i])

                    name = types.KeyboardButton("отписаться от " + arrSub[i])
                    markup.add(name)

                    i = i + 1
                back = types.KeyboardButton('Вернуться')
                markup.add(back)

                bot.reply_to(message, "Вы успешно отписались", reply_markup=markup)


    if message.chat.type == 'private':
          if message.text == 'Новости✉️':
              userid = [message.chat.id]
              connect = sqlite3.connect('base.db')
              cursor = connect.cursor()
              # опять айдишник юзера надо бы это вынести а то че все одно и то же
              id = cursor.execute('SELECT id FROM users WHERE tg_id=?;', (userid)).fetchone()
              id = str(id[0])
              sub = cursor.execute('SELECT * FROM sub INNER JOIN categories ON categories.id = sub.cate_id WHERE user_id = ?;',(id)).fetchall()

              i=0


              while i < len(sub):


                  top_headlines = newsapi.get_top_headlines(category=f'{sub[i][3]}', language='ru', country='ru', page=1,page_size=1)



                  bot.send_message(message.chat.id,f'Категория:{sub[i][3]}\nЗаголовок: {top_headlines["articles"][0]["title"]}\n {top_headlines["articles"][0]["url"]}')

                  i = i + 1









  # кнопка возврата к основому меню
  if message.chat.type == 'private':
    if message.text == 'Вернуться':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

        itemNews = types.KeyboardButton('Новости✉️')
        itemSub = types.KeyboardButton('Подписки📱')
        itemCate = types.KeyboardButton('Категории📁')
        markup.add(itemCate, itemNews, itemSub)
        bot.reply_to(message, "Чем помочь?", reply_markup=markup)




bot.infinity_polling(none_stop = True)




