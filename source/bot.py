#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import telebot
import config
import storage as key_value_storage
import messages
import exception
import field_drawer

bot = telebot.TeleBot(config.token)
storage = key_value_storage.Storage()


def start_new_game(message, field_size):
    session_id = message.chat.id
    storage.start_the_game(session_id, field_size)


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
        print("exception catcher")
        try:
            res = func(*args, **kwargs)
        except Exception as e:
            print(e)
        return res
    return wrapper


@bot.message_handler(commands=['start'])
@arguments_types(int)
def start_the_game(message, field_size=10):
    """
    starting the sea fight game with user or chat
    :param message
    :param field_size
    :return
    """
    try:
        session_id = message.chat.id
        print(message)
        if storage.is_already_started(session_id):
            print("already_started")
            bot.send_message(message.chat.id, messages.is_already_started)
        else:
            print("starting new game")
            start_new_game(message, field_size)
    except Exception as e:
        print(e)


@bot.message_handler(commands=["end"])
def end_game(message):
    session = message.chat.id
    if storage.is_already_started(session):
        storage.end_the_game(session)
    else:
        bot.send_message(message.chat.id, "sorry, but you have not got started game")


@bot.message_handler(commands=["show_my_board"])
def show_my_board(message):
    session = message.chat.id
    field_size = storage.get(session, "field_size")
    board = storage.get_board(session, "user")
    drawer = field_drawer.FieldDrawer(field_size, board)
    img = drawer.img()
    bot.send_photo(chat_id=message.chat.id, photo=img)


# @bot.message_handler(commands=["cmd"])
# @exception_catcher
# @arguments_types(int, int)
# def cmd_bot(message, param1, param2=100500):
#     print("param=", param1, param2)


@bot.message_handler(commands=["help"])
def help_bot(message):
    bot.send_message(message.chat.id, messages.msg_help)


@bot.message_handler(content_types=["text"])
def repeat_all_messages(message):
    """
    repeats whole the messages
    :param message:
    :return:
    """
    # print(message)
    bot.reply_to(message, message.text)


if __name__ == '__main__':
    bot.polling(none_stop=True)
