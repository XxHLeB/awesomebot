# Импортируем необходимые классы.
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
from telegram.ext import CommandHandler, ConversationHandler
import codecs
from random import randint
import requests
import json

all_cities = []
with codecs.open('list_of_cities_new.txt','r', "utf-8") as fileCL: #city_list.txt
    textCityList = fileCL.readlines()
    for textCL in textCityList:
        textCL = textCL.strip()
        all_cities.append(textCL)
    fileCL.close()

def start(bot, update):
    update.message.reply_text(
        "Привет, я робот, который умеет играть в города\n"
        "Вы можете прервать игру, послав команду /stop.\n"
        "Назови город")
    
   
    print(update.message.text)
    #if  update.message.text == '/skip':
       # return 3
    return 1
    # Оно указывает, что дальше на сообщения 
    # от этого пользователя должен отвечать обработчик states[1].
    # До этого момента обработчиков текстовых сообщений 
    # для этого пользователя не существовало,
    # поэтому текстовые сообщения игнорировались.

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
    for each_city in all_cities:
        if last_letter == each_city.lower()[0] and each_city not in used_cities:
            city_choices.append(each_city)
    if len(city_choices) != 0:
        number = randint(1, len(city_choices)-1)
        random_city = city_choices[number]
        city_choices.clear()
        used_cities.append(random_city)
        return random_city 
    else:
        return 0
    
# Добавили словарь user_data в параметры.
def first_response(bot, update, user_data):
    if user_data == {}:
        user_data['used_cities'] = []
    
    #user_data['attempt_number'] = 1  
    # Число-ключ в словаре states — 
    # втором параметре ConversationHandler'а.
   # print(user_data)
   # Сохраняем ответ в словаре.
    city = update.message.text
    
    city_check, used_check, last_letter_check = check(city, user_data['used_cities'])
    
    if used_check > 0:
        update.message.reply_text('Города нельзя повторять, введи новый город')
    if city_check == 0:
        update.message.reply_text('Я такого города не знаю. Попробуй ещё раз')
        update.message.reply_text('Если ты думаешь, что такой город точно есть, ты можешь помочь мне стать умнее и научить меня новому! (Если хочешь, отправь "да" )')
        return 3
    if last_letter_check == 0:
        #last_answer = used_cities[-1]
        last_letter = user_data['used_cities'][-1][-1]
        if last_letter in ['ы', 'ь', 'ъ']:
            last_letter = user_data['used_cities'][-1][-2]
        update.message.reply_text('Город должен начинаться с последней буквы предыдущего,')
        #print(str(user_data['used_cities'][-1]))
        update.message.reply_text('я назвал город "{}",'.format( user_data['used_cities'][-1]))
        update.message.reply_text(' тебе на букву "{}"'.format( last_letter))
    if used_check == 0 and city_check == 1 and last_letter_check == 1:
        #used_cities.append(city_input)
        city = city.lower()
        user_data['used_cities'].append(city)
        #print(user_data)
        output = find_city(city, user_data['used_cities'])
        if output == 0:
            update.message.reply_text('Ой-ой, похоже я не знаю ни одного города на эту букву. Поздравляю, ты победитель!')
            update.message.reply_text('Можешь поиграть со мной ещё или проверить другие игры')
            update.message.reply_text('Кстати, я буду очень рад, если ты поможешь мне стать умнее! Научи меня новым городам (Если хочешь, отправь "да" )')
            return 3
        else:
            update.message.reply_text(output)
            update.message.reply_text('Хочешь, я покажу тебе картинку этого города? (Если хочешь, отправь "да" )')
            return 2
           # user_data['attempt_number'] += 1
    print(user_data)
    #update.message.reply_text(city)
    return 1
 

 
# Добавили словарь user_data в параметры.
def show_picture(bot, update, user_data):
    response = update.message.text
    if response.lower() == 'да':
        city = user_data['used_cities'] [-1]
        print(city)
    
        update.message.reply_text("Картинка города {}!".format(city)) 
        try:
            geocoder_uri = geocoder_request_template = "http://geocode-maps.yandex.ru/1.x/"
            response = requests.get(geocoder_uri, params = {
                "format": "json",
                "geocode": city
            })
    
    
            toponym = response.json()["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
            print(toponym)
       
            ll, spn = get_ll_spn(toponym)  
            # Можно воспользоваться готовой фукнцией,
            # которую предлагалось сделать на уроках, посвященных HTTP-геокодеру.
    
            static_api_request = "http://static-maps.yandex.ru/1.x/?ll={ll}&spn={spn}&l=map".format(**locals())
            if not static_api_request:
                print('nope')
                update.message.reply_text("Ошибка выполнения запроса:")
                update.message.reply_text(geocoder_request)
                update.message.reply_text("Http статус:", response.status_code, "(", response.reason, ")")
            try :
                print(static_api_request)
               # update.message.reply_text(static_api_request)
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
        return 1
    elif response.lower() == 'нет':
        last_letter = user_data['used_cities'][-1][-1]
        if last_letter in ['ы', 'ь', 'ъ']:
            last_letter = user_data['used_cities'][-1][-2]
        update.message.reply_text("Ну ладно, давай играть дальше")
        update.message.reply_text('я назвал город "{}",'.format( user_data['used_cities'][-1]))
        update.message.reply_text(' тебе на букву "{}"'.format( last_letter))
        return 1
    else:
        update.message.reply_text('Извини, я не понял ответа. Так да или нет?')
        return 2


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
        #print(toponym)
   
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
    
    update.message.reply_text('Можешь добавить ещё города (Если хочешь, отправь "да" )') 
    
    return 3
    

    
    
 
def stop(bot, update, user_data):
    update.message.reply_text(
        "Жаль. А было бы интерсно поиграть. Всего доброго!")
    user_data.clear()
    return ConversationHandler.END  # Константа, означающая конец диалога.


def main():
    updater = Updater("878258787:AAEqfpeU72PTVZ6IgYitqMqzuUFYP6OHI9k")
 
    dp = updater.dispatcher
 
    
    conv_handler = ConversationHandler(
        # Точка входа в диалог.
        # В данном случае — команда /start. Она задаёт первый вопрос.
        entry_points=[CommandHandler('start', start)],
     
        # Состояние внутри диалога. Вариант с двумя обработчиками, 
        # фильтрующими текстовые сообщения.
        states={
            # Функция читает ответ на первый вопрос и задаёт второй.
            1: [MessageHandler(Filters.text, first_response, 
                           pass_user_data=True)],
            # Функция читает ответ на второй вопрос и завершает диалог.
            2: [MessageHandler(Filters.text, show_picture, 
                           pass_user_data=True)],
            3: [MessageHandler(Filters.text, add_new_cities_question, 
                           pass_user_data=True)], 
            4: [MessageHandler(Filters.text, add_new_cities, 
                           pass_user_data=True)], 
            
        },
     
        # Точка прерывания диалога. В данном случае — команда /stop.
        fallbacks=[CommandHandler('stop', stop, pass_user_data=True)]
    )    
    #dp.add_handler(CommandHandler("start", start))
    #dp.add_handler(CommandHandler("add_new_cities", add_new_cities)) 
    
    dp.add_handler(conv_handler)
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("add_new_cities_question", add_new_cities_question)) 
    dp.add_handler(CommandHandler("add_new_cities", add_new_cities)) 
    dp.add_handler(CommandHandler("first_response", first_response))
    dp.add_handler(CommandHandler("show_picture", show_picture))
    dp.add_handler(CommandHandler("stop", stop))
   
    # Запускаем цикл приема и обработки сообщений.
    updater.start_polling()
 
    # Ждём завершения приложения. 
    # (например, получения сигнала SIG_TERM при нажатии клавиш Ctrl+C)
    updater.idle()
    
   
 
# Запускаем функцию main() в случае запуска скрипта.
if __name__ == '__main__':
    main()