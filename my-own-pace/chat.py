import socket

# TODO: wrap this in some kinda tkinter gui
# OTHER TODO: add concurrency so that you can send multiple messages in a row

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

def main() -> None:
    backend = ChatBackend()
    
    
    expect_convo = (input("are you waiting for someone to join? [Y/n] ")
                    .strip() + " ")[0].lower() != "n"                
    if expect_convo:
        print(f"your ip: {backend.ip}")
        backend.expect_convo()
        print("connected!\n")
    else:
        ip = "192.168.1.114" # input("who would you like to connect to? ")
        try:
            backend.start_convo(ip)
        except ConnectionRefusedError:
            print("no one is waiting for you there :(")
            return
        
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
        
if __name__ == "__main__":
    main()