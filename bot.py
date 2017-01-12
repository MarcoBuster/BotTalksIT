from config import *

import langdetect
import time

from botogram import create

import cleverbot

cw1 = cleverbot.Cleverbot()
cw2 = cleverbot.Cleverbot()


class TelegramBot:
    def __init__(self, token, name):
        self.bot = create(token)
        self.name = name
        self.chat_id = BOTCHAT

    def send(self, text):
        if DEBUG:
            print('{name}> {text}'.format(name=self.name, text=text))
            return

        self.bot.chat(self.chat_id).send(text, syntax='HTML')

bot1 = TelegramBot(BOT1_TOKEN, 'Bot 1')
bot2 = TelegramBot(BOT2_TOKEN, 'Bot 2')
sys = TelegramBot(SYS_TOKEN, 'Sys')

sys.send(START_MESSAGE)


def getwarns(msg, warn):
    try:
        langdetect.detect(msg)
    except Exception as e:
        return False, warn

    if len(msg[:-1]) == 1:
        warn *= 1.5

    if len([i for i in msg.split() if i.isalnum()]) < MIN_MESSAGE_LENGHT:
        return False, warn

    if langdetect.detect(msg) == 'it':
        if warn - REMOVE_WARN_VALUE > 0:
            warn -= REMOVE_WARN_VALUE
        else:
            warn = 0
        return False, warn

    old_warn = warn

    detected_langs = langdetect.detect_langs(msg)
    for value in detected_langs:
        lang = value.__dict__['lang']
        prob = value.__dict__['prob']

        if lang != LANG:
            if prob > LANG_TRIGGERED:
                warn += prob * LANG_TRIGGERED_MULTIPLIER
            elif prob > LANG_SECURE_TRIGGERED:
                warn += prob * LANG_SECURE_TRIGGERED_MULTIPLIER

    if old_warn == warn:
        if warn - REMOVE_WARN_VALUE > 0:
            warn -= REMOVE_WARN_VALUE
        else:
            warn = 0

    if warn > MAX_WARNINGS:
        return True, warn
    else:
        return False, warn


warn = 0
msg = FIRST_MESSAGE
while True:
    time.sleep(5)
    bot1.send(msg)
    msg = cw1.ask(msg)

    mustStopped, warn = getwarns(msg, warn)
    if mustStopped:
        sys.send(LANG_DETECT_WARNING)
        warn, msg = 0, FIRST_MESSAGE
        cw1 = cleverbot.Cleverbot()
        cw2 = cleverbot.Cleverbot()
        continue

    time.sleep(5)
    bot2.send(msg)
    msg = cw2.ask(msg)

    mustStopped, warn = getwarns(msg, warn)
    if mustStopped:
        sys.send(LANG_DETECT_WARNING)
        warn, msg = 0, FIRST_MESSAGE
        cw1 = cleverbot.Cleverbot()
        cw2 = cleverbot.Cleverbot()
        continue
