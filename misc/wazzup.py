from tkinter import simpledialog
from tkinter import messagebox
import tkinter as tk
import ipaddress
import threading
import socket
import random
import queue

PORT = 5499
RECEIVE_INTERVAL = 200

def code_to_ip(code: str) -> str:
    return str(ipaddress.IPv4Address(bytes.fromhex(code)))

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

    def receive(self, block=True, timeout=None):
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

        self.receive()

    def build_menubar(self) -> None:
        menubar = tk.Menu(self)

        menubar.add_command(label="Join", command=self.join)
        menubar.add_command(label="Leave", command=self.leave)
        menubar.add_command(label="Name", command=self.name)
        self.config(menu=menubar)

    def build_main_area(self) -> None:
        self.text = tk.Text(self, wrap="word")
        self.text.pack(fill="both", expand=True)
        self.text.tag_configure(
            "info",
            foreground="gray",
            font=("Courier", 11, "italic")
        )
        self.text.tag_configure(
            "msg",
            foreground="black",
            font=("Courier", 11)
        )

        self.text.config(state="disabled")

    def append_text(self, msg: str) -> None:
        self.text.config(state="normal")
        self.text.insert("end", msg + "\n")
        self.text.config(state="disabled")
        self.text.see("end")

    def build_bottom_bar(self) -> None:
        bottom = tk.Frame(self)
        bottom.pack(fill="x", side="bottom")

        self.entry = tk.Entry(bottom, state="disabled")
        self.entry.pack(side="left", fill="x", expand=True, padx=5, pady=5)

        self.entry.bind("<Return>", lambda e: self.send())

        self.send_btn = tk.Button(bottom, text="Send", command=self.send, state="disabled")
        self.send_btn.pack(side="right", padx=5, pady=5)

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
            if msg.startswith("<- "):
                self.text.insert("end", " " * 20 + " | " + msg[3:-3] + "\n", "info")
            else:
                parts = msg.split(": ")
                if len(parts) > 1:
                    self.text.insert("end", ": ".join(parts[:1]).rjust(20) + " | ", "info")
                    self.text.insert("end", ": ".join(parts[1:]) + "\n", "msg")
                else:
                    self.text.insert("end", msg + "\n", "msg")
                self.text.config(state="disabled")
                self.text.see("end")

if __name__ == "__main__":
    App().mainloop()
