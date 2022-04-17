# ReverseShell  

## Description
A custom reverse shell program written in Python.  
There are two programs: `casey_listenr.py` and`casey_agent.py`.  

### casey_listener
casey_listener is a program that listens for incoming connection. It sends commands to casey_agent, and recieves the command results sent from casey_agent.  

### casey_agent
casey_agent is a program that get's stored in the target machine. It recieves the commands from casey_listener, executes the commands on the target machine, and sends the result to casey_listener.  

So far, they can be used to execute commands, download and upload files.  
Tested on Windows 10, and the programs are still in development.  
This is to be used for educational and security testing purposes only and I'm not responsible for the misuse of this program.  

### Usage  
1. Transfer casey_agent to the target machine.  
2. Start casey_listener on the attacker machine and enter the IP address of attacker machine and port number to accept connection.  
  `python3 casey_listener.py`  
3. Start casey_agent on the target machine.  
  `python3 casey_agent.py` 
