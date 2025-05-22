import pyodbc
from zoneinfo import ZoneInfo
from datetime import datetime
from Log import Logger
from contextlib import contextmanager
import time


class Database:
    def __init__(self, conn_str):
        self.conn_str = conn_str
        self.conn = pyodbc.connect(self.conn_str)
        self.cursor = None
        self.logger = Logger(use_colors=True, Debug=False)
        self.logger.info("Connessione al database stabilita")
        
        self.prodotti_cache = None
        self.prodotti_time = 0

    def create_cursor(self):
        if self.cursor is None:
            self.cursor = self.conn.cursor()
            self.logger.info("Cursor creato")

    def close_cursor(self):
        if self.cursor:
            self.cursor.close()
            self.cursor = None
            self.logger.info("Cursor chiuso")

    def close_connection(self):
        self.close_cursor()
        if self.conn:
            self.conn.close()
            self.conn = None
            self.logger.info("Connessione al database chiusa")
    
    @contextmanager
    def transazione(self):
        try:
            self.conn.autocommit = False
            yield self.conn
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise
        finally:
            self.conn.autocommit = True
            

    def execute_query(self, query, params=None):
        if self.cursor is None:
            raise Exception("Cursore non creato. Chiamare create_cursor() prima")
        try:
            if params:
                self.logger.info(f"Esecuzione query: {query} con parametri {params}")
                self.cursor.execute(query, params)
            else:
                self.logger.info(f"Esecuzione query: {query}")
                self.cursor.execute(query)
            self.logger.info("Commit eseguito con successo")
        except Exception as e:
            self.logger.info(f"Errore nell'esecuzione della query: {e}")
            raise

    def execute_select_fetchall(self, query, params=None):
        if self.cursor is None:
            raise Exception("Cursore non creato. Chiamare create_cursor() prima")
        try:
            if params:
                self.logger.info(f"Esecuzione fetchall: {query} con parametri {params}")
                self.cursor.execute(query, params)
            else:
                self.logger.info(f"Esecuzione fetchall: {query}")
                self.cursor.execute(query)  
            results = self.cursor.fetchall()
            self.logger.info(f"Fetchall recuperate {len(results)} righe")
            return results
        except Exception as e:
            self.logger.info(f"Errore durante fetchall: {e}")
            raise

    def execute_select_fetchone(self, query, params=None):
        if self.cursor is None:
            raise Exception("Cursore non creato. Chiamare create_cursor() prima")
        try:
            if params:
                self.logger.info(f"Esecuzione fetchone: {query} con parametri {params}")
                self.cursor.execute(query, params)
            else:
                self.logger.info(f"Esecuzione fetchone: {query}")
                self.cursor.execute(query)
            result = self.cursor.fetchone()
            if result:
                self.logger.info("Fetchone ha restituito una riga")
            else:
                self.logger.info("Fetchone non ha trovato righe")
            return result
        except Exception as e:
            print(f"Errore durante fetchone: {e}")
            raise

    def get_client_id(self, nome, cognome):
        print(f"Ricerca ID cliente per {nome} {cognome}")
        self.create_cursor()
        
        row = None
        if nome and cognome:
            row = self.execute_select_fetchone(
                "SELECT ID_Cliente FROM Clienti WHERE Nome = ? AND Cognome = ?",
                (nome, cognome)
            )
        
        self.close_cursor()
        if row:
            self.logger.info(f"Cliente trovato con ID {row[0]}")
            return row[0]
        else:
            self.logger.info("Cliente non trovato o nome e cognome mancanti")
            return None

    def get_prodotti(self):
        if self.prodotti_cache and time.time() - self.prodotti_time < 300:
            return self.prodotti_cache
        
        cursor = self.conn.cursor()
        cursor.execute("SELECT Id_Prodotto, Nome, CodProdotto, Prezzo FROM Prodotto")
        prodotti = {}
        for row in cursor.fetchall():
            prodotti[row[2]] = (row[0], row[1], float(row[3]))
        self.prodotti_cache = prodotti
        self.prodotti_time = time.time()
        return prodotti
    
    def get_or_create_client(self, nome, cognome):
        user_id = self.get_client_id(nome, cognome)
        if user_id:
            self.logger.info(f"Cliente esistente trovato con ID {user_id}")
            return user_id, False
        
        self.logger.info(f"Cliente non trovato, creo nuovo cliente {nome} {cognome}")
        
        with self.transazione():
            self.create_cursor()
            self.execute_query(
            "INSERT INTO Clienti (Nome, Cognome) VALUES (?, ?)",
            (nome, cognome)
        )
            self.close_cursor()
        
        new_id = self.get_client_id(nome, cognome)
        self.logger.info(f"Nuovo cliente creato con ID {new_id}")
        return new_id, True

    def add_ordine_singolo(self, nome_cliente, cognome_cliente, codice_prodotto, quantita, importo_pagato):
        try:
            prodotti = self.get_prodotti()
            if codice_prodotto not in prodotti:
                return {"status": "Errore", "messaggio": f"Prodotto con codice {codice_prodotto} non trovato"}
            
            id_prodotto, nome_prodotto, prezzo_unitario = prodotti[codice_prodotto]
            costo_totale = prezzo_unitario * quantita
            resto = importo_pagato - costo_totale
            
            if resto < 0:
                return {
                    "status": "Errore_Soldi_Insufficienti",
                    "messaggio": f"{nome_cliente} {cognome_cliente} siamo spiacenti ma il tuo ordine è annullato",
                    "costo_totale": costo_totale,
                    "pagato": importo_pagato,
                    "differenza": abs(resto)
                }
            
            user_id, created = self.get_or_create_client(nome_cliente, cognome_cliente)
            data = datetime.now(ZoneInfo('Europe/Rome')).date()
            
            with self.transazione():
                self.create_cursor()
            
            self.execute_query(
                "INSERT INTO Ordini (ID_Cliente, DataOrdine, TotalePagato, Resto) VALUES (?, ?, ?, ?)",
                (user_id, data, importo_pagato, resto)
            )
            
            ordine_row = self.execute_select_fetchone(
                "SELECT TOP 1 ID_Ordine FROM Ordini WHERE ID_Cliente = ? ORDER BY ID_Ordine DESC",
                (user_id,)
            )
            id_ordine = ordine_row[0]
            
            subtotale = prezzo_unitario * quantita
            self.execute_query(
                "INSERT INTO DettagliOrdine (ID_Ordine, ID_Prodotto, Quantita, PrezzoUnitario, Subtotale) VALUES (?, ?, ?, ?, ?)",
                (id_ordine, id_prodotto, quantita, prezzo_unitario, subtotale)
            )
            
            self.close_cursor()
            
            return {
                "status": "Successo",
                "messaggio": f"La consegna di {quantita} confezioni di {nome_prodotto} è in corso con € {resto:.2f} di resto",
                "ordine_id": id_ordine,
                "resto": resto
            }
            
        except Exception as e:
            self.logger.info(f"Errore nell'aggiunta dell'ordine singolo: {e}")
            return {"status": "Errore", "messaggio": f"Errore durante l'elaborazione dell'ordine: {str(e)}"}

    def add_ordine_multiplo(self, nome_cliente, cognome_cliente, items, importo_pagato):
        try:
            prodotti = self.get_prodotti()
            costo_totale = 0
            dettagli_ordine = []
            
            for codice_prodotto, quantita in items:
                if codice_prodotto not in prodotti:
                    return {"status": "Errore", "messaggio": f"Prodotto con codice {codice_prodotto} non trovato"}
                
                id_prodotto, nome_prodotto, prezzo_unitario = prodotti[codice_prodotto]
                subtotale = prezzo_unitario * quantita
                costo_totale += subtotale
                
                dettagli_ordine.append({
                    "id_prodotto": id_prodotto,
                    "nome_prodotto": nome_prodotto,
                    "codice": codice_prodotto,
                    "quantita": quantita,
                    "prezzo_unitario": prezzo_unitario,
                    "subtotale": subtotale
                })
            
            resto = importo_pagato - costo_totale
            
            if resto < 0:
                return {
                    "status": "Errore_Soldi_Insufficienti",
                    "messaggio": f"{nome_cliente} {cognome_cliente} siamo spiacenti ma il tuo ordine è annullato",
                    "costo_totale": costo_totale,
                    "pagato": importo_pagato,
                    "differenza": abs(resto)
                }
            
            user_id, created = self.get_or_create_client(nome_cliente, cognome_cliente)
            
            data = datetime.now(ZoneInfo('Europe/Rome')).date()
            
            with self.transazione():
                self.create_cursor()
            
            self.execute_query(
                "INSERT INTO Ordini (ID_Cliente, DataOrdine, TotalePagato, Resto) VALUES (?, ?, ?, ?)",
                (user_id, data, importo_pagato, resto)
            )
            
            ordine_row = self.execute_select_fetchone(
                "SELECT TOP 1 ID_Ordine FROM Ordini WHERE ID_Cliente = ? ORDER BY ID_Ordine DESC",
                (user_id,)
            )
            id_ordine = ordine_row[0]
            
            prodotti_descrizione = []
            for dettaglio in dettagli_ordine:
                self.execute_query(
                    "INSERT INTO DettagliOrdine (ID_Ordine, ID_Prodotto, Quantita, PrezzoUnitario, Subtotale) VALUES (?, ?, ?, ?, ?)",
                    (id_ordine, dettaglio["id_prodotto"], dettaglio["quantita"], 
                     dettaglio["prezzo_unitario"], dettaglio["subtotale"])
                )
                prodotti_descrizione.append(f"{dettaglio['quantita']} {dettaglio['nome_prodotto']}")
            
            self.close_cursor()
            
            descrizione_prodotti = " - ".join(prodotti_descrizione)
            messaggio = f"{nome_cliente} {cognome_cliente} il tuo ordine di {descrizione_prodotti} è stato inviato con resto di € {resto:.2f}"
            
            return {
                "status": "Successo",
                "messaggio": messaggio,
                "ordine_id": id_ordine,
                "resto": resto,
                "dettagli": dettagli_ordine
            }
            
        except Exception as e:
            self.logger.info(f"Errore nell'aggiunta dell'ordine multiplo: {e}")
            return {"status": "Errore", "messaggio": f"Errore durante l'elaborazione dell'ordine: {str(e)}"}

    def get_ordini_cliente(self, nome_cliente, cognome_cliente):
        user_id = self.get_client_id(nome_cliente, cognome_cliente)
        if not user_id:
            return []
        
        self.create_cursor()
        ordini = self.execute_select_fetchall(
            """
            SELECT o.ID_Ordine, o.DataOrdine, o.TotalePagato, o.Resto,
                p.Nome, p.CodProdotto, d.Quantita, d.PrezzoUnitario, d.Subtotale
            FROM Ordini o
            JOIN DettagliOrdine d ON o.ID_Ordine = d.ID_Ordine
            JOIN Prodotto p ON d.ID_Prodotto = p.Id_Prodotto
            WHERE o.ID_Cliente = ?
            ORDER BY o.ID_Ordine DESC
            """, 
            (user_id,)
        )
        
        self.close_cursor()
        
        result = []
        for row in ordini:
            result.append({
                "id_ordine": row[0],
                "data": row[1],
                "totale_pagato": row[2],
                "resto": row[3],
                "nome_prodotto": row[4],
                "codice_prodotto": row[5],
                "quantita": row[6],
                "prezzo_unitario": row[7],
                "subtotale": row[8]
            })
        
        return result