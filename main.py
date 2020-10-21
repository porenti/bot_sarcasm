import sqlite3 as sql
import time
import random
import json
import vk_api
import pandas as pd
import requests


#Токены
group_token = ''
own_token = ''

#Подключение
vk_own = vk_api.VkApi(token=own_token)
vk_group = vk_api.VkApi(token=group_token)

#Авторизация
vk_own._auth_token()
vk_group._auth_token()

#Декоративная функция
def decor():
    print('\n'*2)


#Функция кнопок вк
def get_button(label, color, payload=""):
    return {
        "action": {
            "type": "text",
            "payload": json.dumps(payload),
            "label": label
        },
        "color": color
    }
#Клавиатура выбора пола
keyboardSEX = {
    "one_time": True,
    "buttons": [
    [get_button(label='Мужчины', color="primary"),
    get_button(label='Женщины', color="negative")],
    [get_button(label='Не имеет значения', color="secondary")]
     ]}

keyboardSEX = json.dumps(keyboardSEX, ensure_ascii=False).encode('utf-8')
keyboardSEX = str(keyboardSEX.decode('utf-8'))

#Клавиатура необходимости образования
keyboardEducation = {
    "one_time": True,
    "buttons": [
    [get_button(label='Да', color="primary"),
    get_button(label='Нет', color="negative")
     ]]}

keyboardEducation = json.dumps(keyboardEducation, ensure_ascii=False).encode('utf-8')
keyboardEducation = str(keyboardEducation.decode('utf-8'))

#Клавиатура Старта
keyboardStart = {
    "one_time": True,
    "buttons": [
    [get_button(label='Начать', color="primary")]]}

keyboardStart = json.dumps(keyboardStart, ensure_ascii=False).encode('utf-8')
keyboardStart = str(keyboardStart.decode('utf-8'))

#Главная клавиаутура
keyboardMain = {
    "one_time": True,
    "buttons": [
    [get_button(label='Начать рекрутинг', color="primary")],
    [get_button(label='Сбросить параметры', color="negative")],
    [get_button(label='А как работает система?', color="secondary")]
     ]}

keyboardMain = json.dumps(keyboardMain, ensure_ascii=False).encode('utf-8')
keyboardMain = str(keyboardMain.decode('utf-8'))


table_main_name = 'people'

connection = sql.connect("main.db")
q = connection.cursor()


id_users_list = []

global_test = q.execute("SELECT * FROM PEOPLE").fetchall()
print('global_test: ',global_test)
connection.commit()
connection.close()

while True:
    try:
        connection.commit()
        connection.close()
    except:
        print()
    finally:
        connection = sql.connect("main.db")
        q = connection.cursor()
    try:
        id_q = list(set(q.execute('SELECT id from people').fetchall()))[0]   #айдишники зареганных
        #print(id_q)
        connection.commit()
        #id_users_list = list(id_q)
    except:
        print('Добавленных пользователей нет')
    try:
        messages = vk_group.method("messages.getConversations", {"offset": 0, "count": 1, "filter": "unanswered"})
        if messages["count"] >= 1:
            id = messages["items"][0]["last_message"]["from_id"]
            body = messages["items"][0]["last_message"]["text"]
            print('t',id)
            print(id not in id_users_list)
            if id not in id_users_list:
                Action = 1   #Место пользователя в системе
                q.execute('INSERT INTO people (id,step) VALUES ({},{})'.format(id,Action))
                connection.commit()
                id_users_list.append(id)
                print(id,id_users_list[0])
            else:   #Рабочая область
                print('posos')
                q.execute("SELECT * FROM people WHERE id = {}".format(int(id)))
                connection.commit()
                
                kash_abrakadabra = list(set(q.fetchall()))[0]
                print(kash_abrakadabra)
                
                usage_action = int(kash_abrakadabra[1]) #Получаем действие
                if usage_action == 1: #Начинаем
                    text = "Здравствуйте и добро пожаловать! Я - ваш помощник в подборе кандидатов на интересующие должности 'HR-Ассистент'. Для того, чтобы приступить к работе скажите мне: вам нужны мужчины или женщины? Или же вы предпочтёте не указывать пол?"
                    vk_group.method("messages.send", {"peer_id": id, "message": text, "random_id": random.randint(1, 2147483647), "keyboard": keyboardSEX})
                    q.execute("UPDATE people SET step = {} Where id = {}".format(2,id))
                    connection.commit()
                elif usage_action == 2: #Выбираем пол
                    if body.title()[0] == 'М':
                        kash_sex = 1
                    elif body.title()[0] == 'Ж':
                        kash_sex = 2
                    else:
                        kash_sex = 0
                    q.execute("UPDATE people SET step = {} Where id = {}".format(3,id))
                    q.execute("UPDATE people SET sex = {} Where id = {}".format(kash_sex,id))
                    connection.commit()
                    text = "Уточните, важно ли для вас образование кандидатов?"
                    vk_group.method("messages.send", {"peer_id": id, "message": text, "random_id": random.randint(1, 2147483647), "keyboard": keyboardEducation})
                    
                elif usage_action == 3:     #Выбираем наличие образования
                    print(body.title == 'Да')
                    print(body.title)
                    if body.title() == "Да":
                        kash_education = 1
                    else:
                        kash_education = 0
                    q.execute("UPDATE people SET step = {} Where id = {}".format(4,id))
                    connection.commit()
                    q.execute("UPDATE people SET education = {} Where id = {}".format(kash_education,id))
                    connection.commit()
                    text = "Какой возрастной диапазон вас интересует? Пожалуйста, укажите диапазон через дефис. Например: 18-25."
                    vk_group.method("messages.send", {"peer_id": id, "message": text, "random_id": random.randint(1, 2147483647)})

                elif usage_action == 4: #Считываем желаемый возраст

                    if int(body[0]+body[1]) > 9 and int(body[3]+body[4]) < 100:
                        kash_min_age = int(body[0]+body[1])
                        kash_max_age = int(body[3]+body[4])
                        q.execute("UPDATE people SET step = {} Where id = {}".format(5,id))
                        q.execute("UPDATE people SET AgeMin = {} Where id = {}".format(kash_min_age,id))
                        q.execute("UPDATE people SET AgeMax = {} Where id = {}".format(kash_max_age,id))
                        connection.commit()
                        text = "Уточните: из какого города вы хотите подбирать кандидатов?"
                        vk_group.method("messages.send", {"peer_id": id, "message": text, "random_id": random.randint(1, 2147483647)})

                    else:
                        text = "Какой возрастной диапазон вас интересует? Пожалуйста, укажите диапазон через дефис. Например: 18-25.\nРазрешены числа от 10 до 99"
                        vk_group.method("messages.send", {"peer_id": id, "message": text, "random_id": random.randint(1, 2147483647)})
                        
                elif usage_action == 5: #Считываем город

                    try:
                        #print(body[:14])
                        city_info = vk_own.method("database.getCities", {"q": body[:14], "country_id": 1, "need_all": 0})
                        kash_city = city_info['items'][0]['id']
                        #print(kash_city)
                        
                        q.execute("UPDATE people SET step = {} Where id = {}".format(10,id))        #В главное меню
                        connection.commit()
                        q.execute("UPDATE people SET town = {} Where id = {}".format(kash_city,id))
                        connection.commit()
                        text = "Добро пожаловать в главное меню."
                        vk_group.method("messages.send", {"peer_id": id, "message": text, "random_id": random.randint(1, 2147483647), "keyboard": keyboardMain})

                    except:
                        text = "Уточните: из какого города вы хотите подбирать кандидатов?\nГород не найден."
                        vk_group.method("messages.send", {"peer_id": id, "message": texzt, "random_id": random.randint(1, 2147483647)})

                elif usage_action == 10: # RABOTA

                    if body.title() == 'А Как Работает Система?':       #Помощь
                        vk_help_link = 'https://vk.com/hr_assistant?w=wall-199540262_2'
                        text = "Для того чтобы понять как работает наш Ассистент, прочтите закрепленный пост на странице сообщества.\n" + vk_help_link
                        vk_group.method("messages.send", {"peer_id": id, "message": text, "random_id": random.randint(1, 2147483647), "keyboard": keyboardMain})

                    elif body.title() == 'Сбросить Параметры':          #Рестарт
                        id_users_list.remove(id)
                        q.execute("Delete From people where id = {}".format(id))
                        text = 'Параметры успешно сброшены'
                        vk_group.method("messages.send", {"peer_id": id, "message": text, "random_id": random.randint(1, 2147483647), "keyboard": keyboardStart})
                        q.execute("UPDATE people SET step = {} Where id = {}".format(2,id))
                        connection.commit()
                        

                    elif body.title() == "Начать Рекрутинг":    #MAIN УЖАС
                        q.execute("SELECT * FROM people WHERE id = {}".format(id))
                        kash_abrakadabra = q.fetchall()
                        print("Начать рекрутинг: ",kash_abrakadabra[0])

                        kash_town_id = int(kash_abrakadabra[0][6])
                        #print('+++',kash_town_id)
                        kash_town_name = vk_own.method("database.getCitiesById", {"city_ids": kash_town_id})[0]['title']
                        #print(kash_town_name)
                        #Переменные
                        end_list = ['Имя,id,Пол,Наличие образования,Возраст,Номер телефона,Скоринговый балл']
                        object_name = "Работа"
                        number_phone_allow_symbols = ['+','0','1','2','3','4','5','6','7','8','9'] #Разрешено для телефона
                        json_list = ["id","id_vk","name","city","sex","education","education_area","age",'mobile_phone',"points"] #Название столбцов
                        #Статистика
                        finded_users = 0
                        banned_users = 0
                        closed_users = 0
                        finded_afk_users = 0
                        finded_users_not_in_our_town = 0
                        finded_users_not_need_sex = 0
                        finded_users_not_need_age = 0
                        finded_users_not_need_education = 0
                        kash_id = []
                        count_return = 0#Повторы
                        start = time.time()
                        #Поиск групп
                        q = object_name + " " + kash_town_name
                        print(q)
                        groups = vk_own.method("groups.search", {"city_id":kash_town_id, "q":q, "count": 5})["items"]
                        
                        decor()
                        
                        for i in groups:
                            print("id: {}".format(i['id'])+' name: {}'.format(i['name']))

                        for i in groups:
                            decor()
                            print('Парсим ', i['name'])
                            decor()
                            x = 1000 #1000 дефолтное значение
                            offset = 0
                            for k in range(0,10): #100 default
                                offset = int(k * x)
                                kash_groups_people = vk_own.method("groups.getMembers", {"group_id":i['id'], "offset": offset, "count":x, "fields":"sex, bdate, city, contacts, education, last_seen"})['items']
            
                                for j in kash_groups_people:    #Находим пользователя
                                    finded_users += 1 #Считаем его
                                    kash_members = []
                                    if j['id'] in kash_id:
                                        count_return += 1
                                    else:
                                        kash_id.append(j['id'])
                                    try: #Проверка на бан
                                        if j['is_closed'] == False:  #Страница открыта
                                            if (time.time()-604800)<j['last_seen']['time']: #АФК ЮЗЕРЫ
                                                if j['city']['title'] == kash_town_name: #Проверка на город
                                                    if j['sex'] != kash_abrakadabra[0][2]:
                                                        kash_edu = 0
                                                        try:
                                                            if j['faculty'] == 0:
                                                                kash_edu += 0
                                                            else:
                                                                kash_edu = 1
                                                        except:
                                                            kash_edu = 0

                                                        try:
                                                            if j['university'] == 0:
                                                                kash_edu += 0
                                                            else:
                                                                kash_edu += 1
                                                        except:
                                                            kash_edu += 0
                                                            
                                                        kash_score = kash_edu   #points
                                                        
                                                        if kash_edu >= kash_abrakadabra[0][3]: #Возраст
                                                            if len(str(j['bdate']).split('.')) == 3:
                                                                kash_age = 2020 - int(str(j['bdate']).split('.')[2])
                                                                if kash_age > kash_abrakadabra[0][4] and kash_age < kash_abrakadabra[0][5]:
                                                                    kash_score += 2

                                                                    kash_mobile_phone = str(j['mobile_phone'])
                                                                    mobile_phone = ''
                                                                    if len(kash_mobile_phone) > 8:
                                                                        if int(kash_mobile_phone[0]) == 9:
                                                                            mobile_phone += '+7'
                                                                        if int(kash_mobile_phone[0]) == 8 or int(kash_mobile_phone[0]) == 7:
                                                                            mobile_phone += '+7'
                                                                    for ii in range(1,len(kash_mobile_phone)):
                                                                        if kash_mobile_phone[ii] in number_phone_allow_symbols:
                                                                            mobile_phone += str(kash_mobile_phone[ii])
                                                                    try:
                                                                        if len(mobile_phone) < 11:
                                                                            mobile_phone = "-"
                                                                        else:
                                                                            kash_score += 3
                                                                    except:
                                                                            mobile_phone = "-"
                                                                    #print("Стойкость")############
                                                                    kash_abra_sex = ''
                                                                    if j['sex'] == 2:
                                                                        kash_abra_sex = 'Мужской'
                                                                    else:
                                                                        kash_abra_sex = 'Женский'
                                                                        
                                                                    kash_member = [j['first_name']+" "+j['last_name'],j['id'],kash_abra_sex,kash_edu,kash_age,mobile_phone,kash_score]
                                                                    #print(kash_member)
                                                                    end_list.append(kash_member)
                                            #
                                                            else:
                                                                finded_users_not_need_age += 1  #Не указано                               
                                                        else:
                                                            findid_users_not_need_education += 1
                                                    else:
                                                        finded_users_not_need_sex += 1
                                                else:
                                                    finded_users_not_in_our_town += 1
                                            else:
                                                finded_afk_users += 1
                                        else:
                                            closed_users += 1
                                    except:
                                        banned_users += 1

                        print(end_list[0])
                        print(len(end_list))
                        decor()
                        report = "С запуска поиска прошло {} секунд\n\nУдачных результатов {}\n\nВсего было найдено пользователей {}\nИз них заблокировано {}\nСкрыты страницы у {}\nНеактивных пользователей отсеяно {}\nИз других городов, не включено в списки {}\nПо половому признаку ушло {} кандидатов\nПо возрасту не подошло {}\nПо образованию не прошло {} человек\nПовторяющихся записей выявлено {}".format(int(time.time()-start),len(end_list),finded_users,banned_users,closed_users,finded_afk_users,finded_users_not_in_our_town,finded_users_not_need_sex,finded_users_not_need_age,finded_users_not_need_education,count_return)
                        print(report)

                        name_file = str(id) + "_" + str(time.time()) + '.csv'
                        _csv = open(name_file, "w", encoding="utf-8")
                        for line in end_list:
                            _str = ""
                            for piece in line:
                                _str += str(piece) + ","
                            _str = _str[:-1]
                            _csv.write(_str + "\n")
                        _csv.close()
                        #frame = pd.DataFrame(end_list) # собираем фрейм
                        #frame.to_csv(name_file,index=False) #экспортируем в файл



                        def send_doc(file,user_id):
                            doc = open(file, "r", encoding='utf-8')
                            a = vk_group.method("docs.getMessagesUploadServer", {"type": "doc", "peer_id": user_id})
                            print(a)
                            print("----------")
                            b = requests.post(a["upload_url"], files={"file": doc}).json()
                            print(b)
                            c = vk_group.method("docs.save", {"file": b["file"], "title": "Parse"})
                            print(c)
                            d = 'doc{}_{}'.format(c['doc']['owner_id'], c['doc']['id'])
                            vk_group.method('messages.send', {'user_id': user_id, 'attachment': d, "random_id":random.randint(1, 20000)})


                        send_doc(name_file,id)
                        vk_group.method("messages.send", {"peer_id": id, "message": report, "random_id": random.randint(1, 2147483647), "keyboard": keyboardMain})
                        












                            
                        connection.commit()
                        #break

                    else:       #HR - Даун
                        text = "Извините, но я не понял вашу команду, попробуйте еще раз или прочитайте пост об использовании Ассистента\n"
                        vk_group.method("messages.send", {"peer_id": id, "message": text, "random_id": random.randint(1, 2147483647), "keyboard": keyboardMain})   
                        
        time.sleep(1)




    except:
        print(er)




