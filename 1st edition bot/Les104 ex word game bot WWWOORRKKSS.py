# Импортируем необходимые классы.
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
from telegram.ext import CommandHandler, ConversationHandler
import codecs
from random import randint

all_cities = []
with codecs.open('city_list.txt','r', "utf-8") as fileCL:
    textCityList = fileCL.readlines()
    for textCL in textCityList:
        textCL = textCL.strip()
        all_cities.append(textCL)

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
            update.message.reply_text('Кстати, я буду очень рад, если ты поможешь мне стать умнее! Научи меня новым городам командой /add_new_cities !')
            game = False
        else:
            update.message.reply_text(output)
           # user_data['attempt_number'] += 1
    print(user_data)
    #update.message.reply_text(city)
    return 1
 

 
# Добавили словарь user_data в параметры.
def second_response(bot, update, user_data):
    weather = update.message.text
    # Используем user_data в ответе.
    update.message.reply_text(
        "Спасибо за участие в опросе! Привет, {0}!".format(
            user_data['locality']))  
    return ConversationHandler.END


 
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
            2: [MessageHandler(Filters.text, second_response, 
                           pass_user_data=True)]       
        },
     
        # Точка прерывания диалога. В данном случае — команда /stop.
        fallbacks=[CommandHandler('stop', stop, pass_user_data=True)]
    )    
 
    
    dp.add_handler(conv_handler)
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("first_response", first_response))
    dp.add_handler(CommandHandler("second_response", second_response))
    dp.add_handler(CommandHandler("stop", stop))
   
    # Запускаем цикл приема и обработки сообщений.
    updater.start_polling()
 
    # Ждём завершения приложения. 
    # (например, получения сигнала SIG_TERM при нажатии клавиш Ctrl+C)
    updater.idle()
    
   
 
# Запускаем функцию main() в случае запуска скрипта.
if __name__ == '__main__':
    main()