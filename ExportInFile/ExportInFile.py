""" Сохранение из АУ в excel. Скрипты select складываем в папку script. Запускаем утилиту, выбираем скрипт,
нажимаем "Экспорт". Результат сохраняется в папке директроии проекта. """
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
        # self.inifile = service.get_name_file(__file__)[0]
        self.geometry("460x240")
        self.title("Выгрузка данных в Эксель")
        """Показать данные по департнику"""
        # self.con = service.connect_fdb(self.inifile)
        # self.cbDepart = customtkinter.CTkComboBox(master=self,
        #                 values=[x for t in self.con.execute(script.SQL["get_depart"]).fetchall() for x in t] ,width=320)
        # service.disconnect_fdb(self.con)
        # self.cbDepart.grid(row=0, column=0, padx=20, pady=10)
        # self.path = f"{service.get_name_file(__file__)[2]}\\script\\"
        """чмтаем ini """
        try:
            self.config = c.ConfigParser()
            self.config.read(inifile)
            self.ini_checknamerow = self.config['visible']['cheknamerow']
            self.ini_script = self.config['visible']['ini_script']
        except:
            pass
        self.path = f"{path}\\script\\"
        self.list_script = os.listdir(path=self.path)
        # self.list_script.append("Выгрузка наличия")
        self.cbexport = customtkinter.CTkComboBox(master=self, values=self.list_script, width=430)
        self.cbexport.grid(row=1, column=0, padx=20, pady=10, )
        self.checknamerow = customtkinter.CTkCheckBox(master=self, onvalue=True, offvalue=False,
                                                      text="Выгружать названия колонок")
        self.checknamerow.grid(row=2, column=0, padx=20, pady=10)
        self.btnexpornalic = customtkinter.CTkButton(master=self, text="Экспорт в xlsx", command=self.export)
        self.btnexpornalic.grid(row=3, column=0, padx=20, pady=10)
        self.check_connect_fdb = service.get_setting_bd(inifile)[0]
        self.label_one = customtkinter.CTkLabel(self, text=f"БД:{self.check_connect_fdb}")
        self.label_one.grid(row=4, column=0, padx=20, pady=10)



    def on_close(self):
        print("Окно закрываем")

    def export(self):
        if self.cbexport.get() == "Выгрузка наличия":
            self.export_nalic()
        else:
            self.export_script()

    def export_script(self):
        self.con = service.connect_fdb(inifile, path)
        # self.id_depart = self.cbDepart.get()
        # x = self.id_depart.find("[")+1
        # y = self.id_depart.find("]")
        with open(f"{self.path}{self.cbexport.get()}", 'r') as file:
            text_file = file.read()
        self.cur_dict = self.con.execute(text_file)
        self.save_excel(self.cur_dict)
        service.disconnect_fdb(self.con)

    def save_excel(self, cur_dict):
        titel = []
        for line in self.cur_dict.description:
            titel.append(line[0])
        excel = pd.DataFrame.from_records(cur_dict.fetchall(), columns=titel)
        excel.to_excel(f"{self.cbexport.get()}.xlsx", index=False, header=self.checknamerow.get())

    def export_nalic(self):
        self.con = service.connect_fdb(inifile)
        self.id_depart = self.cbDepart.get()
        x = self.id_depart.find("[") + 1
        y = self.id_depart.find("]")
        self.cur_dict = self.con.execute(script.SQL["get_nalic_evotor"] % int(self.id_depart[x:y]))
        self.save_excel(self.cur_dict)
        service.disconnect_fdb(self.con)


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
