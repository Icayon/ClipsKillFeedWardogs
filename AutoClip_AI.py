import customtkinter as ctk
from ui import AutoClipWardogsApp

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

def main():
    app = AutoClipWardogsApp()
    app.mainloop()

if __name__ == "__main__":
    main()