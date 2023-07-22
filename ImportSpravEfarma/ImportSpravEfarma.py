import os
import Service.fdb_service as service
import script
import configparser as c
import fdb
import csv


def get_file():
    data = []
    with open('sprav.csv', 'r', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter=';')
        for row in reader:
            data.append(row)
    return data

def clear_bd(inifile, path):
    con = service.connect_fdb(inifile, path)
    con.execute(script.SQL["delete_tovar"])
    service.logs("Удаление данных таблицы TOVAR выполнено")
    con.execute(script.SQL["update_firm"])
    con.execute(script.SQL["delete_firm"])
    service.logs("Удаление данных таблицы FIRM выполнено")
    con.execute(script.SQL["delete_prep_vat"])
    con.execute(script.SQL["delete_group_name_link"])
    con.execute(script.SQL["delete_prep"])
    service.logs("Удаление данных таблицы PREP выполнено")
    con.execute(script.SQL["delete_country"])
    service.logs("Удаление данных таблицы COUNTRY выполнено")
    con.execute(script.SQL["delete_farmgroup"])
    service.logs("Удаление данных таблицы FARMGROUP выполнено")
    con.transaction.commit()
    service.disconnect_fdb(con)


def insert_sprav(inifile, path, sprav):
    con = service.connect_fdb(inifile, path)
    for row in sprav[1:]:
        if row[5] == 'NULL' or row[5] == '':
            id_farmgroup = 0
        else:
            id_farmgroup = con.execute(script.SQL["farmgroup"] % row[5]).fetchone()[0]
        if row[1] == 'NULL':
            id_cs4 = 0
            name_cs4 = ''
        else:
            name_cs4 = row[1]
            id_cs4 = con.execute(script.SQL["cs4"] % name_cs4).fetchone()[0]
        if row[3] == 'NULL':
            id_country = 0
        else:
            id_country = con.execute(script.SQL["country"] % row[3]).fetchone()[0]
        if row[2] == 'NULL':
            id_firm = 0
        else:
            if row[3] == 'Россия':
                is_otech = 1
            else:
                is_otech = 0
            id_firm = con.execute(script.SQL["firm"] % (row[2].replace("'", "''"), id_country, is_otech)).fetchone()[0]

        id_prep = con.execute(script.SQL["prep"] % (row[0].replace("'", "''"), id_cs4, id_farmgroup, name_cs4)).fetchone()[0]
        con.execute(script.SQL["tovar"] % (row[4][:13], id_prep, id_firm))
        con.transaction.commit()
    service.disconnect_fdb(con)


def main():
    # глобальные файлы, влкючение логирования
    global inifile, sqlfile, path, log_file, logger
    inifile, sqlfile, path, log_file, logger = service.get_name_file(__file__)
    data = get_file()
    clear_bd(inifile, path)
    insert_sprav(inifile, path, data)



if __name__ == '__main__':
    main()
