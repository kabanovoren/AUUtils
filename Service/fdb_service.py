import fdb
import os
import configparser as c
from winreg import *
from pathlib import Path
import logging

def get_name_file(file):
    global inifile, sqlfile, path, log_file, logger
    inifile = os.path.splitext(file)[0]+'.ini'
    sqlfile = os.path.splitext(file)[0]+'.xml'
    log_file = os.path.splitext(file)[0]+'.log'
    path = os.path.dirname(file)
    logger = _create_logs()


# Создание лога
def _create_logs(name_modul=Path(__file__).stem):
    logger = logging.getLogger(name_modul)
    logger.setLevel(logging.INFO)
    # create the logging file handler
    fh = logging.FileHandler(globals()['log_file'])
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    # add handler to logger object
    logger.addHandler(fh)
    return logger

# Функция логированя
def logs(message):
    logger.info(message)
    print(message)

def get_setting_bd(inifile=''):
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
    config = c.ConfigParser()
    config.read(inifile)
    try:
        path = config['BD']['path']
        if path != '':
            bd = []
            bd_file = os.listdir(path=path)
            for database in bd_file:
                bd.append(path + database)
        if config['BD']['DatabaseName'] != '':
            bd.append([config['BD']['DatabaseName']])
        host = config['BD']['host']
        port = config['BD']['port']
        fbclient = config['BD']['fbclient']
    except Exception as ex:
        logs(f'INI файл не найден, путь БД из реестра {ex}')
    logs(f'База данных:{bd} Хост:{host} Порт: {str(port)} {fbclient}')
    return bd, host, int(port), fbclient


def connect_fdb(setting):
    bd, host, port, fbclient = get_setting_bd(setting)
    try:
        con = fdb.connect(database=bd, user='sysdba', password='masterkey',
                          charset='win1251', host=host, port=port, fb_library_name=fbclient)
        logs(f'=========Подключение к {bd} УСПЕШНО!=========')
        return con.cursor()
    except Exception as ex:
        logs(f'=========Подлкючение не удалось {ex}=========')
        exit()


def disconnect_fdb(con):
    con.close()
    logs(f'=========Отключение от базы {con.connection.database_name}==============')


class sql_text():
    def __init__(self):
        pass

    def load_file_sql(self, file):
        with open(file, 'r') as file:
            return file.readlines()

    def get_sql(self, sql):
        file = self.load_file_sql('fdb_service.log')
        for line in file:
            if line == sql:
                return sql
def main():
    sql = sql_text()
    print(sql.get_sql('fdb_service'))


if __name__ == '__main__':
    main()
