import customtkinter as ctk


class MainForm(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("600x500")
        self.title("Создание новой БД ПК'Аптека-Урал'")

        self.label_one = ctk.CTkLabel(self, text='Очищаем БД:')
        self.label_one.grid(row=0, column=0, padx=20, pady=10)
        check_var = ctk.StringVar(value="on")
        check_off = ctk.StringVar(value="off")
        self.checkbox_all = ctk.CTkCheckBox(self, text='Удаляем все данные,\n кроме справочникво', variable=check_var,
                                            onvalue="on", offvalue="off", command=self.check_ext)
        self.checkbox_all.grid(row=1, column=0, padx=20, pady=0)

        self.checkbox_one = ctk.CTkCheckBox(self, text='Наличие переносим в один документ, \n остальные удаялем',
                                            variable=check_off, onvalue="on", offvalue="off", command=self.check_ext)
        self.checkbox_one.grid(row=1, column=1, padx=20, pady=0)
        self.button = ctk.CTkButton(self, command=self.button_click)
        self.button.grid(row=2, column=0, padx=40, pady=10)

    def check_ext(self):
        if self.checkbox_all.get() == "off":
            self.checkbox_one.setvar(value="on")
        # add methods to app

    def button_click(self):
        print("button click")


def main():
    app = MainForm()
    app.mainloop()


if __name__ == '__main__':
    main()
