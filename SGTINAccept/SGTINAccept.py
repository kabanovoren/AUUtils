"""Утилита, для создание схем акцептирования по 601 уведомлениям и далее документам списания и не только"""
import time

import customtkinter
import datetime
import os
from customtkinter import CTkButton, CTkTextbox, CTkLabel, CTk, CTkComboBox, CTkFrame, CTkEntry, CTkFont, CTkCheckBox
import tkcalendar
import Service.fdb_service as service
import script
import pandas as pd
import configparser as c
import re
import fdb
import xsd2xml
from lxml import etree
import xmlschema
import json
from xml.etree.ElementTree import ElementTree
from xmlschema.validators import XsdAtomicRestriction, XsdElement
from pprint import pprint
from threading import Thread


class MainForm(CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("900x600")
        self.title("Выгрузка данных в Эксель")
        """Показать данные по департнику"""
        """чмтаем ini """
        try:
            self.config = c.ConfigParser()
            self.config.read(inifile)
        except:
            pass
        self.path_out = f"{path}\\out\\"
        self.path_xsd = f"{path}\\xsd\\"
        self.TopFrame = CTkFrame(master=self, width=800)
        self.TopFrame.grid(row=0, column=0, )

        self.label_text = CTkLabel(master=self.TopFrame, text="Список SGTIN для проверки и формирование схем")
        self.label_text.grid(row=0, column=0, padx=10, pady=10)
        fonttext = CTkFont(family='Courier New')
        self.memoSGTIN = CTkTextbox(master=self.TopFrame, width=420, font=fonttext)
        self.memoSGTIN.grid(row=1, column=0, padx=10, pady=0)

        self.FrameAU = CTkFrame(master=self.TopFrame)
        self.FrameAU.grid(row=1, column=1, padx=0, pady=0)
        self.path_script = f"{path}\\script\\"
        self.list_script = os.listdir(path=self.path_script)
        self.sql_var = customtkinter.StringVar(value="_")
        self.cbsql = customtkinter.CTkComboBox(master=self.FrameAU, values=self.list_script, width=200,
                                               variable=self.sql_var, command=self.get_sql_params)
        self.cbsql.grid(row=0, column=0, padx=10, pady=10, )
        self.btnexpornalic = customtkinter.CTkButton(master=self.FrameAU, text="Заполнить SGTIN из БД",
                                                     command=self.get_sgtin_from_bd)
        self.btnexpornalic.grid(row=0, column=1, padx=10, pady=10)
        self.Obj = dict(run=False)
        self.set_check = CTkButton(master=self.FrameAU, text="На проверку",
                                   command=lambda: Thread(target=self.set_check_sgtin).start())
        self.set_check.grid(row=1, column=1, padx=10, pady=10)
        self.set_check = CTkButton(master=self.FrameAU, text="Отменить проверку", command=self.cansel_prov)
        self.set_check.grid(row=1, column=0, padx=10, pady=10)
        self.set_check = CTkButton(master=self.FrameAU, text="Заполнить цены", command=self.set_cost_sgtin)
        self.set_check.grid(row=2, column=1, padx=10, pady=10)

        self.check_connect_fdb = service.get_setting_bd(inifile)[0]
        self.label_one = CTkLabel(master=self.FrameAU, text=f"БД:{self.check_connect_fdb}")
        self.label_one.grid(row=4, column=0, padx=10, pady=10)

        self.check_xsd_occus = CTkCheckBox(master=self.FrameAU, text=f"Необязательные теги", onvalue=False,
                                           offvalue=True)
        self.check_xsd_occus.grid(row=4, column=1, padx=10, pady=10)
        self.check_one_sgtin_in_xml = CTkCheckBox(master=self.FrameAU, text=f"Формировать 1 SGTIN/SSCC в схеме", onvalue=True,
                                           offvalue=False)
        self.check_one_sgtin_in_xml.grid(row=5, column=0, padx=10, pady=10)

        # self.FrameXSD = CTkFrame(master=self)
        # self.FrameXSD.grid(row=3, column=0, padx=0, pady=0)
        self.list_xsd = os.listdir(path=self.path_xsd)
        self.xsd_var = customtkinter.StringVar(value="_")
        self.xsd = CTkComboBox(master=self.FrameAU, values=self.list_xsd, width=200, command=self.get_xsd,
                               variable=self.xsd_var)
        self.xsd.grid(row=3, column=0, padx=10, pady=10, )
        self.set_check = CTkButton(master=self.FrameAU, text="Сформировать схему", command=self.create_xml)
        self.set_check.grid(row=3, column=1, padx=10, pady=10)

        self.FrameElement = CTkFrame(master=self, width=884)
        self.FrameElement.grid(row=4, column=0)

    def cansel_prov(self):
        self.Obj = dict(run=False)

    def get_sql_params(self, choice):
        self.FrameElement.destroy()
        self.FrameElement = CTkFrame(master=self, width=884)
        self.FrameElement.grid(row=4, column=0)
        text_file = self.get_text_sql(choice)
        self.element_list = []
        self.con = service.connect_fdb(inifile, path)
        self.depart_list = [x for t in self.con.execute(script.SQL["get_depart"]).fetchall() for x in t]
        self.client_list = [x for t in self.con.execute(script.SQL["get_client"]).fetchall() for x in t]
        self.oper_list = [x for t in self.con.execute(script.SQL["get_oper"]).fetchall() for x in t]
        service.disconnect_fdb(self.con)
        n = 0
        list_text = text_file.split('\n')
        self.sql_text = ''
        for line in list_text:
            if line.find(":ID_DEPART") != -1:
                self.element_list.append([CTkLabel(master=self.FrameElement, text="Подразделение:"),
                                          CTkComboBox(master=self.FrameElement, values=self.depart_list, width=150
                                                      )])
            if line.find(":ID_CLIENT") != -1:
                self.element_list.append([CTkLabel(master=self.FrameElement, text="Поставщик/Получатель:"),
                                          CTkComboBox(master=self.FrameElement, values=self.client_list, width=150
                                                      )])
            if line.find(":ID_OPER") != -1:
                self.element_list.append([CTkLabel(master=self.FrameElement, text="Тип операции:"),
                                          CTkComboBox(master=self.FrameElement, values=self.oper_list, width=150
                                                      )])
            if line.find(":DATE1") != -1:
                self.element_list.append([CTkLabel(master=self.FrameElement, text="Дата с:"),
                                          tkcalendar.DateEntry(master=self.FrameElement,
                                                               date_pattern='dd.MM.YYYY', width=20,
                                                               bad=2, font=CTkFont(family='Courier New'))])
            if line.find(":DATE2") != -1:
                self.element_list.append([CTkLabel(master=self.FrameElement, text="Дата по:"),
                                          tkcalendar.DateEntry(master=self.FrameElement,
                                                               date_pattern='dd.MM.YYYY', width=20,
                                                               bad=2, font=CTkFont(family='Courier New'))])
            line = line.replace(':ID_DEPART', '%s').replace(':ID_CLIENT', '%s').replace(':ID_OPER', '%s').replace(
                ':DATE1', "'%s'").replace(':DATE2', "'%s'")
            self.sql_text = f"{self.sql_text} {line} \n"
        for entry in self.element_list:
            entry[0].grid(row=n, column=0, padx=5, pady=5)
            entry[1].grid(row=n, column=1, padx=5, pady=5)
            n = n + 1

    def get_text_sql(self, choice):
        with open(f"{self.path_script}{choice}", 'r') as file:
            text_file = file.read()
        return text_file

    def get_sgtin_from_bd(self):
        params_sql = []
        for element in self.element_list:
            add_params = element[1].get()
            x = add_params.find("[") + 1
            y = add_params.find("]")
            if y != - 1:
                params_sql.append(int(add_params[x:y]))
            else:
                params_sql.append(add_params)
        self.con = service.connect_fdb(inifile, path)
        result_sql = self.con.execute(self.sql_text % tuple(params_sql)).fetchall()
        service.disconnect_fdb(self.con)
        self.memoSGTIN.delete("0.0", "end")
        n = 0
        for sgtin in result_sql:
            try:
                self.memoSGTIN.insert(f"0.{n}", f"{sgtin[0]}\n")
            except:
                self.memoSGTIN.insert(f"0.{n}", f"{sgtin[0]};{sgtin[1]};{sgtin[2]}\n")
            n = n + 1

    def get_sgtin_from_text(self):
        text = self.memoSGTIN.get("0.0", "end")
        sgtins = []
        sgtins_cost = text.split()
        for sgtin in sgtins_cost:
            sgtin = sgtin.split(';')
            if len(sgtin[0]) == 27:
                sgtins.append([sgtin[0], 'sgtin'])
            else:
                sgtin.append([sgtin[0], 'sscc'])
        return sgtins

    def set_cost_sgtin(self):
        sgtins = self.get_sgtin_from_text()
        self.con = service.connect_fdb(inifile, path)
        self.memoSGTIN.delete("0.0", "end")
        n = 0
        for sgtin in sgtins:
            gtin = sgtin[0][:14]
            cost_vat = self.con.execute(script.SQL["get_cost"] % (gtin)).fetchone()
            self.memoSGTIN.insert(f"0.{n}", f"{sgtin[0]};{float(cost_vat[0])};{float(cost_vat[1])}\n")
            n = n + 1
        service.disconnect_fdb(self.con)

    def get_xsd(self, choice):
        try:
            self.FrameElement.destroy()
            self.FrameElement = CTkFrame(master=self, width=884)
            self.FrameElement.grid(row=4, column=0)

            """Парсим xsd и создаем необходимые документы"""
            xsd = f'xsd/{choice}'
            self.document = os.path.splitext(choice)[0].split("-", )
            # document = f'xsd/701-accept.xsd'
            schema = xmlschema.XMLSchema(xsd)
            element_list = []
            for item in schema.types[self.document[1]].content:
                if self.check_xsd_occus.get():
                    if item.occurs[0] == 0:
                        break
                if item.type.name is not None:
                    element_list.append([item.name, item.type.name, item.type.base_type])
            # print(element_list)
            type_list = self.get_type_xsd()

            self.element_list = []
            n = 0
            for element in element_list:
                name_label = ''
                for item in type_list:

                    if item[0] == element[1]:
                        name_label = f"{item[1]}\n{element[0]}"
                        print(item)
                        if item[3] == 'xs:dateTime':
                            self.element_list.append([CTkLabel(master=self.FrameElement, text=name_label),
                                                      tkcalendar.DateEntry(master=self.FrameElement,
                                                                           date_pattern='YYYY-MM-dd', width=20,
                                                                           bad=2, font=CTkFont(family='Courier New'))])
                        if item[3] == 'xs:string':
                            self.element_list.append([CTkLabel(master=self.FrameElement, text=name_label),
                                                      CTkEntry(master=self.FrameElement,
                                                               )])
                        if item[3] == 'xs:decimal':
                            self.element_list.append([CTkLabel(master=self.FrameElement, text=name_label),
                                                      CTkComboBox(master=self.FrameElement, values=item[2]
                                                                  )])
                        break
            for entry in self.element_list:
                entry[0].grid(row=n, column=0, padx=5, pady=5)
                entry[1].grid(row=n, column=1, padx=5, pady=5)
                n = n + 1
        except Exception as ex:
            service.logs(ex)

    def get_params_xml(self):
        param_doc = {}
        for element in self.element_list:
            if type(element[1]) == type(self.xsd):
                param_doc.update({
                    element[0]._text.split('\n')[1]: int(element[1].get().replace('–', '-').split('-')[0].strip())
                })
            else:
                if element[0]._text.split('\n')[1] == 'operation_date':
                    param_doc.update({
                        element[0]._text.split('\n')[
                            1]: f"{element[1].get()}{datetime.datetime.now().isoformat(timespec='seconds')[10:]}+05:00"})
                else:
                    param_doc.update({
                        element[0]._text.split('\n')[1]: element[1].get()
                    })
        return param_doc


    def get_xsd_document(self, document):
        """Загрузка xml"""
        schema = xmlschema.XMLSchema(document)
        return schema

    def get_sgtin_sscc(self, schema):
        text = self.memoSGTIN.get("0.0", "end")
        sscc = []
        sgtins = []
        union_exist = False
        for item in schema.iter_components():
            if item.name == 'union':
                union_exist = True
        sgtins_list = text.split()
        if union_exist:
            for sgtin in sgtins_list:
                if sgtin.find(';') == -1:
                    return print('Не заполнены цены')
        for sgtin in sgtins_list:
            union = sgtin.split(';')
            if len(union[0]) == 27 or len(sgtin) == 27:
                if union_exist:
                    sgtins.append({"sgtin": union[0], "cost": union[1], "vat_value": union[2]})
                else:
                    sgtins.append(sgtin)
            else:
                if union_exist:
                    sgtins.append({"sscc": union[0], "cost": union[1], "vat_value": union[2]})
                else:
                    sgtins.append(sgtin)
        sgtins = {'order_details': {"union": sgtins}}
        return sgtins


    def save_xml(self, data, schema, name_file):
        xml = xmlschema.from_json(data, schema=schema, preserve_root=True)
        ElementTree(xml).write(f'out/{name_file}_{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}_{self.document[0]}.xml',
                               encoding="UTF-8", xml_declaration=True)

    def create_json(self, dict_document, sscc_sgtin, sscc):

        sscc_sgtin = {'order_details': {"sgtin": sscc_sgtin, "sscc": sscc}}
        dict_document.update(sscc_sgtin)

        dict_header = {self.document[1]: dict_document}
        data = {'@version': '1.38'}
        data.update(dict_header)
        data = json.dumps(data)
        return data
    def create_xml(self):
        """Создание xml"""
        schema = self.get_xsd_document(f"xsd/{self.xsd.get()}")
        dict_document = {'@action_id': int(self.document[0])}
        dict_document.update(self.get_params_xml())
        sscc_sgtin = self.get_sgtin_sscc(schema)
        schema = self.get_xsd_document('xsd/documents.xsd')
        if self.check_one_sgtin_in_xml.get():
            for sgtin in sscc_sgtin:
                data = self.create_json(dict_document, sgtin)
                self.save_xml(data, schema, sgtin)
        else:
            data = self.create_json(dict_document, sscc_sgtin)
            self.save_xml(data, schema, '')

    def create_xml2(self):
        text = self.memoSGTIN.get("0.0", "end")
        sgtins = []
        schema = xmlschema.XMLSchema(f"xsd/{self.xsd.get()}")
        # ищем union, если есть, указываем цены по SGTIN
        union_exist = False
        for item in schema.iter_components():
            if item.name == 'union':
                union_exist = True
        if union_exist == True:
            sgtins_list = text.split()
            for sgtin in sgtins_list:
                if sgtin.find(';') == -1:
                    return print('Не заполнены цены')
                union = sgtin.split(';')
                sgtins.append({"sgtin": union[0], "cost": union[1], "vat_value": union[2]})
            sgtins = {'order_details': {"union": sgtins}}
        else:
            sgtins = text.split()
            sgtins = {'order_details': {"sgtin": sgtins}}

        document = 'xsd/documents.xsd'
        schema = xmlschema.XMLSchema(document)
        dict_element = {'@action_id': int(self.document[0])}
        # dict_element.update(self.get_params_xml)
        for element in self.element_list:
            if type(element[1]) == type(self.xsd):
                dict_element.update({
                    element[0]._text.split('\n')[1]: int(element[1].get().replace('–', '-').split('-')[0].strip())
                })
            else:
                if element[0]._text.split('\n')[1] == 'operation_date':
                    dict_element.update({
                        element[0]._text.split('\n')[
                            1]: f"{element[1].get()}{datetime.datetime.now().isoformat(timespec='seconds')[10:]}+05:00"})
                else:
                    dict_element.update({
                        element[0]._text.split('\n')[1]: element[1].get()
                    })
        dict_element.update(sgtins)
        dict_header = {self.document[1]: dict_element}
        data = {'@version': '1.38'}
        data.update(dict_header)
        data = json.dumps(data)
        print(data)

        # print(data)
        xml = xmlschema.from_json(data, schema=schema, preserve_root=True)
        #
        ElementTree(xml).write(f'out/{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}_{self.document[0]}.xml',
                               encoding="UTF-8", xml_declaration=True)

    def update_label(self, label, frame, row, column, text):
        try:
            if type(label) != 'type':
                print(type(label))
        finally:
            label = customtkinter.CTkLabel(master=frame, text=text)
            label.grid(row=row, column=column, padx=10, pady=10)
            print(type(label))

    def set_check_sgtin(self):
        # self.update_label(customtkinter.CTkLabel, self.FrameAU, 2, 0, "Запуск проверки")
        self.label_count = customtkinter.CTkLabel(master=self.FrameAU, text=f"Запуск проверки")
        self.label_count.grid(row=2, column=0, padx=10, pady=10)
        self.con = service.connect_fdb(inifile, path)
        text = self.memoSGTIN.get("0.0", "end")
        self.list_text = text.split()
        self.list_SGTIN = []
        self.list_SGTIN_not_BD = []
        for line in self.list_text:
            """Проверяем SGTIN в текущей БД на нахождение в БД"""
            sgtin = self.con.execute(script.SQL["check_SGTIN"] % (line, f'%{line}%', line, line)).fetchone()
            if sgtin is None:
                self.list_SGTIN_not_BD.append([line])
            else:
                self.list_SGTIN.append(list(sgtin))
        # print(self.list_SGTIN)
        # обновляем списки для загрузки информации
        for sgtin in self.list_SGTIN:
            self.con.execute(script.SQL["ins_upd_sgtin"] % (sgtin[0]))
        for sgtin in self.list_SGTIN_not_BD:
            self.con.execute(script.SQL["ins_upd_sgtin"] % (sgtin[0]))
        self.con.execute(script.SQL["upd_mdlp_doc_14"])
        self.con.transaction.commit()

        i = 1
        self.Obj['run'] = not self.Obj['run']
        while i > 0 and self.Obj['run']:
            i = self.con.execute(script.SQL["get_sgtin_status"]).fetchone()
            i = i[0]
            time.sleep(60)
            self.label_count.destroy()
            self.label_count = customtkinter.CTkLabel(master=self.FrameAU, text=f"проверяем, осталось {i}")
            self.label_count.grid(row=2, column=0, padx=10, pady=10)
        # после того как получили всю информацию дополняем наши данные и сохраняем
        # if not self.Obj['run']:
        #     return service.disconnect_fdb(self.con)

        self.label_count.destroy()
        self.label_count = customtkinter.CTkLabel(master=self.FrameAU, text=f"Формирование файлов")
        self.label_count.grid(row=2, column=0, padx=10, pady=10)
        list_sgtin = []
        list_sgtin_not_BD = []
        for sgtin in self.list_SGTIN:
            info = self.con.execute(script.SQL["select_sgtin_info"] % (sgtin[0])).fetchone()
            list_sgtin.append(sgtin + list(info[1:]))
        for sgtin in self.list_SGTIN_not_BD:
            info = self.con.execute(script.SQL["select_sgtin_info"] % (sgtin[0])).fetchone()
            list_sgtin_not_BD.append((sgtin + list(info[1:])))

        service.disconnect_fdb(self.con)
        titel = ["SGTIN", "Идентификатор документа MDLP_DOC", "Дата документа",
                 "Остаток \n Не найден \n 0 - израсходован \n 1 - в наличии", "Список документов", "Чеки",
                 "Типы операции", "XML по документу", "XML по чеку", "Дата последней операции по АУ", "Статус",
                 "Место деятельности", "Дата последней операции", "Срок годности", "Серия",
                 "Дата загрузки информации"]
        titel_not_bd = ["SGTIN, не найден в БД", "Статус", "Место деятельности", "Дата последней операции",
                        "Срок годности", "Серия",
                        "Дата загрузки информации"]
        self.save_excel(list_sgtin, titel, 'SGTIN_on_BD')
        self.save_excel(list_sgtin_not_BD, titel_not_bd, 'SGTIN_not_BD')
        self.label_count.destroy()
        self.label_count = customtkinter.CTkLabel(master=self.FrameAU, text=f"Файлы сформированы")
        self.label_count.grid(row=2, column=0, padx=10, pady=10)

    def save_excel(self, cur_dict, titel, name_file):
        try:
            excel = pd.DataFrame.from_records(cur_dict, columns=titel)
            excel.to_excel(f"{name_file}.xlsx", index=False)
            service.logs(f"Файл сохранен {name_file}.xlsx")
        except Exception as ex:
            service.logs(f"Не смог соханить файл {name_file}.xlsx \n {ex}")

    def get_type_xsd(self):
        type_doc = f'xsd/base_types.xsd'
        shema_type = xmlschema.XMLSchema(type_doc)
        types = []
        for items in shema_type.iter_components(xsd_classes=XsdAtomicRestriction):
            description = str(items.annotation).split('\n')
            val_list = []
            for val in description[1:]:
                val_list.append(val.strip())
            types.append([items.name, description[0].strip(), val_list, items.sequence_type])

        return list(types)


def main():
    try:
        # глобальные файлы, влкючение логирования
        global inifile, sqlfile, path, log_file, logger
        inifile, sqlfile, path, log_file, logger = service.get_name_file(__file__)
        if not os.path.exists(f'{path}/out/'):
            os.mkdir(f'{path}/out/')
        if not os.path.exists(f'{path}/script/'):
            os.mkdir(f'{path}/script/')
        # запуск формы отображения
        app = MainForm()
        app.mainloop()
    except Exception as ex:
        service.logs(ex)


def main3():
    print(f"{datetime.datetime.now().isoformat(timespec='seconds')[10:]}+05:00")

    # T09:04:01+05:00

    print(datetime.timezone(datetime.timedelta(hours=5)))
    offset = datetime.timedelta(hours=3)
    tz = datetime.timezone(offset, name='МСК')
    dt = datetime.datetime.now()
    print(tz.utcoffset(dt))
    document = 'xsd/documents.xsd'
    # schema = xmlschema.XMLSchema(document)
    # print(schema.to_dict('415_02.xml'))

    # for iter in schema.iter_components():
    #
    #     try:
    #         print(iter)
    #         print(iter.occurs[0])
    #     except:
    #         pass
    #     if iter.name == 'union':
    #         print(iter)


if __name__ == '__main__':
    main()
