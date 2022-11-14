from tkinter import *
from time import sleep
import json
import threading

UI_STATES = ["select_user", "pick_shared", "pick_private", "show_keys"]
with open("defaultValues.json", "r") as f:
    DEFAULT_VALUES = json.loads(f.read())


class ControlPanel(Tk):
    """
    The main controlpanel for all features of the program
    """

    def __init__(self):
        super().__init__()
        self.main_thread = None  # Primary thread for the program
        self._state = UI_STATES[0]  # Current state of the program
        self.user = ""  # Alice or Bob
        self.temp_items = []  # Temporary items to be removed when switching screens

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value: str | int):
        if isinstance(value, int):
            value = UI_STATES[value]
        self._state = value
        match value:
            case "select_user":
                self.select_user()
            case "pick_shared":
                self.pick_shared()
            case "pick_private":
                self.pick_private()
            case "show_keys":
                self.show_keys()
            case _:
                raise ValueError("Invalid state")

    def set_selected_user(self, user: str):
        """
        Set the selected user
        """
        self.user = user
        self.state = 1

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

        title = Label(self, text="Diffie-Hellman", fg="#79c7c0", font="Rockwell 30", bg="#24292e")
        title.pack(pady=10)

    def clear_temp_items(self):
        """
        Remove all temporary items from the window
        """
        for item in self.temp_items:
            item.destroy()

    def select_user(self):
        """
        Change to the user selection screen
        """
        self.clear_temp_items()
        sub_title = Label(self, text="Select user", fg="#79c7c0", font="Rockwell 20", bg="#24292e")
        a_but = Button(
            self,
            text="Alice",
            width=20,
            height=5,
            bg="#2f4861",
            fg="#7abdff",
            font="Rockwell 20",
            command=lambda: self.set_selected_user("Alice")
        )
        b_but = Button(
            self,
            text="Bob",
            width=20,
            height=5,
            bg="#2f4861",
            fg="#7abdff",
            font="Rockwell 20",
            command=lambda: self.set_selected_user("Bob")
        )

        sub_title.place(relx=0.5, rely=0.2, anchor=CENTER)
        a_but.place(relx=0.25, rely=0.5, anchor=CENTER)
        b_but.place(relx=0.75, rely=0.5, anchor=CENTER)

        self.temp_items.extend([sub_title, a_but, b_but])

    def pick_shared(self):
        """
        Change to the shared values selection screen
        """
        self.clear_temp_items()
        sub_title = Label(self, text=f"Select shared values - {self.user}", fg="#79c7c0", font="Rockwell 20", bg="#24292e")
        sub_title.place(relx=0.5, rely=0.2, anchor=CENTER)
        p_label = Label(self, text="Shared prime (p):", fg="#79c7c0", font="Rockwell 16", bg="#24292e")
        p_entry = Entry(self, width=35, font="Rockwell 14")
        g_label = Label(self, text="Shared generator (g):", fg="#79c7c0", font="Rockwell 16", bg="#24292e")
        g_entry = Entry(self, width=35, font="Rockwell 14")
        submit_but = Button(self, text="Submit", width=9, height=2, bg="#2f4861", fg="#7abdff", font="Rockwell 14")
        p_label.place(relx=0.25, rely=0.4, anchor=CENTER)
        p_entry.place(relx=0.75, rely=0.4, anchor=CENTER)
        g_label.place(relx=0.25, rely=0.6, anchor=CENTER)
        g_entry.place(relx=0.75, rely=0.6, anchor=CENTER)
        submit_but.place(relx=0.5, rely=0.8, anchor=CENTER)
        self.temp_items.extend([sub_title, p_label, p_entry, g_label, g_entry])

    def pick_private(self):
        """
        Change to the private values selection screen
        """
        self.clear_temp_items()
        sub_title = Label(self, text="Select private value", fg="#79c7c0", font="Rockwell 20", bg="#24292e")
        sub_title.place(relx=0.5, rely=0.2, anchor=CENTER)
        self.temp_items.append(sub_title)

    def show_keys(self):
        """
        Change to the keys screen
        """
        self.clear_temp_items()
        sub_title = Label(self, text="Keys", fg="#79c7c0", font="Rockwell 20", bg="#24292e")
        sub_title.place(relx=0.5, rely=0.2, anchor=CENTER)
        self.temp_items.append(sub_title)


if __name__ == '__main__':
    CP = ControlPanel()
    CP.select_user()
    CP.start()
