import telebot
import random
import json

TOKEN = ""
bot = telebot.TeleBot(TOKEN)


def get_players_json():
    with open("players.json", "r") as file:
        data = json.load(file)

    return data


def set_players_json(data):
    with open("players.json", "w") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def get_key(game):
    return


def game_start_config(game_id):
    with open(f"games/{game_id}.json", "r", encoding="utf-8") as file:
        game = json.load(file)

    game["game_settings"]["game_status"] = 1

    players = game["teams"]["all_players"].copy()

    random.shuffle(players)

    game["teams"]["red_team"] = players[:len(players) // 2]
    game["teams"]["blue_team"] = players[len(players) // 2:]
    game["teams"]["red_team_cap"] = game["teams"]["red_team"][0]
    game["teams"]["blue_team_cap"] = game["teams"]["blue_team"][0]
    game["teams"]["queue"] = "bc"

    all_words = list(map(lambda x: x.lower(), get_random_words_for_game()))
    game["field"]["all_words"] = all_words.copy()

    random.shuffle(all_words)

    game["field"]["red_words"] = all_words[:8]
    game["field"]["blue_words"] = all_words[8:17]
    game["field"]["black_word"] = all_words[17]
    game["field"]["grey_words"] = all_words[18:]

    game["field"]["key"] = get_key(game)

    with open(f"games/{game_id}.json", "w", encoding="UTF-8") as file:
        json.dump(game, file, indent=4, ensure_ascii=False)

    return game


def create_random_game_id():
    a, b, c, d = random.randint(0, 10), random.randint(0, 10), random.randint(0, 10), random.randint(0, 10)
    return f"{a}{b}{c}{d}"


def create_random_game_password():
    a = random.choice("1234567890qwertyuiopasdfghjklzxcvbnm")
    if random.randint(0, 2) == 1:
        a = a.upper()
    b = random.choice("1234567890qwertyuiopasdfghjklzxcvbnm")
    if random.randint(0, 2) == 1:
        b = b.upper()
    c = random.choice("1234567890qwertyuiopasdfghjklzxcvbnm")
    if random.randint(0, 2) == 1:
        c = c.upper()
    d = random.choice("1234567890qwertyuiopasdfghjklzxcvbnm")
    if random.randint(0, 2) == 1:
        d = d.upper()
    return f"{a}{b}{c}{d}"


def get_games_id():
    res = []
    data = get_players_json()

    for player in data:
        game_id = data[player]["game_id"]
        if game_id not in ("", "..."):
            res.append(game_id)

    return res


def get_all_words():
    with open("dictionary.txt", "r", encoding="utf-8") as file:
        return list(map(lambda word: word.replace("­", ""), file.read().split(", ")))


def get_random_words_for_game():
    return random.sample(get_all_words(), 25)


def print_game_field(words):
    pre_ind = 0
    for ind in range(5, 26, 5):
        print("".join(words[pre_ind:ind]))
        pre_ind = ind


def game_message(message):
    players = get_players_json()
    player_id = str(message.chat.id)
    game_id = players[player_id]["game_id"]
    with open(f"games/{game_id}.json", "r", encoding="utf-8") as file:
        game = json.load(file)
    all_players_ids = game["teams"]["all_players"]
    if game["game_settings"]["game_status"] == 1:
        if player_id in game["teams"]["red_team"]:
            if player_id == game["teams"]["red_team_cap"]:
                player_role = "rc"
            else:
                player_role = "rt"
        else:
            if player_id == game["teams"]["blue_team_cap"]:
                player_role = "bc"
            else:
                player_role = "bt"

        queue_role = game["teams"]["queue"]

        if player_role != queue_role:
            bot.send_message(player_id, "Сейчас не ваш ход")
            return

        if player_role == "bc":
            for id in all_players_ids:
                try:
                    bot.send_message(id, f"[Капитан синих]\n{message.text}")
                except:
                    pass
                game["teams"]["queue"] = "bt"

        elif player_role == "rc":
            for id in all_players_ids:
                try:
                    bot.send_message(id, f"[Капитан красных]\n{message.text}")
                except:
                    pass
                game["teams"]["queue"] = "rt"

        elif player_role == "rt":
            word = message.text.strip().lower()
            all_words = game["field"]["all_words"]
            red_words = game["field"]["red_words"]
            blue_words = game["field"]["blue_words"]
            grey_words = game["field"]["grey_words"]
            if word != "пропустить":
                if word not in all_words:
                    bot.send_message(player_id, "Такого слова нет")
                    return

            for id in all_players_ids:
                try:
                    bot.send_message(id, f"[Команда красных]\n{word}")
                except:
                    pass

            if word == "пропустить":
                game["teams"]["queue"] = "bc"
                mes = "Красные пропустили ход"

            elif word in red_words:
                all_words.remove(word)
                red_words.remove(word)
                mes = "Это слово было красным"

            elif word in blue_words:
                all_words.remove(word)
                blue_words.remove(word)
                mes = "Это слово было синим"
                game["teams"]["queue"] = "bc"

            elif word in grey_words:
                all_words.remove(word)
                grey_words.remove(word)
                mes = "Это слово было белым"
                game["teams"]["queue"] = "bc"

            else:
                game["game_settings"]["game_status"] = 2
                mes = "Это было черное слово\nКоманда красных проиграла"

            for id in all_players_ids:
                try:
                    bot.send_message(id, mes)
                except:
                    pass

        elif player_role == "bt":
            word = message.text.strip().lower()
            all_words = game["field"]["all_words"]
            red_words = game["field"]["red_words"]
            blue_words = game["field"]["blue_words"]
            grey_words = game["field"]["grey_words"]
            if word != "пропустить":
                if word not in all_words:
                    bot.send_message(player_id, "Такого слова нет")
                    return

            for id in all_players_ids:
                try:
                    bot.send_message(id, f"[Команда синих]\n{word}")
                except:
                    pass

            if word == "пропустить":
                game["teams"]["queue"] = "rc"
                mes = "Синие пропустили ход"

            elif word in red_words:
                all_words.remove(word)
                red_words.remove(word)
                mes = "Это слово было красным"
                game["teams"]["queue"] = "rc"

            elif word in blue_words:
                all_words.remove(word)
                blue_words.remove(word)
                mes = "Это слово было синим"

            elif word in grey_words:
                all_words.remove(word)
                grey_words.remove(word)
                mes = "Это слово было белым"
                game["teams"]["queue"] = "rc"

            else:
                game["game_settings"]["game_status"] = 2
                mes = "Это было черное слово\nИгра окончена\nКоманда синих проиграла"

            for id in all_players_ids:
                try:
                    bot.send_message(id, mes)
                except:
                    pass

        if not game["field"]["red_words"]:
            game["game_settings"]["game_status"] = 2
            for id in all_players_ids:
                try:
                    bot.send_message(id, "Игра окончена\nКрасные победили")
                except:
                    pass
        if not game["field"]["blue_words"]:
            game["game_settings"]["game_status"] = 2
            for id in all_players_ids:
                try:
                    bot.send_message(id, "Игра окончена\nСиние победили")
                except:
                    pass

        with open(f"games/{game_id}.json", "w", encoding="utf-8") as file:
            json.dump(game, file, indent=4, ensure_ascii=False)

        if game["game_settings"]["game_status"] != 2:
            for player_id in all_players_ids:
                if player_id in (game["teams"]["red_team_cap"], game["teams"]["blue_team_cap"]):
                    field = game["field"]["all_words"]
                    n_field = []
                    for word in field:
                        if word in game["field"]["red_words"]:
                            n_field.append(f"{word}(К)")
                        elif word in game["field"]["blue_words"]:
                            n_field.append(f"{word}(С)")
                        elif word == game["field"]["black_word"]:
                            n_field.append(f"{word}(Ч)")
                        else:
                            n_field.append(f"{word}(Б)")

                    bot.send_message(player_id, "\n".join(n_field))

                else:
                    field = game["field"]["all_words"]
                    bot.send_message(player_id, "\n".join(field))


                if game["teams"]["queue"] == "bc":
                    bot.send_message(player_id, "Ход капитана синих")
                if game["teams"]["queue"] == "rc":
                    bot.send_message(player_id, "Ход капитана красных")
                if game["teams"]["queue"] == "bt":
                    bot.send_message(player_id, "Ход синей команды")
                if game["teams"]["queue"] == "rt":
                    bot.send_message(player_id, "Ход красной команды")




    else:
        bot.send_message(message.chat.id, "А где игра?")


@bot.message_handler(commands=['start'])
def start_massage(message):
    with open("players.json", "r") as file:
        players = json.load(file)
    if str(message.chat.id) not in players.keys():
        players[message.chat.id] = {
            "game_id": "",
            "game_password": ""
        }
    with open("players.json", "w") as file:
        json.dump(players, file, indent=4, ensure_ascii=False)
    bot.send_message(message.chat.id, "Привет [текст]\nСписок доступных команд:\n/create - создать новую игру\n/join - присоединиться к существующей игре\n/game_start - запустить игру\n/exit - выйти из текущей игры")


@bot.message_handler(commands=['create'])
def create_game(message):
    players = get_players_json()

    if players[str(message.chat.id)]["game_id"] != "":
        bot.send_message(message.chat.id, "Вы не можете создать новую игру, пока участвуете в другой")

    game_id = create_random_game_id()
    game_password = create_random_game_password()
    with open(f"games/{game_id}.json", "w", encoding="utf-8") as file:
        game_json = {
            "game_settings": {
                "game_id": game_id,
                "game_password": game_password,
                "game_status": 0,
                "creater": str(message.chat.id),
            },
            "teams": {
                "all_players": [str(message.chat.id)],
                "red_team": [],
                "blue_team": [],
                "red_team_cap": "",
                "blue_team_cap": "",
                "queue": ""
            },
            "field": {
                "all_words": [],
                "red_words": [],
                "blue_words": [],
                "grey_words": [],
                "black_word": [],
                "key": []
            }
        }

        json.dump(game_json, file, indent=4, ensure_ascii=False)

    players[str(message.chat.id)] = {
        "game_id": game_id,
        "game_password": game_password
    }
    set_players_json(players)

    bot.send_message(message.chat.id, f"Игра создана\nid: {game_id}\npassword: {game_password}")


@bot.message_handler(commands=['join'])
def join_game(message):
    players = get_players_json()

    if players[str(message.chat.id)]["game_id"] != "":
        bot.send_message(message.chat.id, "Вы не можете присоединиться к новой игре, так как уже участвуете в другой")
        return

    players[str(message.chat.id)] = {
        "game_id": "...",
        "game_password": ""
    }
    set_players_json(players)

    bot.send_message(message.chat.id, "Пожалуйста введите id игры")


@bot.message_handler(commands=['exit'])
def exit(message):
    players = get_players_json()

    with open(f"games/{players[str(message.chat.id)]['game_id']}.json", "r", encoding="utf-8") as file:
        game_data = json.load(file)

    game_data["teams"]["all_players"].remove(str(message.chat.id))

    with open(f"games/{players[str(message.chat.id)]['game_id']}.json", "w", encoding="utf-8") as file:
        json.dump(game_data, file, indent=4, ensure_ascii=False)

    players[str(message.chat.id)]["game_id"] = ""
    players[str(message.chat.id)]["game_password"] = ""

    set_players_json(players)

    bot.send_message(message.chat.id, "Вы покинули игру")


@bot.message_handler(commands=['game_start'])
def game_start(message):
    players = get_players_json()

    with open(f"games/{players[str(message.chat.id)]['game_id']}.json", "r", encoding="utf-8") as file:
        game_data = json.load(file)

    if game_data["game_settings"]["creater"] != str(message.chat.id):
        bot.send_message(message.chat.id, "Начать игру может только создатель")
        return

    if len(game_data["teams"]["all_players"]) < 4:
        bot.send_message(message.chat.id, "Вы не можете начать игру, если игроков меньше 4")
        return

    game = game_start_config(players[str(message.chat.id)]["game_id"])
    for player_id in game["teams"]["all_players"]:
        try:
            bot.send_message(player_id, "Игра начинается")
            bot.send_message(player_id,
                             f"Ты играешь за команду {['красных', 'синих'][player_id in game['teams']['blue_team']]}")
            if player_id in (game["teams"]["red_team_cap"], game["teams"]["blue_team_cap"]):
                bot.send_message(player_id, "Ты капитан")
                field = game["field"]["all_words"]
                n_field = []
                for word in field:
                    if word in game["field"]["red_words"]:
                        n_field.append(f"{word}(К)")
                    elif word in game["field"]["blue_words"]:
                        n_field.append(f"{word}(С)")
                    elif word == game["field"]["black_word"]:
                        n_field.append(f"{word}(Ч)")
                    else:
                        n_field.append(f"{word}(Б)")

                bot.send_message(player_id, "\n".join(n_field))

            else:
                field = game["field"]["all_words"]
                bot.send_message(player_id, "\n".join(field))

            bot.send_message(player_id, "Ход капитана синей команды")
        except:
            pass


@bot.message_handler(content_types=['text'])
def text(message):
    players = get_players_json()

    if players[str(message.chat.id)]["game_id"] == "...":
        if message.text in get_games_id():
            players[str(message.chat.id)]["game_id"] = message.text
            players[str(message.chat.id)]["game_password"] = "..."
            bot.send_message(message.chat.id, "Ведите пароль")
        else:
            bot.send_message(message.chat.id, "Такой игры не существует")

    elif players[str(message.chat.id)]["game_password"] == "...":
        with open(f"games/{players[str(message.chat.id)]['game_id']}.json", "r", encoding="utf-8") as file:
            game_data = json.load(file)

        if message.text == game_data["game_settings"]["game_password"]:
            players[str(message.chat.id)]["game_password"] = message.text
            game_data["teams"]["all_players"].append(str(message.chat.id))

            with open(f"games/{players[str(message.chat.id)]['game_id']}.json", "w", encoding="utf-8") as file:
                json.dump(game_data, file, indent=4, ensure_ascii=False)

            bot.send_message(message.chat.id, "Вы успешно подключились к игре")
        else:
            bot.send_message(message.chat.id, "Пароль неверный")

    else:
        game_message(message)

    set_players_json(players)


bot.infinity_polling()
