#!/usr/bin/python3

import telebot
import requests
from telebot import types
import logging
import os.path
import pytz
import sys
import configparser
import datetime
import getopt


### VERSION_BEGIN
version='1.0.4'
### VERSION_END


class Config:
    def __init__(self):
        self.token = None
        self.track_dir = None
        self.timezone = None
        self.log_level = 'INFO'

config = Config()

def usage_help(name):
    print("Usage: " + name + " -c <config file>\n\n")

def main(argv_all):
    global config

    print("XC Score telegram bot. Version: %s"%(version))
    
    config_file_name = None
    
    try:
        argv = argv_all[1:]
        opts, args = getopt.getopt(argv, 'hc:v', ['config=', 'help'])
    except getopt.GetoptError:
        print("Incorrect arguments")
        usage_help(argv_all[0]);
        sys.exit(2)

    for opt, arg in opts:
        if opt in ['-h', '--help']:
            usage_help(argv_all[0]);
            sys.exit()
        elif opt in ("-c", "--config"):
            config_file_name = arg

    if config_file_name == None:
        print("config isn't defined.")
        usage_help(argv_all[0]);
        sys.exit(2)
        
    
    read_config(config_file_name)

    logging.basicConfig(level=config.log_level, format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s')
    telebot.logger.setLevel(config.log_level)

    bot = telebot.TeleBot(config.token)

    @bot.message_handler(commands=['start'])
    def start(message):
        bot.send_message(message.from_user.id, "👋 Привет! Я сегодня принимаю треки! Отправьте пожалуйста трек с расширением IGC")

    @bot.message_handler(content_types=['text'])
    def get_text_messages(message):
        logging.debug("Text message")
        logging.debug("message.from_user.id: " + str(message.from_user.id))
        logging.debug("message.from_user.username: " + str(message.from_user.username))
        bot.send_message(message.from_user.id, "Не морочте мне голову болтовней.")

    @bot.message_handler(content_types=['document'])
    def get_document_messages(message):

        try:
            logging.debug("Document message")
            logging.debug("doc message:" + str(message))
            logging.debug("doc message type:" + str(type(message)))
            logging.debug("message.from_user.id: " + str(message.from_user.id))
            logging.debug("message.from_user.username: " + str(message.from_user.username))
            logging.debug("file_id: " + str(message.document.file_id))
            file_info = bot.get_file(message.document.file_id)
            tz = pytz.timezone(config.timezone)
            current_datetime = datetime.datetime.now(tz)
            date_str = str(current_datetime.strftime("%Y-%m-%d"))
            igc_file_name = date_str + "#" + message.from_user.username + "#" + message.document.file_name
            logging.debug("igc_file_name: " + str(igc_file_name))
            track_date_dir = os.path.join(config.track_dir, date_str)

                ### Create dir
            try:
                os.makedirs(track_date_dir)
            except FileExistsError:
                pass            

            track_date_path = os.path.join(track_date_dir, igc_file_name)

            resp = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(config.token, file_info.file_path))
            with open(track_date_path, "wb") as fout:
                fout.write(resp.content)
                bot.send_message(message.from_user.id, "Ваш трек сохранен и передан на обработку.")
        except Exception as e:
            logging.error("Exception:" + str(e))
            bot.send_message(message.from_user.id, "Что то пошло не так, трек не сохранен. Отправьте пожалуйста свой трек лично скореру.")
            raise(e)

    bot.polling(non_stop=True, interval=0) #обязательная для работы бота часть

def read_config(file_name):
    global config
    try:
        cParser = configparser.ConfigParser()
        f = open(file_name, encoding='utf-8')
        cParser.read_file(f)

        get_param(cParser, 'MAIN', 'token', config, 'token', str, True)
        get_param(cParser, 'MAIN', 'track_dir', config, 'track_dir', str, True)
        get_param(cParser, 'MAIN', 'timezone', config, 'timezone', str, True)
        get_param(cParser, 'MAIN', 'log_level', config, 'log_level', str, False)
        get_param(cParser, 'MAIN', 'log_file', config, 'log_file', str, False)

        if config.log_level not in ['DEBUG', 'INFO', 'ERROR']:
            raise MAIN_EXCEPTION('Incorrect log_level value: "%s"'%(config.log_level))


    except Exception as e:
        logging.error(f'config error: ' + str(e))
        sys.exit(1)

def get_param(cParser, section, object_var_name, conf_obj, param_name, param_type=str, mantatory_flag=True):
    if cParser == None:
        raise CONFIG_EXCEPTION("Incorrect use get_param()")
    if cParser.has_option(section, param_name):
        if param_type == bool:
            val = cParser[section].getboolean(param_name)
        else:
            val = cParser[section][param_name]
            if type(val) != param_type:
                if param_type == int:
                    try:
                        val = int(val)
                    except Exception as e:
                        raise CONFIG_EXCEPTION("Incorrect parameter value for %s:%s - %s"%(section, param_name, str(e)))
                else:
                    raise CONFIG_EXCEPTION("Unknow parameter type for %s:%s"%(section, param_name))

        setattr(conf_obj, object_var_name, val)
    else:
        if mantatory_flag:
            raise CONFIG_EXCEPTION("Error config: " + "[" + section +"]." + param_name +" MUST be defined")


if __name__ == '__main__':
    main(sys.argv)