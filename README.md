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

### Usage Example
<b> V Starting casey_listener on the attacker machine V </b>  
![CaseyListener_Started](https://user-images.githubusercontent.com/83319068/163905544-5d4c0471-07fb-4ce4-ad10-3ea35d547ac9.png)

<b> V Starting casey_agent on the target machine (victim) & Obtaining a shell V </b>  
![CaseyAgent_Started](https://user-images.githubusercontent.com/83319068/163905769-cb6b4eb5-fe1c-4ad1-9a1c-1fd14640a848.png)  
![CaseyListener_Connected](https://user-images.githubusercontent.com/83319068/163905927-f0f8e936-6e0e-4852-8057-fbf5316b21ad.png)

<b> V File Upload V </b>  
![Casey_UploadTest](https://user-images.githubusercontent.com/83319068/163906045-4380c65f-ec92-418b-a51e-aea1a5cba62c.png)

<b> V File Download V </b>  
![Casey_DownloadTest](https://user-images.githubusercontent.com/83319068/163906072-2985cc60-092b-4579-9829-c517acb9c8d3.png)
