from tkinter import *
from time import sleep
import json
import threading

UI_STATES = ["select_user", "pick_shared", "pick_secret", "awaiting_public", "show_keys"]
with open("defaultValues.json", "r") as f:
    DEFAULT_VALUES = json.loads(f.read())


class Placeholder:
    def __init__(self):
        """Placeholder class for the Diffie-Hellman class"""
        self.name = ""
        self.g = -1
        self.p = -1
        self.port = 9000
        self.remote_port = 9001

    @staticmethod
    def send_request(request_type: str) -> bool:
        """Placeholder for send_request"""
        print("Sending request of type ", request_type)
        return True


class ControlPanel(Tk):
    """
    The main controlpanel for all features of the program
    """

    def __init__(self, DH):
        super().__init__()
        self.DH = DH
        self._state = UI_STATES[0]  # Current state of the program
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
            case "pick_secret":
                self.pick_secret()
            case "awaiting_public":
                self.awaiting_public()
            case "show_keys":
                self.show_keys()
            case _:
                raise ValueError("Invalid state")

    def set_selected_user(self, user: str):
        """
        Set the selected user, and start receiving requests
        """
        self.DH.name = user
        self.DH.start()
        self.state = 1

    def get_shared(self, p: int, g: int):
        """
        Set the shared values
        """
        self.DH.p = p
        self.DH.g = g
        self.state = 2

    def submit_shared(self, p: int, g: int):
        """
        Submit the shared values and send them to the other user
        """
        self.DH.p = p
        self.DH.g = g
        self.DH.send_request("shared")
        self.state = 2

    def submit_secret(self, secret: int):
        """
        Submit the secret value
        """
        self.DH.secret = secret
        self.DH.calculate_public()
        self.DH.send_request("public")
        if self.DH.remote_public == -1:
            self.state = 3
        else:
            self.DH.calculate_shared_secret()
            self.state = 4

    def get_public(self, remote_public: int):
        """
        Get the public values
        """
        print("Got public value: ", remote_public)
        if self.state == "pick_secret":
            remote_public_label = Label(self, text=f"Remote public value: {remote_public}", fg="#79c7c0", font="Rockwell 16", bg="#24292e")
            remote_public_label.place(relx=0.5, rely=0.5, anchor=CENTER)
            self.temp_items.append(remote_public_label)
        elif self.state == "awaiting_public":
            self.state = 4

    def start(self):
        """
        Start the program
        """
        print("Setting up main window...")
        self.setup_main_window()
        print("Running program...")
        self.select_user()
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
        sub_title = Label(self, text=f"Select shared values - {self.DH.name}", fg="#79c7c0", font="Rockwell 20", bg="#24292e")
        sub_title.place(relx=0.5, rely=0.2, anchor=CENTER)
        p_label = Label(self, text="Shared prime (p):", fg="#79c7c0", font="Rockwell 16", bg="#24292e")
        p_entry = Entry(self, width=35, font="Rockwell 14")
        p_default = Button(
            self,
            text="Default",
            width=10,
            height=1,
            bg="#2f4861",
            fg="#7abdff",
            font="Rockwell 14",
            command=lambda: p_entry.insert(0, DEFAULT_VALUES["p"])
        )

        g_label = Label(self, text="Shared generator (g):", fg="#79c7c0", font="Rockwell 16", bg="#24292e")
        g_entry = Entry(self, width=35, font="Rockwell 14")
        g_default = Button(
            self,
            text="Default",
            width=10,
            height=1,
            bg="#2f4861",
            fg="#7abdff",
            font="Rockwell 14",
            command=lambda: g_entry.insert(0, DEFAULT_VALUES["g"])
        )

        submit_but = Button(
            self,
            text="Submit",
            width=9,
            height=2,
            bg="#2f4861",
            fg="#7abdff", font="Rockwell 14",
            command=lambda: self.submit_shared(int(p_entry.get()), int(g_entry.get()))
        )

        p_label.place(relx=0.25, rely=0.4, anchor=CENTER)
        p_entry.place(relx=0.75, rely=0.4, anchor=CENTER)
        p_default.place(relx=0.75, rely=0.46, anchor=CENTER)
        g_label.place(relx=0.25, rely=0.6, anchor=CENTER)
        g_entry.place(relx=0.75, rely=0.6, anchor=CENTER)
        g_default.place(relx=0.75, rely=0.66, anchor=CENTER)
        submit_but.place(relx=0.5, rely=0.8, anchor=CENTER)
        self.temp_items.extend([sub_title, p_label, p_entry, p_default, g_label, g_entry, g_default, submit_but])

    def pick_secret(self):
        """
        Change to the secret values selection screen
        """
        self.clear_temp_items()
        sub_title = Label(self, text=f"Select personal secret value - {self.DH.name}", fg="#79c7c0", font="Rockwell 20", bg="#24292e")
        sub_title.place(relx=0.5, rely=0.2, anchor=CENTER)
        p_label = Label(self, text=f"Shared prime (p): {self.DH.p}", fg="#79c7c0", font="Rockwell 16", bg="#24292e")
        g_label = Label(self, text=f"Shared generator (g): {self.DH.g}", fg="#79c7c0", font="Rockwell 16", bg="#24292e")
        x_label = Label(self, text=f"Private value ({self.DH.name[0].lower()}):", fg="#79c7c0", font="Rockwell 16", bg="#24292e")
        x_entry = Entry(self, width=35, font="Rockwell 14")
        submit_but = Button(
            self,
            text="Submit",
            width=9,
            height=2,
            bg="#2f4861",
            fg="#7abdff",
            font="Rockwell 14",
            command=lambda: self.submit_secret(int(x_entry.get()))
        )
        p_label.place(relx=0.50, rely=0.3, anchor=CENTER)
        g_label.place(relx=0.50, rely=0.4, anchor=CENTER)
        x_label.place(relx=0.25, rely=0.6, anchor=CENTER)
        x_entry.place(relx=0.75, rely=0.6, anchor=CENTER)
        submit_but.place(relx=0.5, rely=0.8, anchor=CENTER)
        self.temp_items.extend([sub_title, p_label, g_label, x_label, x_entry, submit_but])

    def awaiting_public(self):
        """
        Change to the awaiting public value screen
        """
        self.clear_temp_items()
        sub_title = Label(self, text=f"Awaiting public value from {self.DH.other_name}", fg="#79c7c0", font="Rockwell 20", bg="#24292e")
        sub_title.place(relx=0.5, rely=0.2, anchor=CENTER)
        p_label = Label(self, text=f"Shared prime (p): {self.DH.p}", fg="#79c7c0", font="Rockwell 16", bg="#24292e")
        g_label = Label(self, text=f"Shared generator (g): {self.DH.g}", fg="#79c7c0", font="Rockwell 16", bg="#24292e")
        x_label = Label(self, text=f"Private value ({self.DH.name[0].lower()}): {self.DH.secret}", fg="#79c7c0", font="Rockwell 16", bg="#24292e")
        X_label = Label(self, text=f"Public value ({self.DH.name[0].upper()}): {self.DH.public}", fg="#79c7c0", font="Rockwell 16", bg="#24292e")
        p_label.place(relx=0.50, rely=0.3, anchor=CENTER)
        g_label.place(relx=0.50, rely=0.4, anchor=CENTER)
        x_label.place(relx=0.50, rely=0.5, anchor=CENTER)
        X_label.place(relx=0.50, rely=0.6, anchor=CENTER)
        self.temp_items.extend([sub_title, p_label, g_label, x_label, X_label])

    def show_keys(self):
        """
        Change to the keys screen
        """
        self.clear_temp_items()
        sub_title = Label(self, text="Keys", fg="#79c7c0", font="Rockwell 20", bg="#24292e")
        sub_title.place(relx=0.5, rely=0.15, anchor=CENTER)
        p_label = Label(self, text=f"Shared prime (p): {self.DH.p}", fg="#a65755", font="Rockwell 16", bg="#24292e")
        g_label = Label(self, text=f"Shared generator (g): {self.DH.g}", fg="#a65755", font="Rockwell 16", bg="#24292e")
        x_label = Label(self, text=f"Private value ({self.DH.name[0].lower()}): {self.DH.secret}", fg="#79c7c0", font="Rockwell 16", bg="#24292e")
        X_label = Label(self, text=f"Public value ({self.DH.name[0].upper()}): {self.DH.public}", fg="#a65755", font="Rockwell 16", bg="#24292e")
        Y_label = Label(self, text=f"Public value ({self.DH.other_name[0].upper()}): {self.DH.remote_public}", fg="#a65755", font="Rockwell 16", bg="#24292e")
        shared_label = Label(self, text=f"Shared key: {self.DH.shared_secret}", fg="#79c7c0", font="Rockwell 18", bg="#24292e")

        p_label.place(relx=0.50, rely=0.24, anchor=CENTER)
        g_label.place(relx=0.50, rely=0.33, anchor=CENTER)
        x_label.place(relx=0.50, rely=0.42, anchor=CENTER)
        X_label.place(relx=0.50, rely=0.52, anchor=CENTER)
        Y_label.place(relx=0.50, rely=0.62, anchor=CENTER)
        shared_label.place(relx=0.50, rely=0.72, anchor=CENTER)

        self.temp_items.extend([sub_title, p_label, g_label, x_label, X_label, Y_label, shared_label])


if __name__ == '__main__':
    PH = Placeholder()
    CP = ControlPanel(PH)
    CP.start()
