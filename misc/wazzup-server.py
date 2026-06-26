import threading
import ipaddress
import socket
import base64

HOST = "0.0.0.0"
PORT = 5499

clients = set()
clients_lock = threading.Lock()

# hex version of an ip address
def ip_to_code(ip: str) -> str:
    return ipaddress.IPv4Address(ip).packed.hex()

# we have to connect to someone else to get the ip for some reason
def get_local_ip() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    finally:
        s.close()

# send a message to all the clients, like an ip broadcast
def broadcast(message: bytes) -> None:
    dead = []

    with clients_lock:
        for sock in clients:
            try:
                sock.sendall(message + b"\n")
            except OSError:
                pass

        for sock in dead:
            clients.discard(sock)


# spawn a new thread for a connected client
def handle_client(sock: socket.socket, addr: str) -> None:
    print(f"{addr[0]} connected.")

    with clients_lock:
        clients.add(sock)

    try:
        with sock.makefile("rb") as f:
            for line in f:
                print(line.decode("utf-8"))
                broadcast(line)

    except Exception as e:
        print(f"{addr}: {e}")

    finally:
        with clients_lock:
            clients.discard(sock)

        sock.close()
        print(f"{addr[0]} left.")


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen()

        print(f"room created with code: {ip_to_code(get_local_ip())}")

        while True:
            sock, addr = server.accept()

            threading.Thread(
                target=handle_client,
                args=(sock, addr),
                daemon=True,
            ).start()


if __name__ == "__main__":
    main()
