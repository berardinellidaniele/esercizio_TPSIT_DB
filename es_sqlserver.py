import pyodbc


conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=10.100.1.251;"
    "DATABASE=Corso B;"
    "Trusted_Connection=yes;"
)

conn = pyodbc.connect(conn_str)


cursor = conn.cursor()

print("QUERY:")
cursor.execute("SELECT * FROM dbo.Beta")

for row in cursor.fetchall():
    print(row)

print("QUERY CON WHERE:")
id=1
cursor.execute("SELECT * FROM dbo.Beta WHERE id=?",id)

for row in cursor.fetchall():
    print(row)

# try:
#     nuovo_nome="Ciao"
#     nuovo_id=4
#     cursor.execute("INSERT INTO dbo.Beta (Nome) VALUES (?)",nuovo_nome)
#     conn.commit()
#     print("Inserimento avvenuto con successo")
# except:
#     print("Errore durante l'inserimento")


# try:
#     nuovo_nome="NomeModificato"
#     id_modificare=1
#     cursor.execute("UPDATE dbo.Beta SET Nome= ? WHERE ID=?",nuovo_nome,id_modificare)
#     conn.commit()
#     print("Aggiornamento avvenuto con successo")
# except Exception as e:
#     print(e)


cursor.close()
conn.close()