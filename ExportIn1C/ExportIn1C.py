"""Утилита для проверки и выгрузки первичных данных в 1С"""
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
