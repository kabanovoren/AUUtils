import fdb
import os
import sys
import configparser as c
from winreg import *
import logging


def _get_files_name():
    """Получение списка наименований файлов"""
    app_name = os.path.basename(sys.orig_argv[1])  # Имя файла с расширением
    app_name_ext = os.path.splitext(app_name)[0]  # Имя файла без расширения
    path = os.path.dirname(sys.orig_argv[1]) + '\\'
    app_name_full = path + app_name
    inifile = path + app_name_ext + '.ini'
    xmlfile = path + app_name_ext + '.xml'
    logfile = path + app_name_ext + '.log'
    return {'app_name': app_name, 'app_name_ext': app_name_ext, 'app_name_full': app_name_full,
            'inifile': inifile, 'xmlfile': xmlfile, 'logfile': logfile, 'path': path}


class Logs:
    """Класс логирования"""

    def __init__(self):
        logfile = _get_files_name()['app_name_ext']
        self.logger = logging.getLogger(logfile)
        self.logger.setLevel(logging.INFO)
        # create the logging file handler
        # fh = logging.FileHandler(_get_files_name()['logfile'], encoding='utf-8')
        fh = logging.FileHandler(_get_files_name()['logfile'])
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


def _get_param_inifile(inifile):
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
        log(f'INI файл {inifile} не найден, путь БД из реестра {ex}')


def _get_params_bd():
    """Получение параметров для подключения к БД"""
    if _get_param_inifile(_get_files_name()['inifile']) is None:
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
            fbclient = f'{_get_files_name()["path"]}\\Service\\fbclient.dll'
        return {'bd': bd, 'port': int(port), 'host': host, 'fbclient': fbclient}
    else:
        return _get_param_inifile(_get_files_name()['inifile'])


class Database(fdb.Cursor):
    """Класс подключения к БД Firebird для Аптеки-Урал"""

    def __init__(self):
        param_connect_bd = _get_params_bd()
        self.con = fdb.connect(database=param_connect_bd['bd'], user='sysdba', password='masterkey',
                               charset='win1251', host=param_connect_bd['host'], port=param_connect_bd['port'],
                               fb_library_name=param_connect_bd['fbclient'])

        super().__init__(connection=self.con, transaction=self.con.main_transaction)
        # log(f"===========Проблема с подключением к БД {param_connect_bd['bd']}=========")
        log(f"=========Подключение к {param_connect_bd['bd']} УСПЕШНО!=========")

    def disconnect(self):
        log(f'=========Отключение от базы {self.con.database_name}==============')
        self.con.close()


def main():
    log("12321", )
    # con = Database()
    #
    # fd = con.execute('select * from oper').fetchall()
    # print(fd)
    #
    # con.disconnect()
    # con.disconnect()


if __name__ == '__main__':
    main()
