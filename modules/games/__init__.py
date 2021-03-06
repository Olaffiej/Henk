import pickle
import time

import telepot

from ..base import Module

from .klaverjas_game import Klaverjas, KlaverjasDispatcher, KlaverjasChallenge, KLAVERJASSEN

#game_identifier = {KLAVERJASSEN: "k"}


class Games(Module):
    def initialise(self, bot):
        bot.games = {}
        games = bot.dataManager.get_active_games()
        for g in games:
            game = pickle.loads(g['game_data'])
            game.setstate(bot)
            bot.games[g['game_id']] = game
        #self.gamestarters = []

    def register_commands(self, bot):
        bot.add_slash_command("klaverjassen", self.klaverjassen)
        bot.add_slash_command("klaverchallenge", self.klaverchallenge)
        #bot.add_callback_query("gamestart", self.callbackstart)
        bot.add_callback_query("games", self.callback)

    def klaverjassen(self, bot, msg):
        ident = len(bot.dataManager.games)
        if msg.chat_type == "private":
            g = Klaverjas(bot, ident, [(msg.sender,msg.sendername)], msg.date, msg.command.strip())
        else:
            g = KlaverjasDispatcher(bot, ident, msg)
        bot.games[ident] = g

    def klaverchallenge(self, bot, msg):
        ident = len(bot.dataManager.games)
        g = KlaverjasChallenge(bot, ident, msg)
        bot.games[ident] = g

    def callback(self, bot, msg):
        query_id, from_id, data = telepot.glance(msg, flavor='callback_query')
        game_id, callback_id, button_id = [int(s) for s in data[5:].split(":")]
        ident, func = bot.games[game_id].callbacks[callback_id]
        s = func(ident, button_id,(msg['from']['id'],msg['from']['first_name']))
        if s: bot.telebot.answerCallbackQuery(query_id, s)

    # def callbackstart(self, bot, msg):
    #     query_id, from_id, data = telepot.glance(msg, flavor='callback_query')
    #     callback_id, button_id = [int(s) for s in data[9:].split(":")]
    #     try:
    #         d = msg["date"]
    #     except:
    #         d = int(time.time())
    #     s = self.gamestarters[callback_id].callback(button_id,msg['from']['id'],msg['from']['first_name'], d)
    #     if s: 
    #         query_id, from_id, data = telepot.glance(msg, flavor='callback_query')
    #         bot.telebot.answerCallbackQuery(query_id, s)

    # def is_games_message(self, msg):
    #     if not msg.sender in self.active_users: return False
    #     game_id = self.active_users[msg.sender]
    #     g = self.games[game_id]
    #     ident = game_identifier[g.game_type]
    #     if msg.raw.startswith(ident) and len(msg.raw)==2:
    #         if msg.sender in g.current_users: return True
    #     return False

    # def parse_message(self, bot, msg):
    #     game_id = self.active_users[msg.sender]
    #     g = self.games[game_id]
    #     msg.command = msg.raw[1:]
    #     g.parse_message(msg)

games = Games()
