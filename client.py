import socket

from db import Database

conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=10.100.1.251;"
    "DATABASE=Corso C;"
    "Trusted_Connection=yes;"
)

SERVER_IP = "127.0.0.1"
SERVER_PORT = 5555

def invia_messaggio(messaggi):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((SERVER_IP, SERVER_PORT))
        for msg in messaggi:
            s.sendall((msg + "\n").encode())
        s.shutdown(socket.SHUT_WR)
        risposta = ""
        while True:
            dati = s.recv(1024)
            if not dati:
                break
            risposta += dati.decode()
        print("\n[risposta server]:")
        print(risposta.strip())

def is_float(value):
    try:
        float(value)
        return True
    except:
        return False
    
def get_products():
    db = Database(conn_str)
    prodotti = db.get_prodotti()
    if not prodotti:
        return []
    else:
        return prodotti
    
def print_products():
    prodotti = get_products()
    if not prodotti:
        print("Nessun prodotto disponibile.")
    else:
        print(f"{'Codice':<15}{'Nome':<30}{'Prezzo':>10}")
        print("-" * 55)
        for codice, (id_prodotto, nome, prezzo) in prodotti.items():
            print(f"{codice:<15}{nome:<30}{prezzo:>10.2f}")


    

def menu():
    print("""
--- MENU CLIENT ORDINAZIONI ---
1. Ordine Singolo
2. Ordine Multiplo
3. visualizza storico ordini
0. Esci
""")


def client():
    while True:
        menu()
        scelta = input("Scelta: ")
        print("\n")

        if scelta == "1":
            print_products()
            nome = input("\nNome cliente: ")
            cognome = input("Cognome cliente: ")
            codice = input("Codice prodotto: ")
            quantita = input("Quantita: ")
            if not quantita.isdigit() or int(quantita) <= 0:
                print("Quantita non valida")
                continue

            pagato = input("Importo pagato: ")
            
            if not is_float(pagato):
                print("Importo non valido")
                continue
            
            messaggi = [
                "SCELTA SINGOLO",
                f"CLIENTE {nome} {cognome}",
                f"ORDINE {codice} {quantita} {pagato}"
            ]
            invia_messaggio(messaggi)

        elif scelta == "2":
            print_products()
            nome = input("\nNome cliente: ")
            cognome = input("Cognome cliente: ")
            messaggi = ["SCELTA MULTIPLO", f"CLIENTE {nome} {cognome}"]
            print("Inserisci ordini (codice quantita),'fine' per terminare:")
            while True:
                riga = input("Prodotto: ")
                if riga.lower() == "fine":
                    break
                try:
                    codice, quantita = riga.split()
                    messaggi.append(f"ORDINE {codice} {quantita}")
                except:
                    print("Il formato non è valido, usa (codice quantità)")
            pagato = input("Importo totale pagato: ")
            messaggi.append(f"PAGAMENTO {pagato}")
            invia_messaggio(messaggi)
        
        elif scelta == "3":
            nome = input("Nome cliente: ")
            cognome = input("Cognome cliente: ")
            messaggi = [f"STORICO {nome} {cognome}"]
            invia_messaggio(messaggi)
            

        elif scelta == "0":
            print("ciao ciao")
            break
        else:
            print("La scelta non è valida, riprova con uno dei 3 numeri")


if __name__ == "__main__":
    client()
