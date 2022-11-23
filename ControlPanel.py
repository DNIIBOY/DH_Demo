from tkinter import *
import json

UI_STATES = ["select_user", "pick_shared", "pick_secret", "awaiting_public", "show_keys", "messaging"]

with open("defaultValues.json", "r") as f:
    DEFAULT_VALUES = json.loads(f.read())

with open("colors.json") as f:
    COLORS = json.loads(f.read())


class ControlPanel(Tk):
    """
    The main controlpanel for all features of the program
    """

    def __init__(self, DH):
        super().__init__()
        self._state = UI_STATES[0]  # Current state of the program
        self.DH = DH  # The Diffie-Hellman object, used to get/set values
        self.temp_items = []  # Temporary items to be removed when switching screens
        self.name_label = Label(self, text="", fg=COLORS["text"], font="Rockwell 22", bg=COLORS["background"])  # Label for the name of the user
        self.lost_connection_label = Label(  # Label for when the connection is lost
            self,
            text="Lost connection to remote user",
            font="Rockwell 16",
            fg=COLORS["error"],
            bg=COLORS["background"]
        )
        self.value_canvas = None  # Canvas that will display all values

        self.message_canvas = Canvas(self, width=500, height=300, bg=COLORS["accent"], highlightthickness=1)  # Canvas for the messaging screen
        self.message_canvas.pack_propagate(False)  # Don't allow the canvas to change size
        self.message_list = []  # List of all currently displayed messages

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
            case "messaging":
                self.messaging()
            case _:
                raise ValueError("Invalid state")

    def set_selected_user(self, user: str):
        """
        Set the selected user, and start receiving requests
        """
        self.name_label.config(text=user)
        self.DH.name = user
        self.DH.start()
        self.state = 1

    def get_shared(self, p: int, g: int):
        """
        Set the shared values
        """
        self.lost_connection_label.place_forget()  # Remove the lost connection label
        self.DH.p = p
        self.DH.g = g
        self.state = 2

    def submit_shared(self, p: int, g: int):
        """
        Submit the shared values and send them to the other user
        """
        self.DH.p = p
        self.DH.g = g
        connection = self.DH.send_request("shared")
        if connection:
            self.lost_connection_label.place_forget()
        else:
            self.lost_connection_label.place(relx=0.5, rely=0.95, anchor=CENTER)
        self.state = 2

    def submit_secret(self, secret: int):
        """
        Submit the secret value
        """
        self.DH.secret = secret
        self.DH.calculate_public()
        connection = self.DH.send_request("public")
        if connection:
            self.lost_connection_label.place_forget()
        else:
            self.lost_connection_label.place(relx=0.5, rely=0.9, anchor=CENTER)

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
        self.lost_connection_label.place_forget()  # Remove the lost connection label
        if self.state == "pick_secret":
            remote_public_label = Label(
                self.value_canvas,
                text=f"Remote public key ({self.DH.remote_name[0].upper()})",
                font="Rockwell 20",
                fg=COLORS["text"],
                bg=COLORS["background"]
            )
            remote_public_value = Label(
                self.value_canvas,
                text=remote_public,
                font="Rockwell 20",
                fg=COLORS["text"],
                bg=COLORS["background"]
            )
            remote_public_label.place(relx=0, rely=0.7, anchor=W)
            remote_public_value.place(relx=0.407, rely=0.7, anchor=W)
            self.value_canvas.create_line(0, 200, 900, 200, fill=COLORS["accent"], width=2)
            self.temp_items.extend([remote_public_label, remote_public_value])
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
        self.geometry("960x540")  # Default size
        self.configure(
            background=COLORS["background"]
        )

        title = Label(self, text="Diffie-Hellman", font="Rockwell 40", fg=COLORS["text"], bg=COLORS["background"])
        title.pack(pady=10)
        self.name_label.place(relx=0.88, rely=0.1, anchor=CENTER)

    def clear_temp_items(self):
        """
        Remove all temporary items from the window
        """
        self.message_canvas.place_forget()
        for item in self.temp_items:
            item.destroy()

    def send_message(self, message: str, field: Entry):
        """
        Send a message to the other client
        """
        if message == "":
            return
        if self.state == "messaging":
            connection = self.DH.send_message(message)
            if connection:
                self.lost_connection_label.place_forget()
            else:
                self.lost_connection_label.place(relx=0.5, rely=0.9, anchor=CENTER)
        self.message_list.append(Label(self.message_canvas, text=message, fg=COLORS["text"], font="Rockwell 16", bg=COLORS["accent"], wraplength=500))
        self.message_list[-1].pack(anchor=NE, pady=5, padx=5)
        if len(self.message_list) > 8:
            self.message_list.pop(0).destroy()  # Remove the oldest message
        field.delete(0, END)

    def receive_message(self, message: str):
        """
        Receive a message from the other client
        """
        print(f"Received message: {message}")  # Print the message
        if self.state != "messaging":
            return
        if message is False:  # If we receive a message that could not be decrypted
            self.message_list.append(
                Label(self.message_canvas, text="*Invalid Message*", fg=COLORS["text"], font="Rockwell 16", bg=COLORS["accent"], wraplength=500))
        else:
            self.message_list.append(
                Label(self.message_canvas, text=message, fg=COLORS["text"], font="Rockwell 16", bg=COLORS["accent"], wraplength=500))
        self.message_list[-1].pack(anchor=NW, pady=5, padx=5)
        if len(self.message_list) > 8:
            self.message_list.pop(0).destroy()  # Remove the oldest message

    def select_user(self):
        """
        Change to the user selection screen
        """
        self.clear_temp_items()
        sub_title = Label(self, text="Select user", fg=COLORS["text"], font="Rockwell 23", bg=COLORS["background"])
        a_button = Button(
            self,
            text="Alice",
            width=10,
            height=2,
            bg=COLORS["accent"],
            fg=COLORS["text"],
            borderwidth=0,
            font="Rockwell 45",
            command=lambda: self.set_selected_user("Alice")
        )
        b_button = Button(
            self,
            text="Bob",
            width=10,
            height=2,
            bg=COLORS["accent"],
            fg=COLORS["text"],
            borderwidth=0,
            font="Rockwell 45",
            command=lambda: self.set_selected_user("Bob")
        )

        sub_title.place(relx=0.5, rely=0.17, anchor=CENTER)
        a_button.place(relx=0.25, rely=0.5, anchor=CENTER)
        b_button.place(relx=0.75, rely=0.5, anchor=CENTER)

        self.temp_items.extend([sub_title, a_button, b_button])

    def pick_shared(self):
        """
        Change to the shared values selection screen
        """
        self.clear_temp_items()
        validation = self.register(ints_only)  # Only allow ints as input
        sub_title = Label(self, text=f"Select shared values", fg=COLORS["text"], font="Rockwell 24", bg=COLORS["background"])
        sub_title.place(relx=0.5, rely=0.17, anchor=CENTER)
        p_label = Label(self, text="Shared prime (p)", fg=COLORS["text"], font="Rockwell 16", bg=COLORS["background"])
        p_entry = Entry(
            self,
            width=33,
            font="Rockwell 20",
            bg=COLORS["accent"],
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            borderwidth=0,
            validate="key",
            validatecommand=(validation, "%P")
        )
        p_default = Button(
            self,
            text="Default",
            width=10,
            height=1,
            bg=COLORS["accent"],
            fg=COLORS["text"],
            font="Rockwell 14",
            borderwidth=0,
            command=lambda: (p_entry.delete(0, END), p_entry.insert(0, DEFAULT_VALUES["p"]))  # Clear the entry and insert the default value
        )

        g_label = Label(self, text="Shared generator (g)", fg=COLORS["text"], font="Rockwell 16", bg=COLORS["background"])
        g_entry = Entry(
            self,
            width=33,
            font="Rockwell 20",
            bg=COLORS["accent"],
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            borderwidth=0,
            validate="key",
            validatecommand=(validation, "%P")
        )
        g_entry.bind("<Return>", lambda event: submit_button.invoke())
        g_default = Button(
            self,
            text="Default",
            width=10,
            height=1,
            bg=COLORS["accent"],
            fg=COLORS["text"],
            font="Rockwell 14",
            borderwidth=0,
            command=lambda: (g_entry.delete(0, END), g_entry.insert(0, DEFAULT_VALUES["g"]))  # Clear the entry and insert the default value
        )

        submit_button = Button(
            self,
            text="Send",
            width=9,
            height=1,
            bg=COLORS["accent"],
            fg=COLORS["text"], font="Rockwell 25",
            borderwidth=0,
            command=lambda: self.submit_shared(int(p_entry.get()), int(g_entry.get()))
        )

        p_label.place(relx=0.05, rely=0.4, anchor=W)
        p_entry.place(relx=0.55, rely=0.4, anchor=CENTER)
        p_default.place(relx=0.88, rely=0.4, anchor=CENTER)
        g_label.place(relx=0.05, rely=0.6, anchor=W)
        g_entry.place(relx=0.55, rely=0.6, anchor=CENTER)
        g_default.place(relx=0.88, rely=0.6, anchor=CENTER)
        submit_button.place(relx=0.5, rely=0.8, anchor=CENTER)
        self.temp_items.extend([sub_title, p_label, p_entry, p_default, g_label, g_entry, g_default, submit_button])

    def pick_secret(self):
        """
        Change to the secret values selection screen
        """
        self.clear_temp_items()
        validation = self.register(ints_only)  # Only allow ints as input
        sub_title = Label(self, text=f"Select private value", fg=COLORS["text"], font="Rockwell 24", bg=COLORS["background"])
        sub_title.place(relx=0.5, rely=0.17, anchor=CENTER)
        self.value_canvas = Canvas(self, width=750, height=250, bg=COLORS["background"], highlightthickness=0)
        self.value_canvas.place(relx=0.04, rely=0.52, anchor=W)
        p_label = Label(self.value_canvas, text=f"Shared prime (p)", fg=COLORS["text"], font="Rockwell 20", bg=COLORS["background"])
        p_value = Label(self.value_canvas, text=self.DH.p, fg=COLORS["text"], font="Rockwell 20", bg=COLORS["background"])
        g_label = Label(self.value_canvas, text=f"Shared generator (g)", fg=COLORS["text"], font="Rockwell 20", bg=COLORS["background"])
        g_value = Label(self.value_canvas, text=self.DH.g, fg=COLORS["text"], font="Rockwell 20", bg=COLORS["background"])
        x_label = Label(self.value_canvas, text=f"Private value ({self.DH.name[0].lower()})", fg=COLORS["text"], font="Rockwell 20",
                        bg=COLORS["background"])
        x_entry = Entry(
            self.value_canvas,
            width=35,
            font="Rockwell 20",
            bg=COLORS["accent"],
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            borderwidth=0,
            validate="key",
            validatecommand=(validation, "%P")
        )
        x_entry.bind("<Return>", lambda event: submit_button.invoke())
        submit_button = Button(
            self,
            text="Send",
            width=9,
            height=1,
            bg=COLORS["accent"],
            fg=COLORS["text"], font="Rockwell 25",
            borderwidth=0,
            command=lambda: self.submit_secret(int(x_entry.get()))
        )
        p_label.place(relx=0, rely=0.1, anchor=W)
        p_value.place(relx=0.4, rely=0.1, anchor=W)
        g_label.place(relx=0, rely=0.3, anchor=W)
        g_value.place(relx=0.4, rely=0.3, anchor=W)
        x_label.place(relx=0, rely=0.5, anchor=W)
        x_entry.place(relx=0.407, rely=0.5, anchor=W)
        self.value_canvas.create_line(0, 45, 900, 45, fill=COLORS["accent"], width=2)
        self.value_canvas.create_line(0, 95, 900, 95, fill=COLORS["accent"], width=2)
        self.value_canvas.create_line(0, 150, 900, 150, fill=COLORS["accent"], width=2)
        submit_button.place(relx=0.5, rely=0.8, anchor=CENTER)
        self.temp_items.extend([sub_title, p_label, g_label, x_label, x_entry, self.value_canvas, submit_button])

    def awaiting_public(self):
        """
        Change to the awaiting public value screen
        """
        self.clear_temp_items()
        sub_title = Label(self, text=f"Awaiting public key from {self.DH.remote_name}", fg=COLORS["text"], font="Rockwell 24",
                          bg=COLORS["background"])
        sub_title.place(relx=0.5, rely=0.17, anchor=CENTER)
        self.value_canvas = Canvas(self, width=750, height=250, bg=COLORS["background"], highlightthickness=0)
        self.value_canvas.place(relx=0.04, rely=0.52, anchor=W)
        p_label = Label(self.value_canvas, text=f"Shared prime (p)", fg=COLORS["text"], font="Rockwell 20", bg=COLORS["background"])
        p_value = Label(self.value_canvas, text=self.DH.p, fg=COLORS["text"], font="Rockwell 20", bg=COLORS["background"])
        g_label = Label(self.value_canvas, text=f"Shared generator (g)", fg=COLORS["text"], font="Rockwell 20", bg=COLORS["background"])
        g_value = Label(self.value_canvas, text=self.DH.g, fg=COLORS["text"], font="Rockwell 20", bg=COLORS["background"])
        x_label = Label(self.value_canvas, text=f"Private key ({self.DH.name[0].lower()})", fg=COLORS["text"], font="Rockwell 20",
                        bg=COLORS["background"])
        x_value = Label(self.value_canvas, text=self.DH.secret, fg=COLORS["text"], font="Rockwell 20", bg=COLORS["background"])
        X_label = Label(self.value_canvas, text=f"Public key ({self.DH.name[0].upper()})", fg=COLORS["text"], font="Rockwell 20",
                        bg=COLORS["background"])
        X_value = Label(self.value_canvas, text=self.DH.public, fg=COLORS["text"], font="Rockwell 20", bg=COLORS["background"])
        p_label.place(relx=0, rely=0.1, anchor=W)
        p_value.place(relx=0.4, rely=0.1, anchor=W)
        g_label.place(relx=0, rely=0.3, anchor=W)
        g_value.place(relx=0.4, rely=0.3, anchor=W)
        x_label.place(relx=0, rely=0.5, anchor=W)
        x_value.place(relx=0.4, rely=0.5, anchor=W)
        X_label.place(relx=0, rely=0.7, anchor=W)
        X_value.place(relx=0.4, rely=0.7, anchor=W)
        self.value_canvas.create_line(0, 45, 900, 45, fill=COLORS["accent"], width=2)
        self.value_canvas.create_line(0, 95, 900, 95, fill=COLORS["accent"], width=2)
        self.value_canvas.create_line(0, 150, 900, 150, fill=COLORS["accent"], width=2)
        self.value_canvas.create_line(0, 200, 900, 200, fill=COLORS["accent"], width=2)
        self.temp_items.extend([sub_title, p_label, g_label, x_label, x_value, X_label, X_value, self.value_canvas])

    def show_keys(self):
        """
        Change to the keys screen
        """
        self.clear_temp_items()
        sub_title = Label(self, text="Keys", fg=COLORS["text"], font="Rockwell 20", bg=COLORS["background"])
        sub_title.place(relx=0.5, rely=0.15, anchor=CENTER)
        p_label = Label(self, text=f"Shared prime (p): {self.DH.p}", fg=COLORS["text"], font="Rockwell 16", bg=COLORS["background"])
        g_label = Label(self, text=f"Shared generator (g): {self.DH.g}", fg=COLORS["text"], font="Rockwell 16", bg=COLORS["background"])
        x_label = Label(self, text=f"Private value ({self.DH.name[0].lower()}): {self.DH.secret}", fg=COLORS["text"], font="Rockwell 16",
                        bg=COLORS["background"])
        X_label = Label(self, text=f"Public value ({self.DH.name[0].upper()}): {self.DH.public}", fg=COLORS["text"], font="Rockwell 16",
                        bg=COLORS["background"])
        Y_label = Label(self, text=f"Public value ({self.DH.remote_name[0].upper()}): {self.DH.remote_public}", fg=COLORS["text"], font="Rockwell 16",
                        bg=COLORS["background"])
        shared_label = Label(self, text=f"Shared key: {self.DH.shared_secret}", fg=COLORS["text"], font="Rockwell 18", bg=COLORS["background"])
        message_button = Button(
            self,
            text="Start messaging",
            width=15,
            height=2,
            bg=COLORS["accent"],
            fg=COLORS["text"],
            font="Rockwell 14",
            command=lambda: setattr(self, "state", "messaging")
        )

        p_label.place(relx=0.50, rely=0.24, anchor=CENTER)
        g_label.place(relx=0.50, rely=0.33, anchor=CENTER)
        x_label.place(relx=0.50, rely=0.42, anchor=CENTER)
        X_label.place(relx=0.50, rely=0.52, anchor=CENTER)
        Y_label.place(relx=0.50, rely=0.62, anchor=CENTER)
        shared_label.place(relx=0.50, rely=0.72, anchor=CENTER)
        message_button.place(relx=0.5, rely=0.85, anchor=CENTER)

        self.temp_items.extend([sub_title, p_label, g_label, x_label, X_label, Y_label, shared_label, message_button])

    def messaging(self):
        """
        A place to message the other client, using AES with the shared secret as key
        """
        self.clear_temp_items()
        sub_title = Label(self, text="Messaging", fg=COLORS["text"], font="Rockwell 20", bg=COLORS["background"])
        secret_label = Label(self, text=f"Shared secret: {self.DH.shared_secret}", fg=COLORS["text"], font="Rockwell 16", bg=COLORS["background"],
                             wraplength=150)
        message_input = Entry(self, width=50, font="Rockwell 14", fg=COLORS["text"], bg=COLORS["background"], insertbackground=COLORS["text"])
        send_button = Button(
            self,
            text="Send",
            width=10,
            height=1,
            fg=COLORS["text"],
            bg=COLORS["accent"],
            font="Rockwell 14",
            command=lambda: self.send_message(message_input.get(), message_input)
        )
        message_input.bind("<Return>", lambda event: send_button.invoke())

        sub_title.place(relx=0.5, rely=0.15, anchor=CENTER)
        self.message_canvas.place(relx=0.5, rely=0.5, anchor=CENTER)
        secret_label.place(relx=0.12, rely=0.3, anchor=CENTER)
        message_input.place(relx=0.5, rely=0.8, anchor=CENTER)
        send_button.place(relx=0.5, rely=0.9, anchor=CENTER)

        self.temp_items.extend([sub_title, secret_label, message_input, send_button])


def ints_only(string):
    """
    :return: True if the string is an int
    """
    if string == "":  # Empty string is allowed
        return True
    try:
        int(string)
        return True
    except ValueError:
        return False
