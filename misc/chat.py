import socket
import threading
import tkinter as tk
from tkinter import simpledialog, scrolledtext, messagebox

PORT = 5556
END = "---< this convo is over >---"

class ChatBackend:
    def __init__(self):
        self.grab_local_ip()
        self.convo = None
        
    def send_message(self, msg: str) -> None:
        if self.convo is None:
            raise ConnectionError("There is no current conversation.")
        
        self.convo.sendall(msg.encode())
        
    def end_convo(self) -> None:
        self.send_message(END)
        self.convo.close()
        self.convo = None
        
    def expect_message(self) -> str|None:
        if self.convo is None:
            raise ConnectionError("There is no current conversation.")
        
        data = self.convo.recv(1024)
        msg = data.decode()
        
        if msg == END: return None
        return msg
        
    def start_convo(self, ip: str) -> None:
        self.convo = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.convo.connect((ip, PORT))
        self.target = ip
        
    def expect_convo(self) -> None:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("0.0.0.0", PORT))
        s.listen(1)

        self.convo, recipient = s.accept()
        self.target = recipient[0]
        
    def grab_local_ip(self) -> None:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        self.ip = s.getsockname()[0]
        s.close()
        
class GuiFrontend:
    def __init__(self, backend):
        self.root = tk.Tk()
        self.backend = backend

        self.root.title("Tkinter Chat")
        self.root.minsize(100, 550)

        self.chat_area = scrolledtext.ScrolledText(self.root, state='disabled', wrap='word')
        self.chat_area.pack(expand=True, fill='both', padx=5, pady=5)

        self.entry = tk.Entry(self.root)
        self.entry.pack(side='left', fill='x', expand=True, padx=5, pady=5)
        self.entry.bind("<Return>", lambda e: self.send_message())

        self.send_button = tk.Button(self.root, text="Send", command=self.send_message)
        self.send_button.pack(side='right', padx=5, pady=5)

        self.start_connection()

    def start_connection(self):
        choice = messagebox.askyesno("Connection", "Start a new chat?")
        if choice:
            self.log(f"Room code: {self.backend.ip}\nWaiting for somone to join...")
            threading.Thread(target=self.wait_for_connection, daemon=True).start()
        else:
            ip = simpledialog.askstring("Connect", "Enter a room code:")
            if not ip:
                self.root.destroy()
                return
            try:
                self.backend.start_convo(ip)
                self.log(f"Connected to {ip}")
                threading.Thread(target=self.listen_for_messages, daemon=True).start()
            except ConnectionRefusedError:
                messagebox.showerror("Error", "That is not a room.")
                self.root.destroy()

    def wait_for_connection(self):
        self.backend.expect_convo()
        self.log(f"Connected by {self.backend.target}")
        threading.Thread(target=self.listen_for_messages, daemon=True).start()

    def listen_for_messages(self):
        while True:
            try:
                msg = self.backend.expect_message()
                if msg is None:
                    self.log(f"{self.backend.target} left the chat.")
                    break
                self.log(f"{self.backend.target} -> {msg}")
            except Exception as e:
                self.log(f"Connection closed: {e}")
                break

    def send_message(self):
        msg = self.entry.get().strip()
        if not msg:
            return
        self.log(f"You -> {msg}")
        self.backend.send_message(msg)
        self.entry.delete(0, tk.END)
        if msg.lower() == "cya":
            self.backend.end_convo()
            self.log("You left the chat.")
            return

    def log(self, text):
        self.chat_area.config(state='normal')
        self.chat_area.insert(tk.END, text + "\n")
        self.chat_area.config(state='disabled')
        self.chat_area.yview(tk.END)
        
    def start(self):
        self.root.mainloop()

def cli_frontend() -> None:
    backend = ChatBackend()
    
    expect_convo = (input("are you waiting for someone to join? [Y/n] ")
                    .strip() + " ")[0].lower() != "n"                
    if expect_convo:
        print(f"your ip: {backend.ip}")
        backend.expect_convo()
        print(f"{backend.target} has connected!\n")
    else:
        ip = input("who would you like to connect to? ")
        try:
            backend.start_convo(ip)
        except ConnectionRefusedError:
            print("no one is waiting for you there :(")
            return
        print("")
        
    if expect_convo:
        print(f"      -> {backend.expect_message()}")
    while True:
        send = input("send  <- ")
        if send == "cya":
            backend.end_convo()
            break
        backend.send_message(send)
        
        reply = backend.expect_message()
        if reply is None:
            print(f"reply -> cya ({backend.target} left the chat)")
            break
        print(f"reply -> {reply}")
    
def main() -> None:
    backend = ChatBackend()
    gui = GuiFrontend(backend)
    gui.start()
        
if __name__ == "__main__":
    main()