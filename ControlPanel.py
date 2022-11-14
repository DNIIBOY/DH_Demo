from tkinter import *
from time import sleep
import json
import threading


class ControlPanel(Tk):
    """
    The main controlpanel for all features of the program
    """

    def __init__(self):
        super().__init__()
        self.main_thread = None  # Thread for running instalocker and other functions

        self.temp_items = []  # Temporary items to be removed when switching screens

    def start(self):
        """
        Start the program
        """
        print("Setting up main window...")
        self.setup_main_window()
        print("Running program...")
        self.mainloop()

    def setup_main_window(self) -> None:
        """
        Set up the main window, including title and size
        """
        self.title("Diffie-Hellman Key Exchange")
        self.minsize(500, 250)
        self.geometry("970x550")  # Default size
        self.configure(
            background="#24292e"
        )

        title = Label(self, text="Diffie-Hellman", fg="#ff4b50", font="Rockwell 30", bg="#24292e")
        title.pack(pady=10)

    def select_user(self):
        """
        Change to the user selection screen
        """
        pass


if __name__ == '__main__':
    CP = ControlPanel()
    CP.start()
