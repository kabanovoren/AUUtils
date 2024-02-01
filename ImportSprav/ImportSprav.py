"""Импорт справочника для Илизарова"""
import Service.Database as d
import script
import csv


def get_file():
    data = []
    with open('XLS/sprav.csv', 'r', encoding='cp866') as file:
        reader = csv.reader(file, delimiter=';')
        for row in reader:
            data.append(row)
    return data


def clear_bd():
    con = d.Database()
    con.execute(script.SQL["delete_tovar"])
    d.log("Удаление данных таблицы TOVAR выполнено")
    con.execute(script.SQL["update_firm"])
    con.execute(script.SQL["delete_firm"])
    d.log("Удаление данных таблицы FIRM выполнено")
    con.execute(script.SQL["delete_prep_vat"])
    con.execute(script.SQL["delete_group_name_link"])
    con.execute(script.SQL["delete_prep"])
    d.log("Удаление данных таблицы PREP выполнено")
    con.execute(script.SQL["delete_country"])
    d.log("Удаление данных таблицы COUNTRY выполнено")
    con.execute(script.SQL["delete_farmgroup"])
    d.log("Удаление данных таблицы FARMGROUP выполнено")
    con.transaction.commit()
    con.disconnect()



def insert_sprav(sprav):
    con = d.Database()
    for row in sprav[1:]:
        if row[2] == 'NULL' or row[2] == '':
            id_farmgroup = 0
        else:
            id_farmgroup = con.execute(script.SQL["farmgroup"] % row[2]).fetchone()[0]

        id_firm = con.execute(script.SQL["firm"] % (row[5].replace("'", "''"), 0, 0)).fetchone()[0]

        id_prep = con.execute(script.SQL["prep"] % (row[4].replace("'", "''"), 0, id_farmgroup, '')).fetchone()[0]
        con.execute(script.SQL["tovar"] % ('0000000000000', id_prep, id_firm))
        con.transaction.commit()
    con.disconnect()

def main():
    clear_bd()
    data = get_file()
    insert_sprav(data)



if __name__ == '__main__':
    main()
