import customtkinter
import tkinter
import Service.fdb_service as service


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

        self.button = customtkinter.CTkButton(self, command=self.run_clear_bd)
        self.button.grid(row=2, column=0, padx=40, pady=10)

        self.check_connect_fdb = service.get_setting_bd()[0]
        self.label_one = customtkinter.CTkLabel(self, text=f"БД:{self.check_connect_fdb}")
        self.label_one.grid(row=3, column=0, padx=20, pady=10)
    #
    def run_clear_bd(self):
        # if self.radio_button_not_nalic.cget()
        print("button click")
        print("213")


def main():
    app = MainForm()
    app.mainloop()


if __name__ == '__main__':
    main()
