#!/usr/bin/env python3

from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import tkinter as tk
import sys
from CustomExceptions import CustomExceptions

# Dimensione del buffer per la ricezione dei messaggi
BUFFER_SIZE = 1024

class ChatClient:
    def __init__(self, host, port):
        # Inizializzazione delle variabili di istanza
        self.host = host
        self.port = port
        self.address = (self.host, self.port)
        
        # Creazione della socket
        self.socket = socket(AF_INET, SOCK_STREAM)
        
        # Creazione dell'interfaccia grafica
        self.gui = tk.Tk()
        self.gui.title("Chat")
        
        # Costruzione dell'interfaccia utente
        self.build_interface()
        
        # Configurazione della connessione socket
        self.setup_socket()
        
        # Avvio del thread per ricevere i messaggi
        self.start_receiving_thread()

    def build_interface(self):
        # Creazione del frame principale
        frame = tk.Frame(self.gui)
        
        # Variabile per il messaggio di input
        self.message_var = tk.StringVar()
        self.message_var.set("Scrivi qui i tuoi messaggi.")
        
        # Creazione della barra di scorrimento
        scrollbar = tk.Scrollbar(frame)
        
        # Creazione della lista per visualizzare i messaggi
        self.message_list = tk.Listbox(frame, height=15, width=50, yscrollcommand=scrollbar.set)
        
        # Configurazione della barra di scorrimento
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.message_list.pack(side=tk.LEFT, fill=tk.BOTH)
        frame.pack()
        
        # Campo di input per i messaggi
        entry_field = tk.Entry(self.gui, textvariable=self.message_var)
        
        # Associa il tasto Invio all'invio del messaggio
        entry_field.bind("<Return>", self.send_message)
        entry_field.pack()
        
        # Bottone per inviare i messaggi
        send_button = tk.Button(self.gui, text="Invio", command=self.send_message)
        send_button.pack()
        
        # Definisce l'azione da intraprendere quando la finestra viene chiusa
        self.gui.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_socket(self):
        try:
            # Tentativo di connessione al server
            self.socket.connect(self.address)
        except ConnectionRefusedError as e:
            # Gestione dell'errore di connessione rifiutata
            print(CustomExceptions.CONNECTION_REFUSED_ERROR + str(e))
            exit(0)
        except OSError as e:
            # Gestione di errori generici del sistema operativo
            print(CustomExceptions.OS_ERROR + e)
            exit(1)
        except Exception as e:
            # Gestione di errori generali di connessione
            print(CustomExceptions.GENERAL_CONNECTION_ERROR + str(e))
            exit(1)

    def start_receiving_thread(self):
        # Creazione e avvio di un thread per ricevere i messaggi dal server
        receive_thread = Thread(target=self.receive_messages)
        receive_thread.daemon = True
        receive_thread.start()

    def receive_messages(self):
        # Ciclo infinito per ricevere i messaggi dal server
        while True:
            try:
                # Ricezione del messaggio dal server
                message = self.socket.recv(BUFFER_SIZE).decode("utf8")
                print(message)
                if message:
                    # Inserimento del messaggio nella lista dei messaggi
                    self.message_list.insert(tk.END, message)
                    if message == "{quit}":
                        print("Abbandono della chat....")
                        # Chiusura della connessione se il messaggio è "{quit}"
                        self.socket.close()
                        self.gui.quit()
                        break
                else:
                    # Gestione del caso in cui la connessione viene chiusa dal server
                    raise ConnectionError
            except ConnectionResetError as e:
                # Gestione dell'errore di reset della connessione
                print(CustomExceptions.CONNECTION_RESET_ERROR + str(e))
                self.socket.close()
                break
            except OSError as e:
                # Gestione di errori generici del sistema operativo durante la ricezione
                print(CustomExceptions.RECEIVE_OS_ERROR + str(e))
                exit(0)
            except Exception as e:
                # Gestione di errori generali durante la ricezione
                print(CustomExceptions.GENERAL_RECEIVE_ERROR + str(e))
                exit(0)

    def send_message(self, event=None):
        # Ottenimento del messaggio dall'input
        message = self.message_var.get()
        self.message_var.set("")
        try:
            # Invio del messaggio al server
            self.socket.sendall(bytes(message, "utf8"))
            
        except BrokenPipeError as e:
            # Gestione dell'errore di rottura della pipe
            print(CustomExceptions.BROKEN_PIPE_ERROR + str(e))
            self.socket.close()
            self.gui.quit()
        except Exception as e:
            # Gestione di errori generali durante l'invio
            print(CustomExceptions.GENERAL_SEND_ERROR + str(e))
            self.socket.close()
            self.gui.quit()

    def on_closing(self, event=None):
        # Azione da intraprendere quando la finestra viene chiusa
        self.message_var.set("{quit}")
        self.send_message()

if __name__ == "__main__":
    # Richiesta della Server Ip
    serverHost = input("Inserisci server host:")
    # Richiesta della Server port
    serverPort = int(input("Inserisci server port:"))

    # Creazione di un'istanza di ChatClient e avvio del loop principale di tkinter
    client = ChatClient(serverHost, serverPort)
    tk.mainloop()