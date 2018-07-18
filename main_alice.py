# Импортируем модули для работы с JSON и логами.
import json
import logging
import random
# Импортируем подмодули Flask для запуска веб-сервиса.
from flask import Flask, request
app = Flask(__name__)
from scripts import *
with open('config/config.json', encoding='utf-8') as f:
    config_json = json.load(f)
#with open('config/yandex_data.json', encoding='utf-8') as f:
#    yandex_data = json.load(f)
logging.basicConfig(level=logging.DEBUG)

# Хранилище данных о сессиях.
sessionStorage = {}

# Задаем параметры приложения Flask.
@app.route("/", methods=['POST'])

def main():
# Функция получает тело запроса и возвращает ответ.
    logging.info('Request: %r', request.json)

    response = {
        "version": request.json['version'],
        "session": request.json['session'],
        "response": {
            "end_session": False
        }
    }

    handle_dialog(request.json, response)

    logging.info('Response: %r', response)

    return json.dumps(
        response,
        ensure_ascii=False,
        indent=2
    )

# Функция для непосредственной обработки диалога.
def handle_dialog(req, res):
    message = ""
    cmd = ""
    user_id = req['session']['user_id']

    if req['session']['new']:
        # Это новый пользователь.
        # Инициализируем сессию и поприветствуем его.

        sessionStorage[user_id] = {
            'suggests': [
                "random",
                "facerec",
                "help",
                "words",
                "fight"
            ],
            'fightMode': False,
            'player_hp': 30,
            'player_mp': 10,
            'enemy_hp':45,
            'enemy_mp':20,
            'name':random.choice(config_json["name1"])+random.choice(config_json["name2"])

        }

        res['response']['text'] = config_json["greet"]
        res['response']['buttons'] = get_suggests(user_id)
        return

    # Обрабатываем ответ пользователя.
    command = req['request']['original_utterance'].split()
    if command[0] == "fight":
        res['response']['text'] = str()
        sessionStorage[user_id]['name'] = str(random.choice(config_json["name1"])+ " "+random.choice(config_json["name2"]))
        sessionStorage[user_id]['player_hp'] = 30
        sessionStorage[user_id]['player_mp'] = 10
        sessionStorage[user_id]['enemy_hp'] = 45
        sessionStorage[user_id]['enemy_mp'] = 20
        sessionStorage[user_id]['fightMode'] = True
        sessionStorage[user_id]['suggests'] = [
            "stats",
            "attack",
            "heal",
            "charge",
            "stop"
        ]
        res['response']['text'] = str(random.choice(config_json['nameaction']) +" "+ sessionStorage[user_id]['name']+"! " + sessionStorage[user_id]['name'] + "'s HP: "+
                        str(sessionStorage[user_id]['enemy_hp']) + ' Your HP: ' + str(sessionStorage[user_id][
                        'player_hp']) + ' Your MP: ' + str(sessionStorage[user_id]['player_mp']))
        res['response']['buttons'] = get_suggests(user_id)
        return
    if sessionStorage[user_id]['fightMode']:
        if command[0] in ["stats", "attack", "heal", "charge", "stop"]:
            if command[0] == "stats":
                res['response']['text'] = str(
                    sessionStorage[user_id]['name'] + "'s HP: "+
                        str(sessionStorage[user_id]['enemy_hp']) + ' Your HP: ' + str(sessionStorage[user_id][
                        'player_hp']) + ' Your MP: ' + str(sessionStorage[user_id]['player_mp']))
                res['response']['buttons'] = get_suggests(user_id)
                return
            else:
                if command[0] == "attack":
                    attackamt = random.randint(2,6)
                    sessionStorage[user_id]['enemy_hp'] -= attackamt
                    res['response']['text'] = str("You attack "+sessionStorage[user_id]['name']+" for "+str(attackamt)+ " damage! "
                                                  + sessionStorage[user_id]['name'] + "'s HP: " + str(sessionStorage[user_id]['enemy_hp'])+" ")
                elif command[0] == "heal":
                    pointamt = random.randint(1,3)
                    healamt = random.randint(6,8)
                    sessionStorage[user_id]['player_hp'] += healamt
                    sessionStorage[user_id]['player_mp'] -= pointamt
                    res['response']['text'] = str("You use "+str(pointamt)+ " magic to heal for "+str(healamt)+" damage! Your HP: "+
                                                  str(sessionStorage[user_id]['player_hp'])+ " Your MP: "+str(sessionStorage[user_id]['player_mp'])+" ")
                elif command[0] == "charge":
                    chargeamt = random.randint(4,7)
                    sessionStorage[user_id]['player_mp'] += chargeamt
                    res['response']['text'] = str("You regain "+str(chargeamt)+" points! ")

                elif command[0] == "stop":
                    sessionStorage[user_id]['fightMode'] = False
                    res['response']['text'] = str("You stop the battle.")
                    sessionStorage[user_id]['suggests'] = [
                        "random",
                        "facerec",
                        "help",
                        "words",
                        "fight"
                    ]
                    res['response']['buttons'] = get_suggests(user_id)
                    return
                action = arcadeAction(user_id)
                res['response']['text'] += action[5]
                sessionStorage[user_id]['player_hp'] += action[0]
                sessionStorage[user_id]['player_mp'] += action[1]
                sessionStorage[user_id]['enemy_hp'] += action[2]
                sessionStorage[user_id]['enemy_mp'] += action[3]
                res['response']['buttons'] = get_suggests(user_id)
                return



    elif command[0] in list(config_json["commands"].keys()):
        cmd = config_json["commands"][command[0]]["func"]
        cmdvalue = getattr(globals()[cmd], "main")(*command[1:])
        res['response']['text'] = cmdvalue
        res['response']['buttons'] = get_suggests(user_id)
        return
    #if req['request']['original_utterance'].lower() in [
    #    'ладно',
    #    'куплю',
    #    'покупаю',
    #    'хорошо',
    #]:
    #    # Пользователь согласился, прощаемся.
    #    res['response']['text'] = 'Слона можно найти на Яндекс.Маркете!'
    #    return

    # Если нет, то убеждаем его купить слона!
    #res['response']['text'] = 'Все говорят "%s", а ты купи слона!' % (
    #    req['request']['original_utterance']
    #)
    res['response']['buttons'] = get_suggests(user_id)

# Функция возвращает две подсказки для ответа.
def get_suggests(user_id):
    session = sessionStorage[user_id]

    # Выбираем две первые подсказки из массива.
    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests']
    ]

    # Убираем первую подсказку, чтобы подсказки менялись каждый раз.
    #session['suggests'] = session['suggests'][1:]
    #sessionStorage[user_id] = session

    # Если осталась только одна подсказка, предлагаем подсказку
    # со ссылкой на Яндекс.Маркет.
    #if len(suggests) < 2:
    #    suggests.append({
    #        "title": "Ладно",
    #        "url": "https://market.yandex.ru/search?text=слон",
    #        "hide": True
    #    })

    return suggests
def arcadeAction(user_id):
    enemy_hp = sessionStorage[user_id]["enemy_hp"]
    enemy_mp = sessionStorage[user_id]["enemy_mp"]
    player_hp = sessionStorage[user_id]["player_hp"]
    player_mp = sessionStorage[user_id]["player_mp"]
    message = ""
    pHP = 0
    pMP = 0
    eHP = 0
    eMP = 0
    eName = sessionStorage[user_id]['name']
    mode = 0
    if (enemy_hp <= 0 or enemy_mp <= 0):
        mode = "win"
        message = "You kill "+eName+ "! Congratulations!"
        sessionStorage[user_id]["fightMode"] = False
        sessionStorage[user_id]['suggests'] = [
            "random",
            "facerec",
            "help",
            "words",
            "fight"
        ]
    elif (enemy_mp <= 5 and random.randint(0,100) <= 70):
        mode = "steal"
        stealamt = random.randint(2,3)
        pMP -= stealamt
        message = eName + " steals "+str(stealamt)+" of your mana!"
    elif (enemy_hp <= 10 and enemy_mp > 4):
        mode = "heal"
        message = eName + " heals for 4 health!"
        eHP += 4
        eMP -= 4
    else:
        attackamt = random.randint(3,6)
        mode = "attack"
        message = eName + " attacks for "+str(attackamt)+" damage!"
        pHP -= attackamt
    if (pHP != 0):
        message += " Your HP: " + str(player_hp + pHP)
    if (pMP != 0):
        message += " Your MP: " + str(player_mp + pMP)
    if (eHP != 0 and mode != "win"):
        message += " "+eName+ "'s HP: " + str(enemy_hp + eHP)
    if (player_hp + pHP <= 0 or player_mp + pMP <= 0):
        mode = "gameover"
        message += " You die! Game over!"
        sessionStorage[user_id]["fightMode"] = False
        sessionStorage[user_id]['suggests'] = [
            "random",
            "facerec",
            "help",
            "words",
            "fight"
        ]
    return(pHP,pMP,eHP,eMP,mode,message)