"""Утилита, для преобразования файла АНСА для загрузки в АУ"""
import time
import pandas as pd
import customtkinter
import datetime
import os
from customtkinter import CTkButton, CTkTextbox, CTkLabel, CTk, CTkComboBox, CTkFrame, CTkEntry, CTkFont, CTkCheckBox
import tkcalendar
import Service.fdb_service as service
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
        self.geometry("380x320")
        self.title("Преобразование файлов в АУ из АСНА")
        """Показать данные по департнику"""
        """чмтаем ini """
        try:
            self.config = c.ConfigParser()
            self.config.read(inifile)
        except:
            pass
        self.path_out = f"{path}\\out\\"
        self.path_in = f"{path}\\in\\"

        self.FrameAU = CTkFrame(master=self.master)
        self.FrameAU.grid(row=1, column=1, padx=0, pady=0)

        self.set_check = CTkButton(master=self.FrameAU, text="Сформировать файлы", command=self.create_file)
        self.set_check.grid(row=2, column=1, padx=10, pady=10)

        self.check_connect_fdb = service.get_setting_bd(inifile)[0]
        self.label_one = CTkLabel(master=self.FrameAU, text=f"БД:{self.check_connect_fdb}")
        self.label_one.grid(row=4, column=0, padx=10, pady=10)


    def create_file(self):
        file = f"{self.path_in}МА 3кв 2023.xls"
        xls = pd.ExcelFile(file)
        df = xls.parse('TDSheet')
        kod = df['Unnamed: 0'].tolist()[5:]
        name_prep = df['Unnamed: 2'].tolist()[5:]
        name_firm = df['Unnamed: 5'].tolist()[5:]
        mark_assort = df['Unnamed: 6'].tolist()[5:]
        ustm = df['Unnamed: 7'].tolist()[5:]
        base_usl = df['Unnamed: 8'].tolist()[5:]
        ind_usl = df['Unnamed: 9'].tolist()[5:]
        kom_vvod = df['Unnamed: 10'].tolist()[5:]
        bezdef_nalic = df['Unnamed: 11'].tolist()[5:]
        vikladka = df['Unnamed: 12'].tolist()[5:]
        kat_bezdef_1 = df['Unnamed: 13'].tolist()[5:]
        kat_bezdef_2 = df['Unnamed: 14'].tolist()[5:]
        kat_bezdef_3 = df['Unnamed: 15'].tolist()[5:]
        kat_bezdef_4 = df['Unnamed: 16'].tolist()[5:]
        kat_bezdef_5 = df['Unnamed: 17'].tolist()[5:]
        kat_vikladka_1 = df['Unnamed: 18'].tolist()[5:]
        kat_vikladka_2 = df['Unnamed: 19'].tolist()[5:]
        kat_vikladka_3 = df['Unnamed: 20'].tolist()[5:]
        kat_vikladka_4 = df['Unnamed: 21'].tolist()[5:]
        kat_vikladka_5 = df['Unnamed: 22'].tolist()[5:]

        data_list = list(zip(kod, name_prep, name_firm, mark_assort, ustm, base_usl, ind_usl, kom_vvod, bezdef_nalic,
                             vikladka, kat_bezdef_1, kat_bezdef_2, kat_bezdef_3, kat_bezdef_4, kat_bezdef_5,
                             kat_vikladka_1, kat_vikladka_2, kat_vikladka_3, kat_vikladka_4, kat_vikladka_5))

        file = f"{self.path_in}ШК (3).xlsx"
        xls = pd.ExcelFile(file)
        df = xls.parse('Лист1')
        kod_ean = df['Номенклатура.Код ННТ'].tolist()
        name_prep_ean = df['Номенклатура'].tolist()
        ean = df['Штрихкод'].tolist()

        ean_list = list(zip(kod_ean, name_prep_ean, ean))

        # col = ['kod', 'name_prep', 'name_firm']
        # data_list = dict(zip(col, [kod, name_prep, name_firm]))

        data_result = []
        for line in data_list:
            resul_line = []
            for ean_line in ean_list:
                if line[0] == ean_line[0]:
                    # print(line)
                    # print(ean_line)
                    resul_line = list(line) + list(ean_line)
                    data_result.append(resul_line)

        with open(f"{self.path_out}ustm_yes.txt", 'w') as file:
            for line in data_result:
                if line[4] == 'Да':
                    file.write(f"{line[22]};4;0;;\n")

        with open(f"{self.path_out}ustm_no.txt", 'w') as file:
            for line in data_result:
                if line[4] == '-':
                    file.write(f"{line[22]};4;0;;\n")

        print(data_result)
        pass





def main():
    try:
        # глобальные файлы, влкючение логирования
        global inifile, sqlfile, path, log_file, logger
        inifile, sqlfile, path, log_file, logger = service.get_name_file(__file__)
        if not os.path.exists(f'{path}/out/'):
            os.mkdir(f'{path}/out/')
        if not os.path.exists(f'{path}/in/'):
            os.mkdir(f'{path}/in/')
        # запуск формы отображения
        app = MainForm()
        app.mainloop()
    except Exception as ex:
        service.logs(ex)



if __name__ == '__main__':
    main()
