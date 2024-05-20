class CustomExceptions:
    # Messaggio di errore per quando la connessione al server viene rifiutata.
    CONNECTION_REFUSED_ERROR = "[!] Connessione rifiutata dal server."
    
    # Messaggio di errore per un errore di sistema generico relativo alle operazioni di socket.
    OS_ERROR = "[!] Errore di sistema:"
    
    # Messaggio di errore per problemi generici durante il tentativo di connessione al server.
    GENERAL_CONNECTION_ERROR = "[!] Errore durante la connessione al server:"
    
    # Messaggio di errore per quando la connessione viene resettata in modo imprevisto dal server.
    CONNECTION_RESET_ERROR = "[!] Connessione persa: il server ha resettato la connessione."
    
    # Messaggio di errore specifico per problemi durante la ricezione dei messaggi dal server.
    RECEIVE_OS_ERROR = "[!] Errore durante la ricezione del messaggio."
    
    # Messaggio di errore per errori generali durante la ricezione dei messaggi.
    GENERAL_RECEIVE_ERROR = "[!] Errore durante la ricezione del messaggio:"
    
    # Messaggio di errore per quando si tenta di inviare un messaggio su un socket che è già stato chiuso.
    BROKEN_PIPE_ERROR = "[!] Errore: tentativo di inviare un messaggio su un socket chiuso."
    
    # Messaggio di errore per errori generici durante l'invio dei messaggi.
    GENERAL_SEND_ERROR = "[!] Errore durante l'invio del messaggio:"
    
    # (Duplicato) Messaggio di errore per quando la connessione viene resettata in modo imprevisto.
    CONNECTION_RESET_ERROR = "[ERRORE] Connessione resettata in modo imprevisto:"
    
    # Messaggio di errore per quando la connessione viene interrotta in modo imprevisto.
    CONNECTION_ABORTED_ERROR = "[ERRORE] Connessione interrotta in modo imprevisto:"
    
    # Messaggio di errore per quando non è possibile decodificare un messaggio ricevuto.
    UNICODE_DECODE_ERROR = "[ERRORE] Impossibile decodificare il messaggio:"
    
    # Messaggio di errore per quando una chiave non viene trovata nel dizionario.
    KEY_ERROR = "[ERRORE] Chiave non trovata nel dizionario:"

