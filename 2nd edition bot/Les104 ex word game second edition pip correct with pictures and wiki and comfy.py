# Импортируем необходимые классы.
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
from telegram.ext import CommandHandler, ConversationHandler
import codecs
from random import randint
import requests
import json
from telegram import ReplyKeyboardMarkup
from telegram import ReplyKeyboardRemove 
import wikipedia


all_cities = []
with codecs.open('list_of_cities_new.txt', 'r', "utf-8") as fileCL: 
    textCityList = fileCL.readlines()
    for textCL in textCityList:
        textCL = textCL.strip()
        all_cities.append(textCL)
    fileCL.close()


def start(bot, update, user_data):
    global all_cities
    user_data['number_of_tries'] = 0
    update.message.reply_text(
        "Привет, я робот, который умеет играть в города,\n" 
        "показывать картинки городов и переводить их названия!")
    update.message.reply_text(
        'На данный момент я знаю {} городов!'.format(len(all_cities)))
    update.message.reply_text(
        'Ты можешь ПОМОЧЬ МНЕ УЗНАТЬ НОВЫЕ ГОРОДА!\n'
        'Я играю в города на ДВУХ ЯЗЫКАХ!\n'
        'Я могу ПОКЗАТЬ ОБЪЕКТЫ НА КАРТЕ!\n'
        'ОТПРАВЬ /help ЧТОБЫ ПОЛУЧИТЬ ПОМОЩЬ\n'
        'ФУНКЦИИ ГЕОКОДЕРА И ПЕРЕВОДЧИКА СТАНУТ\n'
        'ДОСТУПНЫ ПОСЛЕ ТОГО, КАК ТЫ НАЗОВЁШЬ ГОРОД\n'
        "Игру можно прервать, послав команду /stop.\n")
    update.message.reply_text("Назови город")
    return 1
    

def help(bot, update, user_data):
    if user_data['number_of_tries'] == 0:
        update.message.reply_text('ПОМОЩЬ')
        update.message.reply_text('Напечатай название любого города\n'
                                  'ФУНКЦИИ ГЕОКОДЕРА И ПЕРЕВОДЧИКА СТАНУТ\n'
                                  'ДОСТУПНЫ ПОСЛЕ ТОГО, КАК ТЫ НАЗОВЁШЬ ГОРОД\n'
                                  'Тогда сможешь снова набрать /help ,\n'
                                  'чтобы узнать, как ими пользоваться')
    else:
        update.message.reply_text('ПОМОЩЬ')
        update.message.reply_text('Я -- робот, который умеет играть в города, показывать картинки городов и переводить их названия.\n'
        'помощь с добавлением городов -- /help_with_adding\n'
        'помощь с переводом -- /help_with_translater\n'
        'помощь с геокодером -- /help_with_geocoder')


def help_with_adding(bot, update):
    update.message.reply_text('ПОМОЩЬ С ДОБАВЛЕНИЕМ ГОРОДОВ')
    update.message.reply_text(
        'Ты можешь ПОМОЧЬ МНЕ УЗНАТЬ НОВЫЕ ГОРОДА:\n'
        'если введёшь город, которого я не знаю,\n'
        'я попрошу тебя научить меня ему;\n'
        'если он пройдёт проверку подлинности, мы\n'
        'сможем использовать его в игре.\n')


def help_with_translater(bot, update):
    update.message.reply_text('ПОМОЩЬ С ПЕРЕВОДЧИКОМ')
    update.message.reply_text(
        'Я играю в города на ДВУХ ЯЗЫКАХ:\n'
        'можешь писать города как на английском,\n'
        'так и на русском;\n'
        'если нужна помощь в переводе города воспользуйся\n'
        'функцией /translater :\n'
        'cначала отправь /show для открытия\n'
        'клавиатуры с направлением переводов,\n'
        'после выбери направление и отправь его, далее\n'
        'напиши: "/translater  (пробел)  *слово или слова для перевода* ".\n'
        'Чтобы закрыть клавиатуру отправь /close')


def help_with_geocoder(bot, update):
    update.message.reply_text('ПОМОЩЬ С ГЕОКОДЕРОМ')
    update.message.reply_text(
        'если хочешь посмотреть географические\n' 
        'объекты, воспользуйся\n'
        'функцией /geocoder :\n'
        'напиши: "/geocoder  (пробел)  *географический объект* ".\n')


def check(city, used_cities):
    global all_cities
    city_check = 0
    used_check = 0
    last_letter_check = 0
    for c in all_cities:
        if c.lower() == city.lower():
            #такой город есть в нашем списке
            city_check = 1
    for c in used_cities:
        if c.lower() == city.lower():
            #такой город есть в нашем списке        
            used_check += 1
    if len(used_cities) != 0:
        last_letter = used_cities[-1][-1].lower()
        if last_letter in ['ы', 'ь', 'ъ']:
            last_letter = used_cities[-1][-2].lower()
        if last_letter == city[0].lower():
            last_letter_check = 1
    if len(used_cities) == 0:
        last_letter_check = 1
    return city_check, used_check, last_letter_check


def find_city(city, used_cities):
    global all_cities
    city_choices = []
    last_letter = city[-1]
    if last_letter in ['ы', 'ь', 'ъ']:
        last_letter = city[-2]
    used = []
    for city in used_cities:
        used.append(city.lower())
    for each_city in all_cities:
        if last_letter == each_city.lower()[0]:
            if each_city.lower() not in used:
                city_choices.append(each_city)
    if len(city_choices) == 1:
        used_cities.append(city_choices[0])
        return city_choices[0]    
    if len(city_choices) > 1:
        number = randint(1, len(city_choices)-1)
        random_city = city_choices[number]
        city_choices.clear()
        used_cities.append(random_city)
        return random_city 
    else:
        return 0
  

def find_hints(city, used_cities):
    global all_cities
    city_choices = []
    last_letter = city[-1]
    if last_letter in ['ы', 'ь', 'ъ']:
        last_letter = city[-2]
    used = []
    for city in used_cities:
        used.append(city.lower())
    for each_city in all_cities:
        if last_letter == each_city.lower()[0]:
            if each_city.lower() not in used:
                city_choices.append(each_city)
    
    return city_choices
    
# Добавили словарь user_data в параметры.
def first_response(bot, update, user_data):
    if user_data == {'number_of_tries': 0}: 
        user_data['used_cities'] = []
        user_data['added_cities'] = []
        user_data['geocoded'] = []
        user_data['translated'] = []
        user_data['skipped'] = 0
    user_data['number_of_tries'] += 1
    city = update.message.text
    city_check, used_check, last_letter_check = check(
        city, user_data['used_cities'])
    if used_check > 0:
        update.message.reply_text('Города нельзя повторять, введи новый город')
    if city_check == 0:
        update.message.reply_text('Я такого города не знаю. Попробуй ещё раз')
        update.message.reply_text('Если ты думаешь, что такой город точно есть, ты можешь помочь мне стать умнее и научить меня новому! (Если хочешь, отправь "да", если не хочешь -- "нет" )')
        return 3
    if last_letter_check == 0:
        last_letter = user_data['used_cities'][-1][-1]
        if last_letter in ['ы', 'ь', 'ъ']:
            last_letter = user_data['used_cities'][-1][-2]
        update.message.reply_text('Город должен начинаться с последней буквы предыдущего,')
        update.message.reply_text('я назвал город "{}",'.format( user_data['used_cities'][-1]))
        update.message.reply_text(' тебе на букву "{}"'.format( last_letter))
    if used_check == 0 and city_check == 1 and last_letter_check == 1:
        city = city.lower()
        user_data['used_cities'].append(city)
        output = find_city(city, user_data['used_cities'])
        if output == 0:
            update.message.reply_text('Ой-ой, похоже я не знаю ни одного города на эту букву. Поздравляю, ты победитель!')
            if len(user_data['used_cities']) > 0:
                update.message.reply_text(
                    "Вот какие города мы назвали в ходе игры:")
                output_list = []
                for city in user_data['used_cities']:
                    city = city[0].upper() + city[1:].lower()
                    output_list.append(city)
                update.message.reply_text( ' --> '.join(output_list))
                update.message.reply_text(
                    "Количество городов: {} ".format(str(len(output_list))))
                if len(user_data['used_cities']) % 2 == 1:
                    score = len(user_data['used_cities']) // 2 + 1 - user_data['skipped']
                else:
                    score = len(user_data['used_cities']) / 2 - user_data['skipped']
                update.message.reply_text( 'Твой счёт -- {}'.format(score))
            if len(user_data['added_cities']) > 0:
                output_list = []
                for city in user_data['added_cities']:
                    city = city[0].upper() + city[1:].lower()
                    output_list.append(city)        
                update.message.reply_text(
                       "Спасибо, что помог мне узнать новые города!") 
                update.message.reply_text(
                       "Количество выученных городов: {}".format(len(user_data['added_cities'])))
                update.message.reply_text('Города:')
                update.message.reply_text(', '.join(output_list))
            if len(user_data['geocoded']) > 0:
                output_list = []
                for city in user_data['geocoded']:
                    city = city[0].upper() + city[1:].lower()
                    output_list.append(city)        
                update.message.reply_text(
                       "Молодец, что воспользовался функцией геокодера") 
                update.message.reply_text('Показанные места:')
                update.message.reply_text(', '.join(output_list))
            if len(user_data['translated']) > 0:
                output_list = []
                for city in user_data['translated']:
                    city = city[0].upper() + city[1:].lower()
                    output_list.append(city)        
                update.message.reply_text(
                        "Молодец, что воспользовался функцией переводчика") 
                update.message.reply_text('Переведённые слова:')
                update.message.reply_text(', '.join(output_list))
            user_data.clear()
            update.message.reply_text('Поиграть со мной ещё -- /start')
            return ConversationHandler.END
        else:
            update.message.reply_text(output)
            update.message.reply_text('/show_picture - посмотреть карту двух последних названных городов\n'
                                      '/wiki - справка об этих городах из Википедии\n'
                                      '/full_wiki - полная статья из Википедии (робот-спамер)\n'
                                      '/skip - пропустить ход\n'
                                      '/tell_me_hint - посмотреть подсказки')
    return 1
 

def skip(bot, update, user_data):
    update.message.reply_text('ладно, я схожу за тебя,\n'
                              'но в следущий раз постарайся ответить сам')
    output = find_city(user_data['used_cities'][-1], user_data['used_cities'])
    if output == 0:
        update.message.reply_text('Ой-ой, похоже я не знаю ни одного города на эту букву. Поздравляю, ты победитель!')
        if len(user_data['used_cities']) > 0:
            update.message.reply_text(
                "Вот какие города мы назвали в ходе игры:")
            output_list = []
            for city in user_data['used_cities']:
                city = city[0].upper() + city[1:].lower()
                output_list.append(city)
            update.message.reply_text( ' --> '.join(output_list))
            update.message.reply_text(
                "Количество городов: {} ".format(str(len(output_list))))
            if len(user_data['used_cities']) % 2 == 1:
                score = len(user_data['used_cities']) // 2 + 1 - user_data['skipped']
            else:
                score = len(user_data['used_cities']) / 2 - user_data['skipped']
            update.message.reply_text( 'Твой счёт -- {}'.format            (score))
        if len(user_data['added_cities']) > 0:
            output_list = []
            for city in user_data['added_cities']:
                city = city[0].upper() + city[1:].lower()
                output_list.append(city)        
            update.message.reply_text(
                   "Спасибо, что помог мне узнать новые города!") 
            update.message.reply_text(
                   "Количество выученных городов: {}".format(len(user_data['added_cities'])))
            update.message.reply_text('Города:')
            update.message.reply_text(', '.join(output_list))
        if len(user_data['geocoded']) > 0:
            output_list = []
            for city in user_data['geocoded']:
                city = city[0].upper() + city[1:].lower()
                output_list.append(city)        
            update.message.reply_text(
                   "Молодец, что воспользовался функцией геокодера") 
            update.message.reply_text('Показанные места:')
            update.message.reply_text(', '.join(output_list))
        if len(user_data['translated']) > 0:
            output_list = []
            for city in user_data['translated']:
                city = city[0].upper() + city[1:].lower()
                output_list.append(city)        
            update.message.reply_text(
                    "Молодец, что воспользовался функцией переводчика") 
            update.message.reply_text('Переведённые слова:')
            update.message.reply_text(', '.join(output_list))
        user_data.clear()
        update.message.reply_text('Поиграть со мной ещё -- /start')
        return ConversationHandler.END
    else:
        user_data['skipped'] += 1
        update.message.reply_text(output)
        update.message.reply_text('/show_picture - посмотреть     карту двух последних названных городов\n'
                                      '/wiki - справка об этих городах из Википедии\n'
                                      '/full_wiki - полная статья из Википедии (робот-спамер)\n'
                                      '/skip - пропустить ход\n'
                                      '/tell_me_hint - посмотреть подсказки')
    return 1
 

def tell_me_hint(bot, update, user_data):
    output = find_hints(user_data['used_cities'][-1], user_data['used_cities'])
    if len(output) < 1:
        update.message.reply_text('Я не знаю городов на эту букву')
    elif len(output) < 5:
        update.message.reply_text('Я знаю, например, такие города на эту букву: {}'.format(', '.join(output)))
    else:
        update.message.reply_text('Я знаю, например, такие города на эту букву: {}'.format(', '.join(output[:5])))


def show_picture(bot, update, user_data):
    if user_data['number_of_tries'] == 0:
        update.message.reply_text('Ещё не нaзваны города\n'
        'Назови город')                     
    elif len(user_data['used_cities']) > 1:
        cities = user_data['used_cities'][-2:]
        for city in cities:        
            update.message.reply_text("Картинка города {}!".format(city)) 
            try:
                geocoder_uri = geocoder_request_template = "http://geocode-maps.yandex.ru/1.x/"
                response = requests.get(geocoder_uri, params = {
                    "format": "json",
                    "geocode": city
                })
                toponym = response.json()["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
                adress = toponym['metaDataProperty']['GeocoderMetaData']['text'] 
                ll, spn = get_ll_spn(toponym)  
                # Можно воспользоваться готовой фукнцией,
                # которую предлагалось сделать на уроках, посвященных HTTP-геокодеру.
                static_api_request = "http://static-maps.yandex.ru/1.x/?ll={ll}&spn={spn}&l=map".format(**locals())
                if not static_api_request:
                    update.message.reply_text("Ошибка выполнения запроса:")
                    update.message.reply_text(geocoder_request)
                    update.message.reply_text("Http статус:", response.status_code, "(", response.reason, ")")
                try :
                    update.message.reply_text('Расположение города:')
                    update.message.reply_text(adress)
                    bot.sendPhoto(
                        update.message.chat.id,  # Идентификатор чата. Куда посылать картинку.
                        # Ссылка на static API по сути является ссылкой на картинку.
                        static_api_request
                    )                             
                    # Телеграму можно передать прямо ее, не скачивая предварительно карту.
                except  Exception as e:
                    update.message.reply_text(str(e))
            except:
                update.message.reply_text("Запрос не удалось выполнить. Проверьте правильность написания. Cкорее всего такого географического объекта не существует")
        last_letter = user_data['used_cities'][-1][-1]
        if last_letter in ['ы', 'ь', 'ъ']:
            last_letter = user_data['used_cities'][-1][-2]
        update.message.reply_text("Давай играть дальше!")
        update.message.reply_text('последним я назвал город "{}",'.format( user_data['used_cities'][-1]))
        update.message.reply_text(' тебе на букву "{}"'.format( last_letter))
         
       
def get_ll_spn(toponym):
    # Координаты центра топонима:
    toponym_coodrinates = toponym["Point"]["pos"]
    # Долгота и Широта :
    toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")
    # Собираем координаты в параметр ll
    ll = ",".join([toponym_longitude, toponym_lattitude])
    # Рамка вокруг объекта:
    envelope = toponym["boundedBy"]["Envelope"]
    # левая, нижняя, правая и верхняя границы из координат углов:
    l,b = envelope["lowerCorner"].split(" ")
    r,t = envelope["upperCorner"].split(" ")
    # Вычисляем полуразмеры по вертикали и горизонтали
    dx = abs(float(l) - float(r)) / 2.0
    dy = abs(float(t) - float(b)) / 2.0
    # Собираем размеры в параметр span
    span = "{dx},{dy}".format(**locals())
    return (ll, span)


def add_new_cities_question(bot, update, user_data):
    response = update.message.text
    if response.lower() == 'да':
        update.message.reply_text('Благодарю, что помогаешь мне. Напиши город, который хочешь добавить')
        return 4
    elif response.lower() == 'нет':
        if len(user_data['used_cities']) < 1:
            update.message.reply_text("Ну ладно, давай играть дальше")
            update.message.reply_text("Назови любой город")
            return 1
        else:
            last_letter = user_data['used_cities'][-1][-1]
            if last_letter in ['ы', 'ь', 'ъ']:
                last_letter = user_data['used_cities'][-1][-2]
            update.message.reply_text("Ну ладно, давай играть дальше")
            update.message.reply_text('я назвал город "{}",'.format( user_data['used_cities'][-1]))
            update.message.reply_text(' тебе на букву "{}"'.format( last_letter))
            return 1
    else:
        update.message.reply_text('Извини, я не понял ответа. Так да или нет?')
        return 3
    
    
def add_new_cities(bot, update, user_data):
    global all_cities
    #if user_data['number_of_tries'] == 0:
       # update.message.reply_text('Ещё не нaзваны города\n'
        #'Назови город')
    city = update.message.text.lower()
    update.message.reply_text('Ты хочешь добавить город {}'.format(city))
    update.message.reply_text('Сейчас спрошу у Яндекс Карт, что они думают по поводу города {}'.format(city))
    try:
        geocoder_uri = geocoder_request_template = "http://geocode-maps.yandex.ru/1.x/"
        response = requests.get(geocoder_uri, params = {
            "format": "json",
            "geocode": city
        })
        toponym = response.json()["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        if toponym['metaDataProperty']['GeocoderMetaData']['kind'] == 'locality':
            update.message.reply_text('Я спросил у Яндекс Карт, они  думают, что {} -- хороший город.'.format(city))
            city = city[0].upper() + city[1:]
            city_check = 0
            for c in all_cities:
                if c.lower() == city.lower():
                        city_check = 1
            if city_check == 0:
                update.message.reply_text('Это то что мне нужно. я его запомню')
                update.message.reply_text('Cпасибо, что мне помогаешь')
                all_cities.append(city)
                user_data['added_cities'].append(city)
                try:
                    with codecs.open('list_of_cities_new.txt','a', "utf-8") as f: 
                        print(f.write(str('\n' + city)))
                        f.close()                    
                except Exception:
                    print('Ошибка записи файла')
            if city_check == 1:
                update.message.reply_text('Я уже знаю это город, но всё равно спасибо за помощь!')
        else:
            update.message.reply_text('Я спросил у Яндекс Карт, они не думают, что {} это город'.format(city))
    except:
        update.message.reply_text("Я спросил у Яндекс Карт, скорее всего такого географического объекта не существует")
    update.message.reply_text('Можешь добавить ещё города (Если хочешь, отправь "да", если не хочешь -- "нет")') 
    return 3


def show_keyboard(bot, update):
    reply_keyboard = [['/en_ru', '/ru_en']]
                      
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)    
    update.message.reply_text("Это клавиатура с направлениями перевода, если хотите её закрыть, используйте команду /close", 
                              reply_markup=markup)
   
    
def close_keyboard(bot, update):
    update.message.reply_text("Клавиатура с направлениями перевода закрыта", reply_markup=ReplyKeyboardRemove())

    
def en_ru(bot, update, user_data):
    direction = 'en-ru'
    user_data['direction'] = 'en-ru'
   
    
def ru_en(bot, update, user_data):
    direction = 'ru-en'
    user_data['direction'] = 'ru-en'
    

def translater(bot, update, user_data, args):
    word = ' '.join(args)
    direction = user_data['direction']
    accompanying_text = \
        "Переведено сервисом «Яндекс.Переводчик» http://translate.yandex.ru/."
    translator_uri = \
        "https://translate.yandex.net/api/v1.5/tr.json/translate"
    response = requests.get(
        translator_uri,
        params={
            "key":
            # Ключ, который надо получить по ссылке в тексте.
            "trnsl.1.1.20190413T161945Z.f65076a6e526c869.1c8d847f81ad77499a68d51a9b8f9a35009d3429",
            # Направление перевода: с русского на английский.
            "lang": direction,
                    # То, что нужно перевести.
            "text": str(word)
        })
    user_data['translated'].append(word)
    update.message.reply_text(
        "\n\n".join([response.json()["text"][0], accompanying_text]))
    update.message.reply_text('Можешь воспользоваться переводчиком ещё или уже поиграть в города')
    return 5


def geocoder(bot, update, user_data, args):
    try:
        word = ' '.join(args)
        geocoder_uri = geocoder_request_template = "http://geocode-maps.yandex.ru/1.x/"
        response = requests.get(geocoder_uri, params = {
            "format": "json",
            "geocode": word
        })
        toponym = response.json()["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        ll, spn = get_ll_spn(toponym)  
        # Можно воспользоваться готовой фукнцией,
        # которую предлагалось сделать на уроках, посвященных HTTP-геокодеру.
        static_api_request = "http://static-maps.yandex.ru/1.x/?ll={ll}&spn={spn}&l=map".format(**locals())
        if not static_api_request:
            update.message.reply_text("Ошибка выполнения запроса:")
            update.message.reply_text(geocoder_request)
            update.message.reply_text("Http статус:", response.status_code, "(", response.reason, ")")
        try :
            user_data['geocoded'].append(word)
            bot.sendPhoto(
                update.message.chat.id,  # Идентификатор чата. Куда посылать картинку.
                # Ссылка на static API по сути является ссылкой на картинку.
                static_api_request
            )                             
            # Телеграму можно передать прямо ее, не скачивая предварительно карту.
        except  Exception as e:
            update.message.reply_text(str(e))
    except:
        update.message.reply_text("Запрос не удалось выполнить. Проверьте правильность написания")

    
def stop(bot, update, user_data):
    update.message.reply_text(
        "Жаль. А было бы интерсно поиграть. Всего доброго!")
    if len(user_data['used_cities']) > 0:
        update.message.reply_text(
            "Вот какие города мы назвали в ходе игры:")
        output_list = []
        for city in user_data['used_cities']:
            city = city[0].upper() + city[1:].lower()
            output_list.append(city)
        update.message.reply_text( ' --> '.join(output_list))
        update.message.reply_text(
            "Количество городов: {} ".format(str(len(output_list))))
        if len(output_list) % 2 == 1:
            score = len(output_list) // 2 + 1
            update.message.reply_text( 'Твой счёт -- {}'.format(int(score)))
        else:
            score = len(output_list) / 2
            update.message.reply_text( 'Твой счёт -- {}'.format(int(score)))
    if len(user_data['added_cities']) > 0:
        output_list = []
        for city in user_data['added_cities']:
            city = city[0].upper() + city[1:].lower()
            output_list.append(city)        
        update.message.reply_text(
               "Спасибо, что помог мне узнать новые города!") 
        update.message.reply_text(
               "Количество выученных городов: {}".format(len(user_data['added_cities'])))
        update.message.reply_text('Города:')
        update.message.reply_text(', '.join(output_list))
    if len(user_data['geocoded']) > 0:
        output_list = []
        for city in user_data['geocoded']:
            city = city[0].upper() + city[1:].lower()
            output_list.append(city)        
        update.message.reply_text(
               "Молодец, что воспользовался функцией геокодера") 
        update.message.reply_text('Показанные места:')
        update.message.reply_text(', '.join(output_list))
    if len(user_data['translated']) > 0:
        output_list = []
        for city in user_data['translated']:
            city = city[0].upper() + city[1:].lower()
            output_list.append(city)        
        update.message.reply_text(
                "Молодец, что воспользовался функцией переводчика") 
        update.message.reply_text('Переведённые слова:')
        update.message.reply_text(', '.join(output_list))
    user_data.clear()
    return ConversationHandler.END  # Константа, означающая конец диалога.


def check_language(word):
    word = word.replace(' ', '')
    latin = 'absdefghijklmnopqrstuvwxyzßüøéàaî'
    cyrillic = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
    latin_counter = 0
    cyrillic_counter = 0
    for letter in word:
        if letter.lower() in latin:
            latin_counter += 1
        if letter.lower() in cyrillic:
            cyrillic_counter += 1
    if latin_counter == len(word):
        return 'english'
    if cyrillic_counter == len(word):
        return 'russian'
                
    
def wiki(bot, update, user_data):
    if user_data['number_of_tries'] == 0:
        update.message.reply_text('Ещё не нaзваны города\n'
        'Назови город')                     
    elif len(user_data['used_cities']) > 1:
        cities = user_data['used_cities'][-2:]
        for city in cities:
            if check_language(user_data['used_cities'][-2]) == 'english':
                request = str(wikipedia.search(city)[0] + ' (city)')
            elif check_language(user_data['used_cities'][-2]) == 'russian':
                wikipedia.set_lang("ru")
                request = wikipedia.search(city + ' город')[0]
                if request == None:
                    update.message.reply_text('Похоже, про этот город нет информации в Википедии')
            page = wikipedia.page(request)
            update.message.reply_text(page.title) 
            if wikipedia.summary(request, sentences=2)[:19] == 'Это статья о городе' or wikipedia.summary(request, sentences=2)[:19] == 'Эта статья о городе':
                update.message.reply_text(wikipedia.summary(request, sentences=5))
            if len(wikipedia.summary(request, sentences=2)) < 50:
                update.message.reply_text(wikipedia.summary(request, sentences=5))
            elif len(wikipedia.summary(request, sentences=5)) < 50:##
                update.message.reply_text(wikipedia.summary(request, sentences=8))  ##
            else:
                update.message.reply_text(wikipedia.summary(request, sentences=2))   
            update.message.reply_text(page.url) 
            try :
                page = wikipedia.page(request) 
                link = page.images[0]             
                bot.sendPhoto(
                    update.message.chat.id,  # Идентификатор чата. Куда посылать картинку.
                    # Ссылка на static API по сути является ссылкой на картинку.
                    link
                )                             
                # Телеграму можно передать прямо ее, не скачивая предварительно карту.
            except  Exception as e:
                update.message.reply_text('Извини, не получилось отправить картинку\n'
                'Ошибка: {}'.format(str(e)))
        last_letter = user_data['used_cities'][-1][-1]
        if last_letter in ['ы', 'ь', 'ъ']:
            last_letter = user_data['used_cities'][-1][-2]
        update.message.reply_text("Давай играть дальше!")
        update.message.reply_text('последним я назвал город "{}",'.format( user_data['used_cities'][-1]))
        update.message.reply_text('тебе на букву "{}"'.format( last_letter))
      

def full_wiki(bot, update, user_data):
    if user_data['number_of_tries'] == 0:
        update.message.reply_text('Ещё не нaзваны города\n'
        'Назови город')                     
    elif len(user_data['used_cities']) > 1:
        cities = user_data['used_cities'][-2:]
        for city in cities:
            if check_language(user_data['used_cities'][-2]) == 'english':
                request = str(wikipedia.search(city)[0] + ' (city)')
            elif check_language(user_data['used_cities'][-2]) == 'russian':
                wikipedia.set_lang("ru")
                #request = str(wikipedia.search(city)[0] + ' (город)')
                request = wikipedia.search(city + ' город')[0]
                if request == None:
                    update.message.reply_text('Похоже, про этот город нет информации в Википедии')
            page = wikipedia.page(request)
            update.message.reply_text(page.title)
            full_page = page.content.split('.')
            for sentence in full_page:
                update.message.reply_text(str(sentence + '.'))
            update.message.reply_text(page.url) 
            try :
                page = wikipedia.page(request) 
                link = page.images[0]             
                bot.sendPhoto(
                    update.message.chat.id,  # Идентификатор чата. Куда посылать картинку.
                    # Ссылка на static API по сути является ссылкой на картинку.
                    link
                )                             
                # Телеграму можно передать прямо ее, не скачивая предварительно карту.
            except  Exception as e:
                update.message.reply_text('Извини, не получилось отправить картинку\n'
                'Ошибка: {}'.format(str(e)))
                
        last_letter = user_data['used_cities'][-1][-1]
        if last_letter in ['ы', 'ь', 'ъ']:
            last_letter = user_data['used_cities'][-1][-2]
        update.message.reply_text("Давай играть дальше!")
        update.message.reply_text('последним я назвал город "{}",'.format( user_data['used_cities'][-1]))
        update.message.reply_text('тебе на букву "{}"'.format( last_letter))
   

def main():
    updater = Updater("878258787:AAEqfpeU72PTVZ6IgYitqMqzuUFYP6OHI9k")
    dp = updater.dispatcher
    conv_handler = ConversationHandler(
        # Точка входа в диалог.
        # В данном случае — команда /start. Она задаёт первый вопрос.
        entry_points=[CommandHandler('start', start, pass_user_data=True)],
        # Состояние внутри диалога. Вариант с двумя обработчиками, 
        # фильтрующими текстовые сообщения.
        states={
            # Функция читает ответ на первый вопрос и задаёт второй.
            1: [MessageHandler(Filters.text, first_response, 
                           pass_user_data=True)],
            3: [MessageHandler(Filters.text, add_new_cities_question, 
                           pass_user_data=True)], 
            4: [MessageHandler(Filters.text, add_new_cities, 
                           pass_user_data=True)],         
        },
     
        # Точка прерывания диалога. В данном случае — команда /stop.
        fallbacks=[CommandHandler('stop', stop, pass_user_data=True)]
    )    
    dp.add_handler(conv_handler)
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("translater", translater, pass_user_data=True, pass_args=True))
    dp.add_handler(CommandHandler("geocoder", geocoder, pass_user_data=True, pass_args=True))
    dp.add_handler(CommandHandler("wiki", wiki, pass_user_data=True))
    dp.add_handler(CommandHandler("full_wiki", full_wiki, pass_user_data=True))
    dp.add_handler(CommandHandler("show_picture", show_picture, pass_user_data=True))
    dp.add_handler(CommandHandler("skip", skip, pass_user_data=True))
    dp.add_handler(CommandHandler("tell_me_hint", tell_me_hint, pass_user_data=True))
    dp.add_handler(CommandHandler("show", show_keyboard))
    dp.add_handler(CommandHandler("close", close_keyboard))
    dp.add_handler(CommandHandler("ru_en", ru_en, pass_user_data=True))
    dp.add_handler(CommandHandler("en_ru", en_ru, pass_user_data=True))
    dp.add_handler(CommandHandler("help", help, pass_user_data=True))
    dp.add_handler(CommandHandler("help_with_adding", help_with_adding))
    dp.add_handler(CommandHandler("help_with_translater", help_with_translater))
    dp.add_handler(CommandHandler("help_with_geocoder", help_with_geocoder))
    dp.add_handler(CommandHandler("stop", stop))
    # Запускаем цикл приема и обработки сообщений.
    updater.start_polling()
    # Ждём завершения приложения. 
    # (например, получения сигнала SIG_TERM при нажатии клавиш Ctrl+C)
    updater.idle()
    
 
# Запускаем функцию main() в случае запуска скрипта.
if __name__ == '__main__':
    main()