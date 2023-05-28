import customtkinter as ctk


class MainForm(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("600x500")
        self.title("CTk example")

        # add widgets to app
        self.button = ctk.CTkButton(self, command=self.button_click)
        self.button.grid(row=0, column=0, padx=20, pady=10)

        # add methods to app

    def button_click(self):
        print("button click")


def main():
    app = MainForm()
    app.mainloop()

if __name__ == '__main__':
    main()
