import fdb

from Service import log, get_files_name, get_params_bd

class Database(fdb.Cursor):
    """Класс подключения к БД Firebird для Аптеки-Урал"""

    def __init__(self):
        param_connect_bd = get_params_bd()
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
    con = Database()
    con.disconnect()



if __name__ == '__main__':
    main()
