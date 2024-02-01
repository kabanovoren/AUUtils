import configparser as c
import os
import sys
import logging
from winreg import *



def get_files_name():
    """Получение списка наименований файлов"""
    try:
        app_name = os.path.basename(sys.orig_argv[9])  # Имя файла для дебага
        path = os.path.dirname(sys.orig_argv[9]) + '\\'
    except:
        app_name = os.path.basename(sys.orig_argv[1])  # Имя файла с расширением
        path = os.path.dirname(sys.orig_argv[1]) + '\\'

    app_name_ext = os.path.splitext(app_name)[0]  # Имя файла без расширения
    app_name_full = path + app_name
    inifile = path + app_name_ext + '.ini'
    xmlfile = path + app_name_ext + '.xml'
    logfile = path + app_name_ext + '.log'
    return {'app_name': app_name, 'app_name_ext': app_name_ext, 'app_name_full': app_name_full,
            'inifile': inifile, 'xmlfile': xmlfile, 'logfile': logfile, 'path': path}



def get_connect_param_inifile(inifile):
    """Получение параметров для подключения из ini файла"""
    config = c.ConfigParser()
    config.read(inifile)
    try:
        bd = config['BD']['DatabaseName']
        host = config['BD']['host']
        port = config['BD']['port']
        fbclient = config['BD']['fbclient']
        return {'bd': bd, 'port': int(port), 'host': host, 'fbclient': fbclient}
    except Exception as ex:
        log(f'Настройки отсутствуют в {inifile}, путь БД из реестра {ex}')

def get_mdlp_param_inifile(inifile):
    config = c.ConfigParser()
    config.read(inifile)
    try:
        client_id = config['mdlp']['client_id']
        client_secret = config['mdlp']['client_secret']
        user_id = config['mdlp']['user_id']
        url = config['mdlp']['url']
        return {'client_id': client_id, 'client_secret': client_secret, 'user_id': user_id, 'url': url}
    except Exception as ex:
        log(f'Настройки отсутствуют в {inifile}, подключение к МДЛП невозможно!!!')


def get_mdlp_param():
    inifile = get_files_name()['inifile']
    return get_mdlp_param_inifile(inifile)



def get_params_bd():
    """Получение параметров для подключения к БД"""
    if get_connect_param_inifile(get_files_name()['inifile']) is None:
        key = OpenKey(HKEY_CURRENT_USER, r'SOFTWARE\Aurit\По умолчанию', 0, KEY_ALL_ACCESS)
        bd_key = QueryValueEx(key, "DatabaseFile")
        bd_str = bd_key[0]
        bd_str = bd_str.partition(':')
        bd = bd_str[2]
        host_str = bd_str[0]
        port = host_str.partition('/')[2]
        if port == '':
            port = 3050
        host = host_str.partition('/')[0]
        fbclient = f'{os.path.dirname(os.getcwd())}\\Service\\fbclient.dll'
        if not os.path.exists(fbclient):
            fbclient = f'{get_files_name()["path"]}\\Service\\fbclient.dll'
        return {'bd': bd, 'port': int(port), 'host': host, 'fbclient': fbclient}
    else:
        return get_connect_param_inifile(get_files_name()['inifile'])

class Logs:
    """Класс логирования"""

    def __init__(self):
        logfile = get_files_name()['app_name_ext']
        # logfile = 'mdlp.log'
        self.logger = logging.getLogger(logfile)
        self.logger.setLevel(logging.INFO)
        # create the logging file handler
        # fh = logging.FileHandler(_get_files_name()['logfile'], encoding='utf-8')
        fh = logging.FileHandler(get_files_name()['logfile'])
        # fh = logging.FileHandler('mdlp.log')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        # add handler to logger object
        self.logger.addHandler(fh)

    def message(self, message, type_message='i'):
        if type_message == 'i':
            self.info(message)
        elif type_message == 'e':
            self.error(message)

    def info(self, message):
        self.logger.info(message)
        print(message)

    def error(self, message):
        self.logger.error(message)
        print(message)

logger = Logs()



def log(message, type_message='i'):
    """Функция логирования"""
    logger.message(message, type_message)

def main():
    pass


if __name__ == '__main__':
    main()

