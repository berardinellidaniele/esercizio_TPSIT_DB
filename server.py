import socket
import threading
from db import Database
from Ordine import Ordine
from validazione import valida_stringa, valida_integer, valida_float

conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=10.100.1.251;"
    "DATABASE=Corso C;"
    "Trusted_Connection=yes;"
)

def gestisci_client(conn, addr):
    print(f"[nuova connessione] {addr}")
    local_db = Database(conn_str)

    buffer = []
    ordine_multiplo = False
    cliente_nome = ""
    cliente_cognome = ""
    pagato = 0.0

    try:
        while True:
            data = conn.recv(1024).decode()
            if not data:
                break

            righe = data.strip().split("\n")
            for riga in righe:
                if riga.startswith("SCELTA"):
                    scelta = riga.strip().split()[1].upper()
                    ordine_multiplo = (scelta == "MULTIPLO")
                    buffer.clear()

                elif riga.startswith("CLIENTE"):
                    parti = riga.strip().split()
                    if len(parti) < 2:
                        conn.sendall("errore client non valido\n".encode())
                        return
                    cliente_nome = parti[1]
                    cliente_cognome = parti[2] if len(parti) > 2 else ""
                    if not valida_stringa(cliente_nome) or (cliente_cognome and not valida_stringa(cliente_cognome)):
                        conn.sendall("nome o cognome non valido\n".encode())
                        return

                elif riga.startswith("ORDINE") and not ordine_multiplo:
                    try:
                        _, codice, quantita, pagato_str = riga.strip().split()
                        if not (valida_stringa(codice) and valida_integer(quantita) and valida_float(pagato_str)):
                            raise ValueError("dati non validi")

                        quantita = int(quantita)
                        pagato = float(pagato_str)
                        risposta = gestisci_ordine_singolo(local_db, cliente_nome, cliente_cognome, codice, quantita, pagato)
                        conn.sendall((risposta + "\n").encode())
                    except Exception as e:
                        conn.sendall((f"errore parsing ordine singolo {str(e)}\n").encode())

                elif riga.startswith("ORDINE") and ordine_multiplo:
                    try:
                        _, codice, quantita = riga.strip().split()
                        if not (valida_stringa(codice) and valida_integer(quantita)):
                            raise ValueError("dati non validi")

                        quantita = int(quantita)
                        ordine = (codice, quantita)
                        buffer.append(ordine)
                    except Exception as e:
                        conn.sendall((f"errori nel parsing ordine multiplo {str(e)}\n").encode())
                
                elif riga.startswith("STORICO"):
                    _, nome, cognome = riga.strip().split()
                    storico = local_db.get_ordini_cliente(nome, cognome)
                    if storico:
                        risposta = "\n".join(
                            f"Ordine {o['id_ordine']}: {o['quantita']}x {o['nome_prodotto']} - {o['subtotale']}€" for o in storico
                        )
                    else:
                        risposta = "nessun ordine trovato"
                    
                    conn.sendall((risposta + "\n").encode())
                


                elif riga.startswith("PAGAMENTO") and ordine_multiplo:
                    try:
                        pagato_str = riga.strip().split()[1]
                        if not valida_float(pagato_str):
                            raise ValueError("importo non valido")

                        pagato = float(pagato_str)
                        risposta = gestisci_ordine_multiplo(local_db, cliente_nome, cliente_cognome, buffer, pagato)
                        conn.sendall((risposta + "\n").encode())
                        buffer.clear()
                    except Exception as e:
                        conn.sendall((f"errore nel pagamento {str(e)}\n").encode())

    except Exception as e:
        conn.sendall((f"errore generale {str(e)}\n").encode())
    finally:
        conn.close()

def gestisci_ordine_singolo(local_db, nome, cognome, codice, quantita, pagato):
    risultato = local_db.add_ordine_singolo(nome, cognome, codice, quantita, pagato)
    return risultato["messaggio"]

def gestisci_ordine_multiplo(local_db, nome, cognome, items, pagato):
    risultato = local_db.add_ordine_multiplo(nome, cognome, items, pagato)
    return risultato["messaggio"]

def avvia_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    server.bind(("0.0.0.0", 5555))
    server.listen()
    print("Server Avviato")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=gestisci_client, args=(conn, addr))
        thread.start()

if __name__ == "__main__":
    avvia_server()
