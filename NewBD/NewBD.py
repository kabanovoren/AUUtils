import customtkinter
import tkinter
import Service.fdb_service as service
import script


class MainForm(customtkinter.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("368x480")
        self.title("Создание новой БД ПК'Аптека-Урал'")

        # список для выбора действий
        self.radiobutton_frame = customtkinter.CTkFrame(self)
        self.radiobutton_frame.grid(row=0, column=0, padx=(10, 10), pady=(10, 0), sticky="nsew", )
        self.radio_var = tkinter.IntVar(value=0)
        self.label_radio_group = customtkinter.CTkLabel(master=self.radiobutton_frame, text="Выберите действие:")
        self.label_radio_group.grid(row=0, column=2, columnspan=1, padx=10, pady=10, sticky="")

        self.radio_button_all_delete = customtkinter.CTkRadioButton(master=self.radiobutton_frame,
                                                                    variable=self.radio_var,
                                                                    value=0,
                                                                    text="Удалить все данные, справочники остаются")
        self.radio_button_all_delete.grid(row=1, column=2, pady=10, padx=20, sticky="n")
        self.radio_button_not_nalic = customtkinter.CTkRadioButton(master=self.radiobutton_frame,
                                                                   variable=self.radio_var,
                                                                   value=1,
                                                                   text="Удалить все двжиения товара,\nналичие перенести в документ ввод остатков")
        self.radio_button_not_nalic.grid(row=2, column=2, pady=10, padx=20, sticky="n")

        self.button_execute = customtkinter.CTkButton(self, command=self.run_clear_bd, text='Выполнить')
        self.button_execute.grid(row=2, column=0, padx=40, pady=10)

        self.button_script = customtkinter.CTkButton(self, command=self.open_script_frame, text='Список скриптов')
        self.button_script.grid(row=3, column=0, padx=10, pady=10)
        self.check_connect_fdb = service.get_setting_bd()[0]
        self.label_one = customtkinter.CTkLabel(self, text=f"БД:{self.check_connect_fdb}")
        self.label_one.grid(row=4, column=0, padx=20, pady=10)
        self.toplevel_window = None

    def run_clear_bd(self):
        if self.radio_var.get() == 0:
            script.all_delete()
        else:
            script.not_nalic()

    def open_script_frame(self):
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            self.toplevel_window = LevelScript(self)  # create window if its None or destroyed
        else:
            self.toplevel_window.focus()  # if window exists focus it


class LevelScript(customtkinter.CTkToplevel, service.sql):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("800x600")
        self.title("Список скриптов")
        sql = service.sql()
        data = sql.load_file_sql()
        self.label = customtkinter.CTkLabel(self, text='Наименование скрипта', width=100)
        self.label.grid(row=0, column=0, padx=10)
        self.label2 = customtkinter.CTkLabel(self, text='Позиция запуска', width=100)
        self.label2.grid(row=0, column=1, padx=10)
        self.label3 = customtkinter.CTkLabel(self, text='Текст', width=370)
        self.label3.grid(row=0, column=2, padx=10)
        self.n = 1
        self.list_entry = []
        for item in data:
            self.list_entry.append([customtkinter.CTkEntry(self, width=150),
                                   customtkinter.CTkEntry(self, width=50),
                                   customtkinter.CTkTextbox(self, width=370, height=50)]
                                  )

        for entry in self.list_entry:
            entry[0].insert(0, data[self.n-1]["name_item"])
            entry[1].insert(0, data[self.n-1]["pos_item"])
            entry[2].insert("0.0", data[self.n-1]["text_item"])
            entry[0].grid(row=self.n, column=0, padx=5, pady=5)
            entry[1].grid(row=self.n, column=1, padx=5, pady=5)
            entry[2].grid(row=self.n, column=2, padx=5, pady=5)
            self.n = self.n + 1
        self.button_add = customtkinter.CTkButton(self, text='Добавить скрипт', command=self.add_script)
        self.button_add.grid(row=self.n, column=0, padx=10)
        self.button_save = customtkinter.CTkButton(self, text='Сохранить изменения', command=self.save_script)
        self.button_save.grid(row=self.n, column=1, padx=10)

    def add_script(self):
        self.list_entry.append([customtkinter.CTkEntry(self, width=150),
                               customtkinter.CTkEntry(self, width=50),
                               customtkinter.CTkTextbox(self, width=370, height=50)]
                              )
        for entry in self.list_entry:
            entry[0].grid(row=self.n, column=0, padx=5, pady=5)
            entry[1].grid(row=self.n, column=1, padx=5, pady=5)
            entry[2].grid(row=self.n, column=2, padx=5, pady=5)
            self.n = self.n + 1
        self.button_add.grid(row=self.n, column=0, padx=10)
        self.button_save.grid(row=self.n, column=1, padx=10)

    def save_script(self):
        self.data_list = []
        for entry in self.list_entry:
            self.data_list.append(
                {'name_item': entry[0].get(),
                 'pos_item': entry[1].get(),
                 'text_item': entry[2].get(1.0)}
            )
        self.name_file = service.get_name_file(__file__)[1]
        self.save_file_sql(self.data_list)







def main():
    # глобальные файлы, влкючение логирования
    service.get_name_file(__file__)
    # запуск формы отображения
    app = MainForm()
    app.mainloop()


if __name__ == '__main__':
    main()
