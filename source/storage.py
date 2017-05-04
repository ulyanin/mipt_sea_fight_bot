#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import redis
import config
import json


class Storage:
    def __init__(self):
        self.kv_storage = redis.StrictRedis(host=config.r_hostname,
                                            port=config.r_port, db=config.r_db)

    def get(self, session, key):
        value = self.kv_storage.get(json.dumps((session, key)))
        if value is not None:
            return json.loads(value)
        return value

    def put(self, session, key, value):
        return self.kv_storage.set(
            json.dumps((session, key)),
            json.dumps(value)
        )

    def delete(self, session, key):
        return self.kv_storage.delete(
            json.dumps((session, key))
        )

    def is_already_started(self, session_id):
        return self.get(session_id, "started") is not None

    @staticmethod
    def create_field_(field_size):
        return [[0] * field_size for _ in range(field_size)]

    def start_the_game(self, session_id, field_size=10):
        self.put(session_id, "field_size", field_size)
        self.put(session_id, "user", self.create_field_(field_size))
        self.put(session_id, "bot", self.create_field_(field_size))
        self.put(session_id, "started", "started")
        self.put(session_id, "step", 0)
        print("successfully started")

    def end_the_game(self, session_id):
        self.delete(session_id, "started")
        self.delete(session_id, "bot")
        self.delete(session_id, "user")
        self.delete(session_id, "step")
        print("successfully stopped")

    def get_board(self, session_id, who):
        """
        returns field of <who> = user || bot
        :param session_id: message.chat.id  
        :param who: string
        :return: 
        """
        return self.get(session_id, who)
