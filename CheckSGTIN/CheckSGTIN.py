import os
import customtkinter
import tkinter
import Service.fdb_service as service
import script
import pandas as pd
import configparser as c
import fdb

class MainForm(customtkinter.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("300x460")
        self.title("Выгрузка данных в Эксель")
        """Показать данные по департнику"""
        """чмтаем ini """
        try:
            self.config = c.ConfigParser()
            self.config.read(inifile)
        except:
            pass
        self.path = f"{path}\\script\\"
        self.list_script = os.listdir(path=self.path)
        self.label_text = customtkinter.CTkLabel(master=self, text="Список SGTIN для проверки")
        self.label_text.grid(row=0, column=0, padx=20, pady=10)
        self.memoSGTIN = customtkinter.CTkTextbox(master=self, width=260)
        self.memoSGTIN.grid(row=1, column=0, padx=20, pady=0)
        self.set_check = customtkinter.CTkButton(master=self, text="На проверку", command=self.set_check_sgtin)
        self.set_check.grid(row=2, column=0, padx=20, pady=10)
        self.btnexpornalic = customtkinter.CTkButton(master=self, text="Экспорт в xlsx", command=self.export)
        self.btnexpornalic.grid(row=3, column=0, padx=20, pady=10)
        self.check_connect_fdb = service.get_setting_bd(inifile)[0]
        self.label_one = customtkinter.CTkLabel(self, text=f"БД:{self.check_connect_fdb}")
        self.label_one.grid(row=4, column=0, padx=20, pady=10)

    def set_check_sgtin(self):
        pass

    def export(self):
        pass

def main():
    # глобальные файлы, влкючение логирования
    global inifile, sqlfile, path, log_file, logger
    inifile, sqlfile, path, log_file, logger = service.get_name_file(__file__)
    if not os.path.exists(f'{path}/script/'):
        os.mkdir(f'{path}/script/')
    # запуск формы отображения
    app = MainForm()
    app.mainloop()


if __name__ == '__main__':
    main()