from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
 # Import delle eccezioni personalizzate
from CustomExceptions import CustomExceptions

import sys
import time



class ChatServer:
    #funzione di inizializzazione del server 
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.buffer_size = 1024
        self.address = (self.host, self.port)
        # Inizializzazione dei dizionari per i client e i loro indirizzi
        self.clients = []
        self.names = []
        self.threads = []
        # Creazione del socket del Server
        self.server_socket = socket(AF_INET, SOCK_STREAM)
        
        self.handle_thread = True
        self.receive_thread= True

    def start(self):
        try:
            # Legame del socket del Server con il suo address
            self.server_socket.bind(self.address)
            # Il server inizia ad ascoltare le connessioni in entrata (fino a 5 in coda)
            self.server_socket.listen(5)
            print("[SERVER] In attesa di connessioni...")
            # Creazione e avvio del thread per accettare le connessioni in entrata
            accept_thread = Thread(target=self.receive_connections)
            accept_thread.start()
            self.threads.append(accept_thread)
            
        except OSError as e:
            print(CustomExceptions.OS_ERROR + str(e))

        while True :
            try:
                time.sleep(5)
                print("server in azione")
            except KeyboardInterrupt:
                print("prova")
                self.shutdown_server()


    # funzione che gestisce le richieste di connessione
    def receive_connections(self):
        while self.receive_thread:
            try:
                # Accettazione di  una connessione da un Client
                client_socket, client_address = self.server_socket.accept()
                print("Si è collegato al server", client_address)
                #al client che si connette per la prima volta fornisce alcune indicazioni di utilizzo
                client_socket.send(bytes("Salve! Digita il tuo Nome seguito dal tasto Invio!", "utf8"))
                
                # Memorizzazione dell'indirizzo del client
                
                self.clients.append(client_socket)
                
                # Creazione e avvio di un thread per gestire il client
                clientThread = Thread(target=self.handle_client, args=(client_socket,))
                clientThread.start()
                self.threads.append(clientThread)
            except ConnectionResetError as e:
                # Stampa di errore
                print("Tentativo di ricezione su socket precedentemente chiusa, terminazione dell'handle thread in corso ...",e)
                # Interruzione del ciclo
                break
            except OSError as e:
                print("Thread Server terminato da linea di comando")
                break
            except Exception as e:
                print("[ERRORE] Impossibile accettare la connessione:", e)
                break
            
            

    def handle_client(self, client_socket):

        try:
            name = client_socket.recv(1024).decode("utf-8")
            self.names.append(name)
            welcome_message = 'Benvenuto %s! Se vuoi lasciare la Chat, scrivi {quit} per uscire.' % name
            client_socket.send(bytes(welcome_message, "utf8"))
            msg = "%s si è unito alla chat!" % name
            self.broadcast(bytes(msg, "utf8"))
            

            while self.handle_thread:
                try:
                    # Ricezione di un messaggio dal client
                    msg = client_socket.recv(self.buffer_size)
                    #se il messaggio ricevuto è diverso da quit
                    if msg != bytes("{quit}", "utf8"):
                        self.broadcast(msg, name+": ")
                    else:
                        #se il messaggio è uguale a quit
                        self.delete_client(client_socket,name)
                        # Interruzione del ciclo
                        break
                except ConnectionResetError as e:
                    print(CustomExceptions.CONNECTION_RESET_ERROR + str(e))
                    break
                except ConnectionAbortedError as e:
                    print(CustomExceptions.CONNECTION_ABORTED_ERROR + str(e))
                    break
                except UnicodeDecodeError as e:
                    print(CustomExceptions.UNICODE_DECODE_ERROR + str(e))
                    break
                except KeyError as e:
                    print(CustomExceptions.KEY_ERROR + str(e))
                    break

        except OSError as e:
            print(CustomExceptions.OS_ERROR + str(e))

    
    # FUNZIONE DI DISCONNESSIONE DEL CLIENT
    def delete_client(self,client_socket,name):
        try:
            
            # Invio del messaggio di quit al Client (per dirgli di abbandonare la chat)
            client_socket.send(bytes("{quit}", "utf8"))
            #eliminiamo il client dalla lista
            self.clients.remove(client_socket)
            self.names.remove(name)
            #chiudiamo la socket relativa a quel client
            #client_socket.close()
            #invio a tutti i client restanti il messaggio che il client ha abbandonato la chat
            self.broadcast(bytes("%s ha abbandonato la Chat." % name, "utf8"))
            print("%s ha abbandonato la Chat." % name)
            print("persone rimaste :")
            for name in self.names:
                print(" ",name)
        
        # Gestione del tentativo di invio di un messaggio su un socket chiuso
        except ConnectionResetError:
            # Stampa di avviso
            print("Azione non andata a buon fine perchè la socket è gia stata chiusa")


    def broadcast(self, msg, prefix=""):
        for client_socket in self.clients:
            try:
                # Invio del messaggio a tutti i client connessi
                client_socket.send(bytes(prefix, "utf8")+msg)
            except OSError as e:
                print(CustomExceptions.OS_ERROR + str(e))
    
    
    def shutdown_server(self):
        
        
        # Notificare tutti i client connessi e chiudere le loro connessioni
        for client in list(self.clients):
            try:
                client.send(bytes("{quit}", "utf8"))
                
            except OSError as e:
                print(CustomExceptions.OS_ERROR + str(e))
        
        print("Tutti i client sono stati disconnessi")

        # Svuotare le liste dei client e dei nomi
        self.clients.clear()
        self.names.clear()

        self.handle_thread=False
        self.receive_thread=False

         # Chiudere il server socket per interrompere il loop di accettazione
        try:
            self.server_socket.close()
        except OSError as e:
            print(CustomExceptions.OS_ERROR + str(e))

        print("Server disconnesso")

        ## Attendere la terminazione dei thread
        for thread in self.threads:
            try:
                
                thread.join()
                print("thread rimosso",thread)
            except RuntimeError as e:
                print("[ERRORE] Impossibile terminare il thread:", e)

       

        sys.exit(0)

          
if __name__ == "__main__":
    #Creazione del server tramite il proprio costruttore (funzione _init_)
    server = ChatServer('localhost', 8080)
    #Chiama la funzione per mettere il server in ascolto
    server.start()
    




