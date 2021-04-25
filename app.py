from threading import Thread
from time import sleep, time

import json
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

vk_session = vk_api.VkApi(token='264ac6c9a8c2baa4012e45d752b11aeed2a3dcb75001979f69cbe72f99c9e455329d7a4a95cf0791b9019')
longpoll = VkLongPoll(vk_session)


class User():
    def __init__(self, minion_level, id, mode, money, pol, energy, level, count5, count10, count15, coal, pers_name,
                 last_minion_work, minion_evo):
        self.id = id
        self.mode = mode
        self.money = money
        self.pol = pol
        self.energy = energy
        self.level = level
        self.count5 = count5
        self.count10 = count10
        self.count15 = count15
        self.coal = coal
        self.minion_level = minion_level
        self.pers_name = pers_name
        self.last_minion_work = last_minion_work
        self.minion_evo = minion_evo


def check_registration(id):
    members = vk_session.method('groups.getMembers', {'group_id': 204211434})['items']
    return id in members


def save_bd(users):
    lines = []
    for user in users:
        lines.append(
            f'"minion_level" : {user.minion_level}, "minion_evo" : {user.minion_evo}, "last_minion_work" : {user.last_minion_work}, "id" : {user.id}, "mode" : "{user.mode}", "money" : {user.money},  "pol" : "{user.pol}",  "energy" : {user.energy},  "level" : {user.level},"count5" : {user.count5},  "count10" : {user.count10},  "count15" : {user.count15}, "coal" : {user.coal}, "pers_name" : "{user.pers_name}"')
    lines = '\n'.join(lines)
    with open('data.txt', 'w', encoding='utf-8') as file:
        file.write(lines)
        file.close()


def read_bd():
    users = []
    with open('data.txt', 'r', encoding='utf-8') as file:
        lines = [x.replace('\n', '') for x in file.readlines()]
        file.close()
    for line in lines:
        line = eval('{' + line + '}')
        if line != '{}':
            users.append(User(minion_level=line['minion_level'], minion_evo=line['minion_evo'],
                              last_minion_work=line['last_minion_work'], id=line['id'], mode=line['mode'],
                              money=line['money'], pol=line['pol'], energy=line['energy'], level=line['level'],
                              count5=line['count5'], count10=line['count10'], count15=line['count15'],
                              coal=line['coal'], pers_name=line['pers_name']))
    return users


def get_keyboard(buts):  # функция создания клавиатур
    nb = []
    color = ''
    for i in range(len(buts)):
        nb.append([])
        for k in range(len(buts[i])):
            nb[i].append(None)
    for i in range(len(buts)):
        for k in range(len(buts[i])):
            text = buts[i][k][0]
            color = {'зеленый': 'positive', 'красный': 'negative', 'синий': 'primary', 'белый': 'secondary'}[
                buts[i][k][1]]
            nb[i][k] = {"action": {"type": "text", "payload": "{\"button\": \"" + "1" + "\"}", "label": f"{text}"},
                        "color": f"{color}"}
    first_keyboard = {'one_time': False, 'buttons': nb}
    first_keyboard = json.dumps(first_keyboard, ensure_ascii=False).encode('utf-8')
    first_keyboard = str(first_keyboard.decode('utf-8'))
    return first_keyboard


def sender(id, text, key):
    vk_session.method('messages.send',
                      {'user_id': id, 'message': text, 'random_id': 0, 'keyboard': key, 'dont_parse_links': 1})


reg_key = get_keyboard([
    [('Мужской', 'белый'), ('Женский', 'белый')]
])

lv1_menu_key = get_keyboard([
    [('Работа', 'белый'), ('Персонаж', 'белый')]
])

lv2_menu_key = get_keyboard([
    [('Работа', 'белый'), ('Персонаж', 'белый'), ('Миньён', 'белый')]
])

pers_key = get_keyboard([
    [('Статистика', 'белый'), ('Назад', 'красный')]
])

time_key_lv1 = get_keyboard([
    [('5сек', 'белый'), ('10сек', 'белый'), ('15сек', 'белый')],
    [('Назад', 'красный')]
])

time_key_lv2 = get_keyboard([
    [('15сек', 'белый'), ('30сек', 'белый'), ('45сек', 'белый')],
    [('Назад', 'красный')]
])

to2lvl_key = get_keyboard([
    [('Перейти на 2й уровень', 'зеленый')]
])

to3lvl_key = get_keyboard([
    [('Перейти на 3й уровень', 'зеленый')]
])

minion_menu = get_keyboard([
    [('Улучшить', 'белый'), ('Статистика', 'белый')],
    [('Назад', 'красный')]
])

buy_minion_key = get_keyboard([
    [('Купить миньёна', 'зеленый'), ('Назад', 'красный')]
])

ask_key = get_keyboard([
    [('Улучшить', 'зеленый'), ('Отмена', 'красный')]
])

evo_minion_key = get_keyboard([
    [('Эволюция', 'зеленый'), ('Назад', 'красный')]
])

clear_key = get_keyboard([])

menus = {1: lv1_menu_key, 2: lv2_menu_key}
minion_level_cash = {0: {0: 70, 1: 90, 2: 120}, 1: {1: 90, 2: 120}}
minion_cash_from_evo_level = {0: {0: 0, 1: 0, 2: 0, 3: 0}, 1: {1: 0, 2: 1, 3: 2}}
minion_energy_from_evo_level = {0: {0: 0, 1: 3, 2: 6, 3: 9}, 1: {1: 6, 2: 9, 3: 12}}
users = read_bd()

predel = 1


def minions_render():
    global users
    while True:
        for user in users:
            if user.level > 1:
                if user.coal > 0:
                    if time() - user.last_minion_work > (60 * 60):
                        user.money += minion_cash_from_evo_level[user.minion_evo][user.minion_level]
                        user.energy += minion_energy_from_evo_level[user.minion_evo][user.minion_level]
                        user.last_minion_work = time()
                        user.coal -= 1
                        save_bd(users)


Thread(target=minions_render).start()


def timer(id, level, time):
    global users
    for user in users:
        if user.id == id:
            if time == 5:
                if user.level == 1:
                    sleep(5)
                    user.money += 1
                    user.energy -= 1
                    sender(id, 'Работа выполнена, вам начислена 1 монета', time_key_lv1)

                elif user.level == 2:
                    sleep(15)
                    user.money += 1
                    user.energy -= 1
                    sender(id, 'Работа выполнена, вам начислена 1 монета', time_key_lv2)

                user.count5 += 1

            elif time == 10:
                if user.level == 1:
                    sleep(10)
                    user.money += 2
                    user.energy -= 2
                    sender(id, 'Работа выполнена, вам начислена 2 монеты', time_key_lv1)

                elif user.level == 2:
                    sleep(30)
                    user.money += 2
                    user.energy -= 2
                    sender(id, 'Работа выполнена, вам начислена 2 монеты', time_key_lv2)

                user.count10 += 1

            elif time == 15:
                if user.level == 1:
                    sleep(15)
                    user.money += 3
                    user.energy -= 3
                    sender(id, 'Работа выполнена, вам начислена 3 монеты', time_key_lv1)

                elif user.level == 2:
                    sleep(45)
                    user.money += 3
                    user.energy -= 3
                    sender(id, 'Работа выполнена, вам начислена 3 монеты', time_key_lv2)

                user.count15 += 1

            print(user.count5, user.count10, user.count15)

            for user in users:
                if user.id == id:
                    if (user.count5 == predel) & (user.count10 == predel) & (user.count15 == predel):
                        if user.level == 1:
                            sender(id, 'Вы выполнили все задания на 1м уровне, перейдите на 2й уровень!', to2lvl_key)
                            user.mode = 'level_up'

                        elif user.level == 2:
                            sender(id, 'Вы выполнили все задания на 2м уровне, перейдите на 3й уровень!', to3lvl_key)
                    # user.mode = 'level_up'


print('Bot started!')
for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me:

            id = event.user_id
            msg = event.text.lower()

            if msg == 'начать':

                if check_registration(id):
                    flag = 0
                    for user in users:
                        if user.id == id:
                            flag = 1
                            break
                    if not flag:  # если новый пользователь, то переходим в меню регистрации
                        users.append(
                            User(id=id, coal=24, last_minion_work=0, minion_evo=0, pers_name=None, minion_level=0,
                                 mode='registration1', money=100000, pol=None, energy=100, level=1, count5=0, count10=0,
                                 count15=0))
                        sender(id, 'Выберите пол вашего персонажа:', reg_key)
                    elif flag:  # если пользователь старый, то выходим в главное меню
                        for user in users:
                            if user.id == id:
                                if not (user.mode in ['registration1', 'registration2']):
                                    sender(id, 'Выберите действие:', menus[user.level])
                                    user.mode = 'start'
                else:
                    sender(id,
                           'Вы не подписаны на группу!\nДля того, чтобы пользоваться ботом, необходимо подписаться на '
                           'сообщество!',
                           clear_key)

            else:
                for user in users:
                    if user.id == id:

                        if user.mode == 'registration1':
                            flag = 0
                            if msg == 'мужской':
                                user.pol = 'Мужской'
                                flag = 1
                            elif msg == 'женский':
                                user.pol = 'Женский'
                                flag = 1
                            if flag:
                                sender(id, 'Введите имя персонажа:', clear_key)
                                user.mode = 'registration2'


                        elif user.mode == 'registration2':
                            user.pers_name = event.text
                            sender(id, 'Выберите действие:', lv1_menu_key)
                            user.mode = 'start'

                        elif user.level == 1:
                            if user.mode == 'start':

                                if msg == 'работа':
                                    sender(id, 'Выберите, сколько вы хотите работать:', time_key_lv1)
                                    user.mode = 'work'

                                elif msg == 'персонаж':
                                    sender(id, f'Пол: {user.pol}\nИмя: {user.pers_name}\nМонеты: {user.money}',
                                           lv1_menu_key)

                            elif user.mode == 'work':
                                if msg == '5сек':
                                    if user.count5 < predel:
                                        sender(id, 'Работа началась и продлится 5 секунд...', clear_key)
                                        Thread(target=timer(id, user.level, 5)).start()
                                    else:
                                        sender(id, 'Вы выполнили всю 5-ти секундную работу, приступайте к другой!',
                                               time_key_lv1)

                                elif msg == '10сек':
                                    if user.count10 < predel:
                                        sender(id, 'Работа началась и продлится 10 секунд...', clear_key)
                                        Thread(target=timer(id, user.level, 10)).start()
                                    else:
                                        sender(id, 'Вы выполнили всю 10-ти секундную работу, приступайте к другой!',
                                               time_key_lv1)

                                elif msg == '15сек':
                                    if user.count15 < predel:
                                        sender(id, 'Работа началась и продлится 15 секунд...', clear_key)
                                        Thread(target=timer(id, user.level, 15)).start()
                                    else:
                                        sender(id, 'Вы выполнили всю 15-ти секундную работу, приступайте к другой!',
                                               time_key_lv1)

                                elif msg == 'назад':
                                    sender(id, 'Выберите действие:', lv1_menu_key)
                                    user.mode = 'start'

                            elif user.mode == 'level_up':
                                if msg == 'перейти на 2й уровень':
                                    user.count5 = 0
                                    user.count10 = 0
                                    user.count15 = 0
                                    user.coal = 24
                                    sender(id, 'Поздравляем, вы перешли на 2й уровень!\nВыберите действие:',
                                           lv2_menu_key)
                                    user.level = 2
                                    user.mode = 'start'

                        elif user.level == 2:
                            if user.mode == 'start':
                                if msg == 'работа':
                                    sender(id, 'Выберите, сколько вы хотите работать:', time_key_lv2)
                                    user.mode = 'work'

                                elif msg == 'персонаж':
                                    sender(id,
                                           f'Пол персонажа: {user.pol}\nИмя: {user.pers_name}\nМонеты: {user.money}',
                                           lv2_menu_key)

                                elif msg == 'миньён':
                                    if user.minion_level == 0:
                                        sender(id, 'Для начала работы с миньёном, купите его за 70 монет:',
                                               buy_minion_key)
                                    else:
                                        sender(id, 'Выберите действие:', minion_menu)
                                    user.mode = 'minion'

                            elif user.mode == 'work':
                                if msg == '15сек':
                                    if user.count5 < predel:
                                        sender(id, 'Работа началась и продлится 15 секунд...', clear_key)
                                        Thread(target=timer(id, user.level, 5)).start()
                                    else:
                                        sender(id, 'Вы выполнили всю 15-ти секундную работу, приступайте к другой!',
                                               time_key_lv2)

                                if msg == '30сек':
                                    if user.count10 < predel:
                                        sender(id, 'Работа началась и продлится 30 секунд...', clear_key)
                                        Thread(target=timer(id, user.level, 10)).start()
                                    else:
                                        sender(id, 'Вы выполнили всю 30-ти секундную работу, приступайте к другой!',
                                               time_key_lv2)

                                if msg == '45сек':
                                    if user.count15 < predel:
                                        sender(id, 'Работа началась и продлится 45 секунд...', clear_key)
                                        Thread(target=timer(id, user.level, 15)).start()
                                    else:
                                        sender(id, 'Вы выполнили всю 45-ти секундную работу, приступайте к другой!',
                                               time_key_lv2)

                                if msg == 'назад':
                                    sender(id, 'Выберите действие:', lv2_menu_key)
                                    user.mode = 'start'

                            elif user.mode == 'minion':
                                if user.minion_level == 0:
                                    if msg == 'купить миньёна':
                                        if user.money >= minion_level_cash[user.minion_evo][user.minion_level]:
                                            user.money -= minion_level_cash[user.minion_evo][user.minion_level]
                                            user.minion_level = 1
                                            sender(id,
                                                   'Поздравляем, вы купили миньёна, теперь он будет приносить вам доход!\nВыберите действие:',
                                                   minion_menu)
                                        else:
                                            sender(id, 'У вас не достаточно монет!', buy_minion_key)
                                    elif msg == 'назад':
                                        sender(id, 'Выберите действие:', lv2_menu_key)
                                        user.mode = 'start'

                                else:
                                    if msg == 'улучшить':
                                        if user.minion_evo == 0:
                                            if user.minion_level < 3:
                                                sender(id,
                                                       f'Улучшение стоит: {minion_level_cash[user.minion_evo][user.minion_level]}\nВаши монеты: {user.money}',
                                                       ask_key)
                                                user.mode = 'ask_menu'
                                            elif user.minion_level == 3:
                                                if user.minion_evo < 1:
                                                    sender(id,
                                                           'Ваш миньён достиг максимального уровня, эволюционируйте его!',
                                                           evo_minion_key)
                                                    user.mode = 'evo_1_minion_mode'
                                                else:
                                                    sender(id, 'Ваш миньён уже эволюционирован!', minion_menu)

                                        elif user.minion_evo == 1:
                                            if user.minion_level < 3:
                                                sender(id,
                                                       f'Улучшение стоит: {minion_level_cash[user.minion_evo][user.minion_level]}\nВаши монеты: {user.money}',
                                                       ask_key)
                                                user.mode = 'ask_menu'
                                            elif user.minion_level == 3:
                                                sender(id, 'Ваш миньён достиг максимального уровня!', minion_menu)

                                    elif msg == 'статистика':
                                        if user.minion_evo == 0:
                                            sender(id,
                                                   f'Уровень миньёна: {user.minion_level}\nПрибыль: {minion_energy_from_evo_level[user.minion_evo][user.minion_level]} энергии в час',
                                                   minion_menu)
                                        elif user.minion_evo == 1:
                                            sender(id,
                                                   f'Уровень миньёна: {user.minion_level}\nПрибыль:\n{minion_energy_from_evo_level[user.minion_evo][user.minion_level]} энергии в час\n{minion_cash_from_evo_level[user.minion_evo][user.minion_level]} монет в час',
                                                   minion_menu)

                                    elif msg == 'назад':
                                        sender(id, 'Выберите действие:', lv2_menu_key)
                                        user.mode = 'start'

                            elif user.mode == 'ask_menu':
                                if msg == 'улучшить':
                                    if user.money >= minion_level_cash[user.minion_evo][user.minion_level]:
                                        user.money -= minion_level_cash[user.minion_evo][user.minion_level]
                                        user.minion_level += 1
                                        sender(id, f'Вы успешно улучшили своего миньёна на {user.minion_level} уровень',
                                               minion_menu)
                                        user.mode = 'minion'
                                    else:
                                        sender(id, 'У вас не достаточно монет для улучшения!', ask_key)

                                elif msg == 'отмена':
                                    sender(id, 'Выберите действие:', minion_menu)
                                    user.mode = 'minion'

                            elif user.mode == 'evo_1_minion_mode':
                                if msg == 'эволюция':
                                    if user.minion_evo < 1:
                                        user.minion_level = 1
                                        user.minion_evo += 1
                                        sender(id, 'Вы успешно эволюционировали своего миньёна!\nВыберите действие:',
                                               minion_menu)
                                        user.mode = 'minion'
                                    else:
                                        sender(id, 'Ваш миньён уже эволюционирован!', minion_menu)

                                elif msg == 'назад':
                                    sender(id, 'Выберите действие:', minion_menu)

                            elif user.mode == 'level_up':
                                pass

            save_bd(users)
