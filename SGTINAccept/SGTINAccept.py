"""Утилита, для создание схем акцептирования по 601 уведомлениям и далее документам списания"""

import os
from customtkinter import CTkButton, CTkTextbox, CTkLabel, CTk
import tkinter
import Service.fdb_service as service
import script
import pandas as pd
import configparser as c
import fdb
import xsd2xml
import xmlschema
import json
from xml.etree.ElementTree import ElementTree
from pprint import pprint


class MainForm(CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("360x460")
        self.title("Выгрузка данных в Эксель")
        """Показать данные по департнику"""
        """чмтаем ini """
        try:
            self.config = c.ConfigParser()
            self.config.read(inifile)
        except:
            pass
        self.path = f"{path}\\out\\"
        self.list_script = os.listdir(path=self.path)
        self.label_text = CTkLabel(master=self, text="Список SGTIN для проверки и формирование схем")
        self.label_text.grid(row=0, column=0, padx=20, pady=10)
        self.memoSGTIN = CTkTextbox(master=self, width=260)
        self.memoSGTIN.grid(row=1, column=0, padx=20, pady=0)
        self.set_check = CTkButton(master=self, text="На проверку", command=self.set_check_sgtin)
        self.set_check.grid(row=2, column=0, padx=20, pady=10)
        # self.btnexpornalic = CTkButton(master=self, text="Экспорт в xlsx", command=self.export)
        # self.btnexpornalic.grid(row=3, column=0, padx=20, pady=10)
        self.check_connect_fdb = service.get_setting_bd(inifile)[0]
        self.label_one = CTkLabel(self, text=f"БД:{self.check_connect_fdb}")
        self.label_one.grid(row=4, column=0, padx=20, pady=10)

    def set_check_sgtin(self):
        self.con = service.connect_fdb(inifile, path)
        text = self.memoSGTIN.get("0.0", "end")
        self.list_text = text.split()
        self.list_SGTIN_doc = []
        for line in self.list_text:
            """Проверяем SGTIN в текущей БД на нахождение в БД"""
            id_doc = self.con.execute(script.SQL["check_601"] % f"%{str(line)}%").fetchone()
            # service.logs(f"SGTIN {str(line)} найден в документе MDLP_DOC.PRIM = {id_doc[0]}")
            if id_doc is None:
                self.list_SGTIN_doc.append(['None', 'None', str(line)])
            else:
                self.list_SGTIN_doc.append([id_doc[0], id_doc[1], str(line)])

        """Проверям движение SGTIN возращаем None - не найден в движении 0 - израсходовали 1 - в наличии"""
        self.list_SGTIN = []
        for sgtin in self.list_SGTIN_doc:
            id_sgtin = self.con.execute(script.SQL["check_SGTIN_doc"] % sgtin[1]).fetchone()
            if id_sgtin is None:
                self.list_SGTIN.append([sgtin[2], sgtin[0], sgtin[1], 'None', 'None'])
            else:
                self.list_SGTIN.append([sgtin[2], sgtin[1], id_sgtin[0], id_sgtin[1]])
            # service.logs(
            #     f"SGTIN {sgtin[1]} найден в документе MDLP_DOC.PRIM = {sgtin[0]}, остаток в БД {id_sgtin[0]}, срок годности: {id_sgtin[1]}")
        service.logs(self.list_SGTIN)
        # self.con.execute(script.SQL["upd_mdlp_doc_14"])
        self.con.transaction.commit()
        service.disconnect_fdb(self.con)
        self.save_excel(self.list_SGTIN)


    def save_excel(self, cur_dict):
        # body = []
        titel = ["SGTIN", "Идентификатор документа MDLP_DOC", "Дата документа", "Остаток \n None - не найден \n 0 - израсходован \n 1 - в наличии", "Срок годности"]
        # for list in cur_dict:
        #     for line in list:
        #         body.append(line)
        try:
            excel = pd.DataFrame.from_records(cur_dict, columns=titel)
            excel.to_excel(f"SGTINАccept.xlsx", index=False)
            service.logs("Файл сохранен SGTINАccept.xlsx")
        except Exception as ex:
            service.logs(f"Не смог соханить файл SGTINАccept.xlsx \n {ex}")


def main():
    try:
        # глобальные файлы, влкючение логирования
        global inifile, sqlfile, path, log_file, logger
        inifile, sqlfile, path, log_file, logger = service.get_name_file(__file__)
        if not os.path.exists(f'{path}/out/'):
            os.mkdir(f'{path}/out/')
        # запуск формы отображения
        # app = MainForm()
        # app.mainloop()
    except Exception as ex:
        service.logs(ex)

    my_xsd = '701-accept.xsd'

    schema = xmlschema.XMLSchema(my_xsd)
    # pprint(schema.to_dict('701_01.xml'))
    print(schema.is_valid('701_01.xml'))
    # data = json.dumps({'accept': {'subject_id': '12345678912345'}})
    #
    # xml = xmlschema.from_json(data, schema=schema, preserve_root=True)
    #
    # ElementTree(xml).write('my_xml.xml')


if __name__ == '__main__':
    main()
