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
        self.con = service.connect_fdb(inifile, path)
        text = self.memoSGTIN.get("0.0", "end")
        self.list_text = text.split()
        for line in self.list_text:
            self.con.execute(script.SQL["ins_upd_sgtin"] % str(line))
        self.con.execute(script.SQL["upd_mdlp_doc_14"])
        self.con.transaction.commit()
        service.disconnect_fdb(self.con)

    def export(self):
        text = self.memoSGTIN.get("0.0", "end")
        self.list_text = text.split()
        select_sgtin_list = []
        self.con = service.connect_fdb(inifile, path)
        for line in self.list_text:
            select_sgtin = self.con.execute(script.SQL["select_sgtin"] % str(line)).fetchall()
            select_sgtin_list.append(select_sgtin)
        service.disconnect_fdb(self.con)
        self.save_excel(select_sgtin_list)


    def save_excel(self, cur_dict):
        body = []
        titel = ["SGTIN", "Статус", "Место деятельности", "Дата последней операции", "Срок годности", "Серия", "Дата загрузки информации"]
        service.logs(f"Количество записей:{len(cur_dict)}")
        for list in cur_dict:
            for line in list:
                service.logs(line)
                body.append(line)
        try:
            excel = pd.DataFrame.from_records(body, columns=titel)
            excel.to_excel(f"Check_SGTIN.xlsx", index=False)
            service.logs("Файл сохранен Check_SGTIN.xlsx")
        except:
            service.logs("Не смог соханить файл Check_SGTIN.xlsx")

def main():
    try:
        # глобальные файлы, влкючение логирования
        global inifile, sqlfile, path, log_file, logger
        inifile, sqlfile, path, log_file, logger = service.get_name_file(__file__)
        if not os.path.exists(f'{path}/script/'):
            os.mkdir(f'{path}/script/')
        # запуск формы отображения
        app = MainForm()
        app.mainloop()
    except Exception as ex:
        service.logs(ex)


if __name__ == '__main__':
    main()