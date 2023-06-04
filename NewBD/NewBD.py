import customtkinter
import tkinter
import Service.fdb_service as service
import script


class MainForm(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("368x480")
        self.title("Создание новой БД ПК'Аптека-Урал'")

        # список для выбора действий
        self.radiobutton_frame = customtkinter.CTkFrame(self)
        self.radiobutton_frame.grid(row=0, column=0, padx=(10, 10), pady=(10, 0), sticky="nsew",)
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


class LevelScript(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("400x300")
        self.title("Список скриптов")
        sql = service.sql()
        data = sql.load_file_sql()
        n = 0
        for item in data:
            self.label = customtkinter.CTkLabel(self, text=item["name_item"])
            self.label.grid(row=n, column=0, padx=10)
            self.entry = customtkinter.CTkLabel(self, text=item["pos_item"])
            self.entry.grid(row=n, column=1, padx=10)
            self.textscript = customtkinter.CTkTextbox(self, )
            self.textscript.grid(row=n, column=2, padx=10)
            self.textscript.insert("0.0", item["text_item"])
            n = n+1
        self.button_add = customtkinter.CTkButton(self, text='Добавить скрипт', command=self.add_script())
        self.button_add.grid(row=n+1, column=0, padx=10)

    def add_script(self):
        pass

def main():
    # глобальные файлы, влкючение логирования
    service.get_name_file(__file__)
    # запуск формы отображения
    app = MainForm()
    app.mainloop()


if __name__ == '__main__':
    main()
