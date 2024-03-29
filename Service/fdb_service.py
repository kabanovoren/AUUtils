import fdb
import os
import configparser as c
from winreg import *
from pathlib import Path
import logging
import xml.etree.ElementTree as ET


def get_name_file(file):
    global inifile, sqlfile, path, log_file, logger
    inifile = os.path.splitext(file)[0]+'.ini'
    sqlfile = os.path.splitext(file)[0]+'.xml'
    log_file = os.path.splitext(file)[0]+'.log'
    path = os.path.dirname(file)
    logger = _create_logs()
    return [inifile, sqlfile, path, log_file, logger]


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

def get_setting_bd(inifile='', path=''):
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
        fbclient = f'{path}\\Service\\fbclient.dll'
    logs(fbclient)
    config = c.ConfigParser()
    config.read(inifile)
    try:
        bd = config['BD']['DatabaseName']
        host = config['BD']['host']
        port = config['BD']['port']
        fbclient = config['BD']['fbclient']
    except Exception as ex:
        logs(f'INI файл {inifile} не найден, путь БД из реестра {ex}')
    logs(f'База данных:{bd} Хост:{host} Порт: {str(port)} {fbclient}')
    return bd, host, int(port), fbclient

def connect_fdb(setting='', path=''):
    bd, host, port, fbclient = get_setting_bd(setting, path)
    try:
        # Подключение к СМ (меняем пароль, остальные настройки в ini)
        # con = fdb.connect(database=bd, user='sysdba', password='wpn47L',
        #                   charset='win1251', host=host, port=port, fb_library_name=fbclient)
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


class sql():
    def __init__(self):
        self.name_file = globals()['sqlfile']
        self.file = self.load_file_sql()


    def load_file_sql(self):
        if not os.path.exists(self.name_file):
            self.save_file_sql(data_list=[])
        tree = ET.parse(self.name_file)
        root = tree.getroot()
        items = root.findall("Скрипт")
        data = []
        for chield in items:
            name_item = chield.find("НаименованиеСкрипта").text
            pos_item = chield.find("ПозицияЗапуска").text
            text_item = chield.find("ТекстСкрипта").text
            data.append({"name_item": name_item, "pos_item":pos_item, "text_item":text_item})
        return data


    def save_file_sql(self, data_list):
        data = ET.Element('СписокСкриптов')
        for line in data_list:
            item = ET.SubElement(data, 'Скрипт')
            name_item = ET.SubElement(item, 'НаименованиеСкрипта')
            pos_item = ET.SubElement(item, 'ПозицияЗапуска')
            text_item = ET.SubElement(item, 'ТекстСкрипта')
            name_item.text = line['name_item']
            pos_item.text = line['pos_item']
            text_item.text =line['text_item']
        mydata = '<?xml version="1.0" encoding="windows-1251"?>'
        mydata = mydata + ET.tostring(data, encoding='unicode')

        with open(self.name_file, "w", encoding='windows-1251') as file:
            file.write(mydata)

    def get_sql(self, sql):
        file = self.load_file_sql()
        for line in file:
            if line == sql:
                return sql
def main():
    pass
    # get_name_file(__file__)
    # s = sql()
    # s.save_file_sql([{'name_item':'fdsf','pos_item':'fdafd','text_item':'qwerer'},
    #                  {'name_item':'Второй пример','pos_item':'1,2','text_item':'select * from prep where id_prep =34'}])
    # data = s.load_file_sql()
    # print(data)
    # # print(sql.get_sql('fdb_service'))


if __name__ == '__main__':
    main()
