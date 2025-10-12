import socket
import threading
from sys import argv
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
        
        if msg == END:
            self.convo.close()
            self.convo = None
            return None
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
        s.connect(("8.8.8.8", 80)) # google dns
        self.ip = s.getsockname()[0]
        s.close()
        
class GuiFrontend:
    def __init__(self, backend):
        self.root = tk.Tk()
        self.backend = backend

        self.root.title("Tkinter Chat")
        self.root.minsize(100, 550)

        self.chat_area = scrolledtext.ScrolledText(self.root, state='disabled', wrap='word')
        self.chat_area.tag_config("user", foreground="green", font=("Helvetica", 10, "bold"))
        self.chat_area.tag_config("them", foreground="blue", font=("Helvetica", 10, "bold"))
        self.chat_area.tag_config("system", foreground="darkgray", font=("Helvetica", 10, "italic"))
        self.chat_area.pack(expand=True, fill='both', padx=5, pady=5)

        self.entry = tk.Entry(self.root)
        self.entry.pack(side='left', fill='x', expand=True, padx=5, pady=5)
        self.entry.bind("<Return>", lambda e: self.send_message())

        self.send_button = tk.Button(self.root, text="Send", command=self.send_message)
        self.send_button.pack(side='right', padx=5, pady=5)

        self.start_connection()

    def start_connection(self):
        choice = messagebox.askyesno("Join Someone",
                                     "Would you like to join an existing chat?")
        if not choice:
            self.log(f"Room code: {self.backend.ip}\nWaiting for somone to join...")
            threading.Thread(target=self.wait_for_connection, daemon=True).start()
        else:
            ip = simpledialog.askstring("Connect", "Enter a room code:")
            if not ip:
                self.root.destroy()
                return
            try:
                self.backend.start_convo(ip)
                self.log(f"Joined {ip}...\n")
                self.log("Send 'cya' to leave the chat.\n")
                threading.Thread(target=self.listen_for_messages, daemon=True).start()
            except ConnectionRefusedError:
                messagebox.showerror("Not found", "That room could not be found.")
                self.root.destroy()

    def wait_for_connection(self):
        self.backend.expect_convo()
        self.log(f"Someone has joined!\n")
        self.log("Send 'cya' to leave the chat.\n")
        threading.Thread(target=self.listen_for_messages, daemon=True).start()

    def listen_for_messages(self):
        while True:
            try:
                msg = self.backend.expect_message()
                if msg is None:
                    self.log(f"cya", "them")
                    self.log(f"\nThe chat has been closed.")
                    self.send_button.config(state=tk.DISABLED)
                    self.entry.config(state=tk.DISABLED)
                    break
                self.log(f"{msg}", "them")
            except Exception as e:
                self.log(f"Error: {e}")
                break

    def send_message(self):
        if self.backend.convo is None: return
        
        msg = self.entry.get().strip()
        if not msg:
            return
        self.entry.delete(0, tk.END)
        if msg.lower() == "cya":
            self.backend.end_convo()
            self.root.destroy()
            return
        
        self.log(f"{msg}", "user")
        self.backend.send_message(msg)
            

    def log(self, text=str, tag: str="system") -> None:
        self.chat_area.config(state='normal')
        if tag is not None:
            self.chat_area.insert(tk.END, text + "\n", tag)
        else:
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
    if len(argv) > 1 and (argv[1] == "--cli" or argv[1] == "-c"):
        cli_frontend()
    else:
        main()