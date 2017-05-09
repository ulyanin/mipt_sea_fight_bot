#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import random

import telebot
import logging
from telebot import types
import config
import storage as key_value_storage
import messages
import field_drawer
import sea_fight_logic

logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)
bot = telebot.TeleBot(config.token)
storage = key_value_storage.Storage()


def start_new_game(message, field_size):
    session_id = message.chat.id
    storage.start_the_game(session_id, field_size)
    bot.send_message(message.chat.id, messages.game_starting)
    bot_field = sea_fight_logic.generate_random_field(field_size)
    storage.put(session_id, "bot", bot_field)
    storage.put(session_id, "ships_arrangement", True)


def get_current_board(session):
    user_board = storage.get(session, "user")
    user_board_stricken = storage.get(session, "user_stricken")
    user_board_hidden = storage.get(session, "user_hidden")
    bot_board = storage.get(session, "bot")
    bot_board_stricken = storage.get(session, "bot_stricken")
    bot_board_hidden = storage.get(session, "bot_hidden")
    field_size = storage.get(session, "field_size")
    drawer = field_drawer.FieldDrawer(field_size, user_board, user_board_stricken, user_board_hidden,
                                      bot_board, bot_board_stricken, bot_board_hidden)
    return drawer.img()


def arguments_types(*arg_types):
    """
    by the tuple of argument types extract parameters from message
    and applies it to wrapped function
    :param arg_types: tuple
    :return: function
    """
    def decorator(func):
        def wrapper(message, **kwargs):
            parsed = message.text.split()[1:]
            print(parsed)
            parsed = [type_(param) for type_, param in zip(arg_types, parsed)]
            return func(message, *parsed, **kwargs)
        return wrapper
    return decorator


def arguments(func):
    def wrapper(message, **kwargs):
        parsed = message.text.split()[1:]
        return func(message, *parsed, **kwargs)
    return wrapper


def exception_catcher(func):
    def wrapper(*args, **kwargs):
        res = None
        logger.debug("exception catcher")
        try:
            res = func(*args, **kwargs)
        except Exception as e:
            logger.exception("Exception: '" + str(e) + "'")
        return res
    return wrapper


def show_inline_field(message):
    session = message.chat.id
    field_size = storage.get(session, "field_size")
    field = storage.get(session, "bot_stricken")
    markup = types.InlineKeyboardMarkup(row_width=1)
    for i in range(field_size):
        markup.row(*[
            types.InlineKeyboardButton(
                'X' if field[i][j] else 'O',
                callback_data=json.dumps((i, j))
            ) for j in range(field_size)
        ])
    bot.send_message(message.chat.id, text='make your choice', reply_markup=markup)


def show_keyboard_field(message):
    session = message.chat.id
    field_size = storage.get(session, "field_size")
    bot_stricken_field = storage.get(session, "bot_stricken")
    bot_field = storage.get(session, "bot")
    bot_hidden_field = storage.get(session, "bot_hidden")
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    for i in range(field_size):
        markup.row(*[
            types.KeyboardButton(
                'X' if bot_field[j][i] and bot_stricken_field[j][i] else
                'O' if bot_stricken_field[j][i] else
                'o' if bot_hidden_field[j][i] else
                chr(ord('A') + j) + str(i)
            ) for j in range(field_size)
        ])
    bot.send_message(message.chat.id, text='make your choice', reply_markup=markup)


@bot.message_handler(commands=['start'])
@arguments_types(int)
@exception_catcher
def start_the_game(message, field_size=10):
    """
    starting the sea fight game with user or chat
    :param message
    :param field_size
    :return
    """
    field_size = max(9, field_size)
    session_id = message.chat.id
    print(message)
    if storage.is_already_started(session_id):
        logger.debug("already started")
        bot.send_message(message.chat.id, messages.is_already_started)
    else:
        logger.debug("starting new game")
        start_new_game(message, field_size)


@bot.message_handler(commands=["random"])
@exception_catcher
def random_ships_arrangement(message):
    session = message.chat.id
    logger.debug("{} is doing random ships arrangement".format(session))
    if storage.get(session, "ships_arrangement"):
        field_size = storage.get(session, "field_size")
        field = sea_fight_logic.generate_random_field(field_size)
        storage.put(session, "user", field)
        storage.delete(session, "ships_arrangement")
        bot.send_photo(message.chat.id,
                       caption="successfully generated",
                       photo=get_current_board(session))
        show_keyboard_field(message)
        # show_inline_field(message)
    else:
        bot.reply_to(message, "unavailable action")


@bot.message_handler(commands=["manually"])
@exception_catcher
def random_ships_arrangement(message):
    session = message.chat.id
    logger.debug("{} is doing random ships arrangement".format(session))
    if storage.get(session, "ships_arrangement"):
        bot.reply_to(message, "not implemented yet")
        field_size = storage.get(session, "field_size")
        field = sea_fight_logic.generate_random_field(field_size)
        storage.put(session, "user", field)
        storage.delete(session, "ships_arrangement")
        bot.send_message(message.chat.id, "successfully generated")
    else:
        bot.reply_to(message, text="unavailable action")


@bot.message_handler(commands=["end_game"])
def end_game(message):
    logger.debug("{} is ending the game".format(message.chat.id))
    session = message.chat.id
    if storage.is_already_started(session):
        storage.end_the_game(session)
    else:
        bot.send_message(message.chat.id, "sorry, but you have not got any started game")


@bot.message_handler(commands=["show_my_board"])
def show_my_board(message):
    session = message.chat.id
    bot.send_photo(chat_id=message.chat.id, photo=get_current_board(session))
    # show_inline_field(message)
    show_keyboard_field(message)


# @bot.callback_query_handler(func=lambda call: True)
# @exception_catcher
# def callback_handler(callback):
#     print(callback)
#     message = callback.message
#     print(message)
#     session, x, y = json.loads(callback.data)
#     storage.set_board(session, "bot_stricken", x, y)
#     bot.edit_message_text("done", chat_id=message.chat.id, message_id=message.message_id)
#     bot.send_photo(chat_id=message.chat.id, photo=get_current_board(session))
#     show_inline_field(message)
#     bot.edit_message_reply_markup("done")


@bot.message_handler(commands=["help"])
@exception_catcher
def help_bot(message):
    bot.send_message(message.chat.id, messages.msg_help)


def hide_nearby_cells(session, who, x, y):
    field_size = storage.get(session, "field_size")
    for i in [-1, 0, 1]:
        for j in [-1, 0, 1]:
            n_x = x + i
            n_y = y + j
            if 0 <= n_x < field_size and 0 <= n_y < field_size:
                storage.set_board(session, who + "_hidden", n_x, n_y)


def damage(session, who, x, y):
    field_size = storage.get(session, "field_size")
    board = storage.get(session, who)
    # board_hidden = storage.get(session, who + "_hidden")
    storage.set_board(session, who + "_stricken", x, y)
    storage.set_board(session, who + "_hidden", x, y)
    board_stricken = storage.get(session, who + "_stricken")
    if board[x][y]:
        for i in [-1, 1]:
            for j in [-1, 1]:
                n_x = x + i
                n_y = y + j
                if 0 <= n_x < field_size and 0 <= n_y < field_size:
                    storage.set_board(session, who + "_hidden", n_x, n_y)
        # check if the ship was killed
        was_killed = True
        for v in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
            for i in range(4):
                n_x = x + v[0] * i
                n_y = y + v[1] * i
                if not (0 <= n_x < field_size and 0 <= n_y < field_size):
                    break
                if not board[n_x][n_y]:
                    break
                if board[n_x][n_y] and not board_stricken[n_x][n_y]:
                    was_killed = False
        if was_killed:
            # we need to hidden all nearby cells
            bot.send_message(session, who + " ship was killed")
            for v in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
                for t in range(4):
                    n_x = x + v[0] * t
                    n_y = y + v[1] * t
                    if not (0 <= n_x < field_size and 0 <= n_y < field_size):
                        break
                    if not board[n_x][n_y]:
                        break
                    if board[n_x][n_y]:
                        hide_nearby_cells(session, who, n_x, n_y)


def do_bot_step(session):
    field_size = storage.get(session, "field_size")
    field = storage.get(session, "user_hidden")
    free_coordinates = [(i, j) for i in range(field_size)
                        for j in range(field_size) if not field[i][j]]
    x, y = random.choice(free_coordinates)
    damage(session, "user", x, y)


def is_won(session, who):
    field_size = storage.get(session, "field_size")
    board = storage.get(session, who)
    board_stricken = storage.get(session, who + "_stricken")
    for i in range(field_size):
        for j in range(field_size):
            if board[i][j] and not board_stricken[i][j]:
                return False
    return True


@bot.message_handler(regexp="^[A-J][0-9]$")
@exception_catcher
def do_step(message):
    session = message.chat.id
    logger.debug("do_step of {}".format(session))
    x = ord(message.text[0]) - ord('A')
    y = int(message.text[1:])
    if storage.get(session, "bot_stricken")[x][y]:
        bot.send_message(session, "that cell is already damaged")
    else:
        damage(session, "bot", x, y)
        do_bot_step(session)
    # bot.edit_message_text("done", chat_id=message.chat.id, message_id=message.message_id)
    bot.send_photo(chat_id=message.chat.id, photo=get_current_board(session))
    show_keyboard_field(message)
    if is_won(session, "user"):
        bot.send_message(message.chat.id, "bot has won you")
        storage.end_the_game(session)
    if is_won(session, "bot"):
        bot.send_message(message.chat.id, "You won!!!")
        storage.end_the_game(session)


@bot.message_handler(content_types=["text"])
@exception_catcher
def repeat_all_messages(message):
    """
    repeats whole the messages
    :param message:
    :return:
    """
    print("repeat:", message)
    # markup = types.ReplyKeyboardMarkup()
    # field_size = storage.get(session, "field_size")
    # field = storage.get(session, "bot_stricken")
    # markup = types.InlineKeyboardMarkup()
    # for i in range(field_size):
    #     markup.row(*[
    #         types.InlineKeyboardButton(
    #             str(field[i][j]),
    #             callback_data=json.dumps((session, i, j))
    #         ) for j in range(field_size)
    #     ])
    # bot.send_message(message.chat.id, text='make your choice', reply_markup=markup)
    bot.reply_to(message, "don't understand")


def run():
    bot.polling(none_stop=True)


if __name__ == '__main__':
    run()
