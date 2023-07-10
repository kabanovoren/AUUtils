import os
import Service.fdb_service
import Service.fdb_service as d
import configparser as c
import subprocess



def all_delete():
    pass


def not_nalic():
    pass



def main():
    newbd()


def newbd(delete_all=True, ):
    con = d.connect_fdb()

def newbd2():
    # входящие переменные (пока тут, может перенесу)
    delete_all = int(input(
        'Удалить все данные? (0 - удаляем движение, наличие переносится в документ, 1 - удалить все наличие и движение)'))
    d.logs('========================Старт выполнения========================')
    config = c.ConfigParser()
    config.read('newBD.ini')
    path = config['BD']['path']
    print(path)
    path_new = config['BD']['path_new']
    print(path_new)
    # список файлов в папке /BD с исполняемым файлом
    bd_file = os.listdir(path=path)

    for bd in bd_file:
        name_file, file_ext = os.path.splitext(bd)
        path_bd = path + bd
        if file_ext != '.FDB':
            continue
        d.logs(path + bd)
        if delete_all == True:
            # удаляем все данные
            con = d.connect_fdb(path_bd)
            for sql in SQL.delete:
                d.logs('Чистка таблицы ' + sql)
                d.delete(con, SQL.delete[sql], 0)
            con.execute(SQL.SQL['del_err_tovar'])
            con.transaction.commit()
            d.close_connect_fdb(con)

        if delete_all != True:
            # переносим все наличие в один документ (несколько), остальное удаляем
            con = d.connect_fdb(path_bd)
            d.logs('Переносим наличие по документам')
            con.execute(SQL.SQL['one_doc'])
            id_doc = str()
            id_doc_list = []
            for doc in con:
                id_doc_list.append(doc)
                id_doc += str(*doc) + ','
            # список документов в виде стоки, которые нужно пропустить
            id_doc = id_doc.rstrip(id_doc[-1])
            d.logs('Создали документы:' + id_doc)

            for sql in SQL.delete:
                d.logs('Чистка таблицы ' + sql)
                d.delete(con, SQL.delete[sql], id_doc)
            # Чистка таблицы TOVAR от плохих ЕАН13
            con.execute(SQL.SQL['del_err_tovar'])

            # Ставим документ на учет, после удаления всех данных
            for id_doc_n in id_doc_list:
                con.execute(SQL.SQL['doc_reg'] % id_doc_n)
            con.transaction.commit()
            d.close_connect_fdb(con)

        # делаем бекап/рестор БД
        #    subprocess.Popen(['gstat', '-r', path_bd, '-user', 'SYSDBA', '-password', 'masterkey', '>>stat.txt'])
        subprocess.Popen(['gfix', '-mend', path_bd, '-user', 'SYSDBA', '-password', 'masterkey'])
        d.logs('Делаю бекап БД')
        subprocess.check_call(
            ['gbak', '-b', '-v', '-ig', '-g', path_bd, 'arhiv.fbk', '-user', 'SYSDBA', '-password', 'masterkey'])
        d.logs('Бекап БД выполнен')
        path_bd = path_new + bd
        d.logs('Делаю восстановление БД')
        subprocess.check_call(
            ['gbak', '-c', '-v', '-rep', 'arhiv.fbk', path_bd, '-user', 'SYSDBA', '-password', 'masterkey'])
        d.logs('Восстановление БД выполнено')
        os.remove('arhiv.fbk')

        # восстанавливаем генераторов вручную
        con = d.connect_fdb(path_bd)
        for table, id, name_gen in SQL.generator:
            d.logs('Обновление генератора ' + name_gen)
            d.gen(con, table, id, name_gen)
        d.close_connect_fdb(con)

        # восстановление генераторов автоматом
        con = d.connect_fdb(path_bd)
        gen_add = []
        con.execute(SQL.SQL['aut_gen'])
        for table, id, name_gen in con:
            gen_add.append([table, id, name_gen])
        for table, id, name_gen in gen_add:
            d.logs('Обновление генератора ' + name_gen)
            d.gen(con, table, id, name_gen)
        d.close_connect_fdb(con)

    d.logs('========================Финиш===================================')
    os.system('pause')


if __name__ == '__main__':
    main()
