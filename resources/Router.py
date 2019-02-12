import random


class Router:

    def db_for_read(self, model, **hints):
        return random.choice(["slave1", "slave2", "slave3"])
        # return "default"

    def db_for_write(self, model, **hints):
        return "default"
