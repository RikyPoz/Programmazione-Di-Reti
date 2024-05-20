#!/usr/bin/env python3

from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import tkinter as tk
import sys
from CustomExceptions import CustomExceptions



BUFFER_SIZE = 1024

class ChatClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.address = (self.host, self.port)
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.gui = tk.Tk()
        self.gui.title("Chat")
        self.build_interface()
        self.setup_socket()
        self.start_receiving_thread()
        

    def build_interface(self):
        frame = tk.Frame(self.gui)
        self.message_var = tk.StringVar()
        self.message_var.set("Scrivi qui i tuoi messaggi.")
        scrollbar = tk.Scrollbar(frame)
        self.message_list = tk.Listbox(frame, height=15, width=50, yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.message_list.pack(side=tk.LEFT, fill=tk.BOTH)
        frame.pack()
        entry_field = tk.Entry(self.gui, textvariable=self.message_var)
        entry_field.bind("<Return>", self.send_message)
        entry_field.pack()
        send_button = tk.Button(self.gui, text="Invio", command=self.send_message)
        send_button.pack()
        self.gui.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_socket(self):
        try:
            self.socket.connect(self.address)
        except ConnectionRefusedError as e:
            print(CustomExceptions.CONNECTION_REFUSED_ERROR + str(e))
            exit(0)
        except OSError as e:
            print(CustomExceptions.OS_ERROR + e)
            exit(1)
        except Exception as e:
            print(CustomExceptions.GENERAL_CONNECTION_ERROR + str(e))
            exit(1)

    def start_receiving_thread(self):
        receive_thread = Thread(target=self.receive_messages)
        receive_thread.daemon = True
        receive_thread.start()

    def receive_messages(self):
        
        while True:
            try:
                message = self.socket.recv(BUFFER_SIZE).decode("utf8")
                print(message)
                if message:
                    self.message_list.insert(tk.END, message)
                    if message == "{quit}":
                        print("Disconnessione in corso a causa della chiusura del Server ...")
                        self.socket.close()
                        self.gui.quit()
                        break

                else:
                    raise ConnectionError
            except ConnectionResetError as e:
                print(CustomExceptions.CONNECTION_RESET_ERROR + str(e))
                print("1")
                self.socket.close()
                break
            except OSError as e:
                print(CustomExceptions.RECEIVE_OS_ERROR + str(e))
                print("2")
                exit(0)
                
                
            except Exception as e:
                print(CustomExceptions.GENERAL_RECEIVE_ERROR + str(e))
                print("3")
                exit(0)
        
        
    

    def send_message(self, event=None):
        message = self.message_var.get()
        self.message_var.set("")
        try:
            self.socket.sendall(bytes(message, "utf8"))
            if message == "{quit}":
                self.socket.close()
                self.gui.quit()
                
        except BrokenPipeError as e:
            print(CustomExceptions.BROKEN_PIPE_ERROR + str(e))
            self.socket.close()
            self.gui.quit()
        except Exception as e:
            print(CustomExceptions.GENERAL_SEND_ERROR + str(e))
            self.socket.close()
            self.gui.quit()

    def on_closing(self, event=None):
        self.message_var.set("{quit}")
        self.send_message()

if __name__ == "__main__":
    host = 'localhost'
    port = 8080

    client = ChatClient(host, port)
    tk.mainloop()
