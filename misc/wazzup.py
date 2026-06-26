from tkinter import simpledialog
from tkinter import messagebox
from tkinter import ttk
import tkinter as tk
import ipaddress
import threading
import hashlib
import socket
import random
import queue

SEP = " │ "
PORT = 5499
RECEIVE_INTERVAL = 200
COLORS = ["#cc421d", "#98971a", "#d89921", "#458588", "#b16286", "#689d6a"]

def code_to_ip(code: str) -> str:
    return str(ipaddress.IPv4Address(bytes.fromhex(code)))

def randcol(sender: str) -> str:
    return f"sender{int(hashlib.sha256(sender.encode()).hexdigest(), 16) % len(COLORS)}"

class Room:
    def __init__(self, code: str) -> None:
        self.code = code
        self.name = f"guest{random.randint(0, 127)}"
        self.host = code_to_ip(code)

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, PORT))

        self.send_queue = queue.Queue()
        self.recv_queue = queue.Queue()

        self.send_queue.put(f"<- {self.name} has joined. ->")

        self.running = True

        self.send_thread = threading.Thread(target=self._send_loop, daemon=True)
        self.recv_thread = threading.Thread(target=self._recv_loop, daemon=True)

        self.send_thread.start()
        self.recv_thread.start()

    def send(self, msg: str) -> None:
        self.send_queue.put(f"{self.name}: {msg}")

    def set_name(self, name: str) -> None:
        self.send_queue.put(f"<- {self.name} has changed their name to '{name}'. ->")
        self.name = name

    def receive(self):
        try:
            return self.recv_queue.get_nowait()
        except queue.Empty:
            return None

    def leave(self) -> None:
        self.running = False

        try:
            self.send_queue.put(f"<- {self.name} has left the room. ->")
            self.send_queue.put(None)
        except Exception:
            pass

    def _send_loop(self) -> None:
        while self.running:
            try:
                msg = self.send_queue.get()
                if msg is None:
                    break

                self.sock.sendall((msg + "\n").encode("utf-8"))

            except Exception as e:
                print("failed to send:", e)
                break

    def _recv_loop(self) -> None:
        buffer = ""

        while self.running:
            try:
                data = self.sock.recv(4096)

                if not data: break

                buffer += data.decode("utf-8")

                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    if line:
                        self.recv_queue.put(line)

            except Exception as e:
                print("failed to receive:", e)
                break

        self.running = False
        try:
            self.sock.close()
        except Exception:
            pass


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()

        self.title("Wazzup!")
        self.geometry("800x600")

        self.room = None

        self.build_menubar()
        self.build_main_area()
        self.build_bottom_bar()
        self.set_style()
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.receive()

    def build_menubar(self) -> None:
        menubar = tk.Menu(self)

        menubar.add_command(label="Join", command=self.join)
        menubar.add_command(label="Leave", command=self.leave)
        menubar.add_command(label="Name", command=self.name)
        self.config(menu=menubar)

    def build_main_area(self) -> None:
        self.text = tk.Text(self, wrap="word", height=1,
            bg="#282828", borderwidth=0,
            relief="flat",
            highlightthickness=0
        )
        self.text.pack(fill="both", expand=True)
        self.text.tag_configure(
            "info",
            foreground="#928374",
            font=("Consolas", 11, "italic")
        )
        self.text.tag_configure(
            "separator",
            foreground="#928374",
            font=("Consolas", 11)
        )

        for i, c in enumerate(COLORS):
            self.text.tag_configure(
                f"sender{i}",
                foreground=c,
                font=("Consolas", 11),
            )

        self.text.tag_configure(
            "msg",
            foreground="#ebdbb2",
            font=("Consolas", 11)
        )
        self.text.config(state="disabled")

    def append_text(self, msg: str) -> None:
        self.text.config(state="normal")
        self.text.insert("end", msg + "\n")
        self.text.config(state="disabled")
        self.text.see("end")

    def build_bottom_bar(self) -> None:
        bottom = ttk.Frame(self)
        bottom.pack(fill="x", side="bottom")

        self.entry = ttk.Entry(bottom, state="disabled")
        self.entry.pack(side="left", fill="x", expand=True, padx=5, pady=5)

        self.entry.bind("<Return>", lambda e: self.send())

        self.send_btn = ttk.Button(bottom, text="Send", command=self.send, state="disabled")
        self.send_btn.pack(side="right", padx=5, pady=5)

    def set_style(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")
        self.configure(bg="#282828")

        style.configure("TFrame",
            background="#1d2021",
            borderwidth=0,
            relief="flat",
        )

        style.configure("TEntry",
            font=("Consolas", 11),
            padding=4,
            fieldbackground="#282828",
            foreground="#ebdbb2",
            borderwidth=0,
            relief="flat",
            highlightthickness=0,
        )

        style.configure("TButton",
            font=("Segoe UI", 9),
            padding=5,
            background="#3c3836",
            foreground="#ebdbb2",
        )

    def on_close(self) -> None:
        self.leave()
        self.destroy()
    
    def send(self) -> None:
        if not self.room: return

        msg = self.entry.get().rstrip() # keep leading whitespace for
                                        # ascii art :)
        if msg:
            self.room.send(msg)
            self.entry.delete(0, "end")

    def join(self) -> None:
        if self.room:
            messagebox.showerror("Leave first", "You must leave your current room first.")
            return

        code = simpledialog.askstring("Room code", "Enter a room code:")
        if not code: return
        try:
            self.room = Room(code)
        except ValueError:
            messagebox.showerror("Invalid code", "That is not a valid room code.")
            return
        except OSError:
            messagebox.showerror("Not found", "That room does not exist.")
            return

        self.entry.config(state="normal")
        self.send_btn.config(state="normal")
        pass

    def leave(self) -> None:
        if not self.room: return
        self.entry.config(state="disabled")
        self.send_btn.config(state="disabled")
        self.room.leave()
        self.room = None
        pass

    def name(self) -> None:
        if not self.room:
            messagebox.showerror("No room", "You must join a room first.")
            return
        name = simpledialog.askstring("Name", "Enter a new name:")
        if name: self.room.set_name(name)

    def receive(self) -> None:
        self.after(RECEIVE_INTERVAL, self.receive)
        if not self.room: return

        msg = None
        while (msg := self.room.receive()):
            self.text.config(state="normal")
            if msg.startswith("<- ") and msg.endswith(" ->"):
                    self.text.insert("end", "*".rjust(20), "info")
                    self.text.insert("end", SEP, "separator")
                    self.text.insert("end", msg[3:-3] + "\n", "info")
            else:
                parts = msg.split(": ")
                if len(parts) > 1:
                    sender = ": ".join(parts[:1])
                    self.text.insert("end", sender.rjust(20), randcol(sender))
                    self.text.insert("end", SEP, "separator")
                    self.text.insert("end", ": ".join(parts[1:]) + "\n", "msg")
            self.text.config(state="disabled")
            self.text.see("end")

if __name__ == "__main__":
    App().mainloop()
