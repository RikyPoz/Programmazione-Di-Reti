from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
# Import delle eccezioni personalizzate
from CustomExceptions import CustomExceptions

import sys
import time


class ChatServer:
    # Funzione di inizializzazione del server
    def __init__(self, host, port):
        # Inizializzazione dei valori necessari per la creazione del socket
        self.host = host
        self.port = port
        self.buffer_size = 1024
        self.address = (self.host, self.port)
        # Liste per memorizzare i client e i loro nomi
        self.clients = []
        self.names = []
        self.threads = []
        # Creazione del socket del server
        self.server_socket = socket(AF_INET, SOCK_STREAM)
        # Flag utilizzati per interrompere i thread in esecuzione
        self.handleThread_flag = True
        self.receiveThread_flag = True

    def start(self):
        try:
            # Binding del socket del server con il suo indirizzo
            self.server_socket.bind(self.address)
            # Il server inizia ad ascoltare le connessioni in entrata (fino a 5 in coda)
            self.server_socket.listen(5)
            print("[SERVER] In attesa di connessioni...")
            # Creazione e avvio del thread per accettare le connessioni in entrata
            accept_thread = Thread(target=self.receive_connections)
            accept_thread.start()
            self.threads.append(accept_thread)
        except OSError as e:
            print(CustomExceptions.OS_ERROR + str(e) + "start")

        while True:
            try:
                #Ogni 5 secondi viene notificato che il server è ancora attivo
                time.sleep(5)
                print("server in azione")
            except KeyboardInterrupt:
                #Eccezione che viene gestita quando il server viene terminato tramite CTRL+C
                self.shutdown_server()

    # Funzione che gestisce le richieste di connessione
    def receive_connections(self):
        while self.receiveThread_flag:
            try:
                # Accettazione di una connessione da un client
                client_socket, client_address = self.server_socket.accept()
                print("Si è collegato al server", client_address)
                # Invia al client un messaggio di benvenuto con istruzioni
                client_socket.send(bytes("Salve! Digita il tuo Nome seguito dal tasto Invio!", "utf8"))
                
                # Memorizzazione del client
                self.clients.append(client_socket)
                
                # Creazione e avvio di un thread per gestire il client
                clientThread = Thread(target=self.handle_client, args=(client_socket,))
                clientThread.start()
                self.threads.append(clientThread)
            except BrokenPipeError as e:
                print(CustomExceptions.BROKEN_PIPE_ERROR + str(e))
                break
            except OSError as e:
                print("Thread Server terminato da linea di comando")
                break
            except Exception as e:
                print("[ERRORE] Impossibile accettare la connessione:", e)
                break

    # Funzione per gestire le comunicazioni con un client specifico
    def handle_client(self, client_socket):
        try:
            # Ricezione del nome del client
            name = client_socket.recv(1024).decode("utf-8")
            self.names.append(name)
            # Invio del messaggio di benvenuto al nuovo client
            welcome_message = 'Benvenuto %s! Se vuoi lasciare la Chat, scrivi {quit} per uscire.' % name
            client_socket.send(bytes(welcome_message, "utf8"))
            msg = "%s si è unito alla chat!" % name
            self.broadcast(bytes(msg, "utf8"))

            while self.handleThread_flag:
                try:
                    # Ricezione di un messaggio dal client
                    msg = client_socket.recv(self.buffer_size)
                    # Se il messaggio ricevuto è diverso da "{quit}"
                    if msg != bytes("{quit}", "utf8"):
                        self.broadcast(msg, name + ": ")
                    else:
                        # Se il messaggio è uguale a "{quit}", disconnetti il client
                        self.delete_client(client_socket, name)
                        break
                except UnicodeDecodeError as e:
                    print(CustomExceptions.UNICODE_DECODE_ERROR + str(e))
        
        except ConnectionResetError as e:
                    print(CustomExceptions.CONNECTION_RESET_ERROR + str(e))
                    self.clients.remove(client_socket)
                    self.names.remove(name)
        except ConnectionAbortedError as e:
                    print(CustomExceptions.CONNECTION_ABORTED_ERROR + str(e))
                    self.clients.remove(client_socket)
                    self.names.remove(name)
        except OSError as e:
                    print(CustomExceptions.OS_ERROR + str(e))
                    self.clients.remove(client_socket)
                    self.names.remove(name)
                   


    # Funzione per disconnettere un client
    def delete_client(self, client_socket, name):
        try:
            # Invio del messaggio di quit al client
            client_socket.send(bytes("{quit}", "utf8"))
            # Rimuove il client dalla lista dei client connessi
            self.clients.remove(client_socket)
            self.names.remove(name)
            # Chiude la socket del client
            #client_socket.close()

            # Invia un messaggio a tutti i client rimanenti per notificare che un client ha lasciato la chat
            self.broadcast(bytes("%s ha abbandonato la Chat." % name, "utf8"))
            print("%s ha abbandonato la Chat." % name)
        
            #Stampa una lista di tutti i client connessi  
            print("Persone rimaste:")
            for name in self.names:
                print(" ", name)
                
        except BrokenPipeError as e:
                print(CustomExceptions.BROKEN_PIPE_ERROR + str(e))

    # Funzione per inviare un messaggio a tutti i client connessi
    def broadcast(self, msg, prefix=""):
        for client_socket in self.clients:
            try:
                # Invio del messaggio a tutti i client connessi
                client_socket.send(bytes(prefix, "utf8") + msg)
            except BrokenPipeError as e:
                print(CustomExceptions.BROKEN_PIPE_ERROR + str(e)+"broadcast")
            
            

    # Funzione per chiudere il server
    def shutdown_server(self):
        # Notifica tutti i client connessi e chiude le loro connessioni
        for client in list(self.clients):
            try:
                client.send(bytes("{quit}", "utf8"))
            except BrokenPipeError as e:
                print(CustomExceptions.BROKEN_PIPE_ERROR + str(e)+"broadcast")
            
        print("Tutti i client sono stati disconnessi")

        # Svuota le liste dei client e dei nomi
        self.clients.clear()
        self.names.clear()

        # Imposta i flag per interrompere i thread
        self.handleThread_flag = False
        self.receiveThread_flag = False

        # Chiude il server socket per interrompere il loop di accettazione
        try:
            self.server_socket.close()
        except OSError as e:
            print(CustomExceptions.OS_ERROR + str(e)+"close server socket")

        print("Server disconnesso")

        # Attende la terminazione dei thread
        for thread in self.threads:
            try:
                thread.join()
                print("Thread rimosso", thread)
            except RuntimeError as e:
                print("[ERRORE] Impossibile terminare il thread:", e)

        sys.exit()


if __name__ == "__main__":
    # Richiesta della Server Ip
    serverHost = input("Inserisci server host:")
    # Richiesta della Server port
    serverPort = int(input("Inserisci server port:"))
    # Creazione del server tramite il costruttore (funzione __init__)
    server = ChatServer(serverHost, serverPort)
    # Chiama la funzione per mettere il server in ascolto
    server.start()
