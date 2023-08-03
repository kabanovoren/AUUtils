"""Утилита, для создание схем акцептирования по 601 уведомлениям и далее документам списания"""
import customtkinter
import datetime
import os
from customtkinter import CTkButton, CTkTextbox, CTkLabel, CTk, CTkComboBox, CTkFrame, CTkEntry
import tkinter, tkcalendar
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


class MainForm(CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("884x600")
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
        self.label_text.grid(row=0, column=0, padx=20, pady=10)
        self.memoSGTIN = CTkTextbox(master=self.TopFrame, width=420)
        self.memoSGTIN.grid(row=1, column=0, padx=20, pady=0)

        self.FrameAU = CTkFrame(master=self.TopFrame)
        self.FrameAU.grid(row=1, column=1, padx=0, pady=0)
        self.set_check = CTkButton(master=self.FrameAU, text="На проверку", command=self.set_check_sgtin)
        self.set_check.grid(row=0, column=1, padx=20, pady=10)
        self.check_connect_fdb = service.get_setting_bd(inifile)[0]
        self.label_one = CTkLabel(master=self.FrameAU, text=f"БД:{self.check_connect_fdb}")
        self.label_one.grid(row=0, column=0, padx=20, pady=10)

        # self.FrameXSD = CTkFrame(master=self)
        # self.FrameXSD.grid(row=3, column=0, padx=0, pady=0)
        self.list_xsd = os.listdir(path=self.path_xsd)
        self.xsd_var = customtkinter.StringVar(value="_")
        self.xsd = CTkComboBox(master=self.FrameAU, values=self.list_xsd, width=200, command=self.get_xsd,
                               variable=self.xsd_var)
        self.xsd.grid(row=1, column=0, padx=20, pady=10, )
        self.set_check = CTkButton(master=self.FrameAU, text="Сформировать схему", command=self.create_xml)
        self.set_check.grid(row=1, column=1, padx=20, pady=10)

        # self.Frame_component_XSD = CTkFrame(master=self)
        # self.Frame_component_XSD.grid(row=4, column=0, padx=0, pady=0)

        # self.label_fcx = CTkLabel(master=self.Frame_component_XSD, text=f"МД:")
        # self.label_fcx.grid(row=0, column=0, padx=20, pady=10)
        # self.MD = CTkEntry(master=self.Frame_component_XSD, width=210)
        # self.MD.grid(row=0, column=1, padx=5, pady=10)
        # self.label_fcx_to = CTkLabel(master=self.Frame_component_XSD, text=f"МД получателя:")
        # self.label_fcx_to.grid(row=1, column=0, padx=20, pady=10)
        # self.MD_to = CTkEntry(master=self.Frame_component_XSD, width=210)
        # self.MD_to.grid(row=1, column=1, padx=5, pady=10)
        # self.label_fcx_date = CTkLabel(master=self.Frame_component_XSD, text=f"Дата документа:")
        # self.label_fcx_date.grid(row=2, column=0, padx=20, pady=10)
        # self.fcx_date = tkcalendar.DateEntry(master=self.Frame_component_XSD, date_pattern='YYYY-MM-dd', width=20,
        #                                      bad=2)
        # self.fcx_date.grid(row=2, column=1, padx=5, pady=10)

        self.FrameElement = CTkFrame(master=self, width=884)
        self.FrameElement.grid(row=4, column=0)

        # self.btnexpornalic = CTkButton(master=self, text="Экспорт в xlsx", command=self.export)
        # self.btnexpornalic.grid(row=3, column=0, padx=20, pady=10)

    def get_xsd(self, choice):
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
            if item.type.name is not None:
                element_list.append([item.name, item.type.name, item.type.base_type])
        print(element_list)
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
                                                                       bad=2)])
                    if item[3] == 'xs:string':
                        self.element_list.append([CTkLabel(master=self.FrameElement, text=name_label),
                                                  CTkEntry(master=self.FrameElement,
                                                           )])
                    if item[3] == 'xs:decimal':
                        self.element_list.append([CTkLabel(master=self.FrameElement, text=name_label),
                                                  CTkComboBox(master=self.FrameElement, values=item[2]
                                                              )])
                    break
            # self.element_list.append([CTkLabel(master=self.FrameElement, text=name_label)])
        for entry in self.element_list:
            entry[0].grid(row=n, column=0, padx=5, pady=5)
            entry[1].grid(row=n, column=1, padx=5, pady=5)
            # entry[2].grid(row=self.n, column=2, padx=5, pady=5)
            n = n + 1

        # for item in schema.iter_components():
        #     print(item)

        # namespaces = {'': 'http://example.com/ns/collection'}
        # schema.find('collection/object', namespaces)
        # pprint(schema.findall('collection/object/*', namespaces))
        # for xsd_comp in schema.iter_components():
        #     if type(xsd_comp) is xmlschema.validators.elements.XsdElement:
        #         # print(xsd_comp.name)
        #
        #         clas = schema.find('*/{http://www.w3.org/2001/XMLSchema}subject_id')
        #         print(clas)

        # pprint(schema.elements["documents"].iter_components())

    def create_xml(self):
        text = self.memoSGTIN.get("0.0", "end")
        sgtins = text.split()
        document = 'xsd/documents.xsd'
        schema = xmlschema.XMLSchema(document)

        dict_element = {'@action_id': int(self.document[0])}
        for element in self.element_list:
            if type(element[1]) == type(self.xsd):
                dict_element.update({
                    element[0]._text.split('\n')[1]: int(element[1].get().replace('–', '-').split('-')[0].strip())
                })
            else:
                if element[0]._text.split('\n')[1] == 'operation_date':
                    dict_element.update({
                        element[0]._text.split('\n')[1]: f"{element[1].get()}T09:04:01+05:00"})
                else:
                    dict_element.update({
                        element[0]._text.split('\n')[1]: element[1].get()
                    })
        # print(dict_element)
        dict_element.update({'order_details': {'sgtin': sgtins}})
        dict_header = {self.document[1]: dict_element}
        data = {'@version': '1.38'}
        data.update(dict_header)
        data = json.dumps(data)
        print(data)

        # print(data)
        xml = xmlschema.from_json(data, schema=schema, preserve_root=True)
        #
        ElementTree(xml).write(f'out/{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}_{self.document[0]}.xml')

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
        titel = ["SGTIN", "Идентификатор документа MDLP_DOC", "Дата документа",
                 "Остаток \n None - не найден \n 0 - израсходован \n 1 - в наличии", "Срок годности"]
        # for list in cur_dict:
        #     for line in list:
        #         body.append(line)
        try:
            excel = pd.DataFrame.from_records(cur_dict, columns=titel)
            excel.to_excel(f"SGTINАccept.xlsx", index=False)
            service.logs("Файл сохранен SGTINАccept.xlsx")
        except Exception as ex:
            service.logs(f"Не смог соханить файл SGTINАccept.xlsx \n {ex}")

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
        # запуск формы отображения
        app = MainForm()
        app.mainloop()
    except Exception as ex:
        service.logs(ex)


def main3():
    document = 'xsd/documents.xsd'
    schema = xmlschema.XMLSchema(document)
    print(schema.is_valid('252_01.xml'))
    print(schema.to_dict('252_01.xml'))


if __name__ == '__main__':
    main()
