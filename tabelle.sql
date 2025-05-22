CREATE TABLE Clienti (
    ID_Cliente INT IDENTITY(1,1) PRIMARY KEY,
    Nome NVARCHAR(50) NOT NULL,
    Cognome NVARCHAR(50) NOT NULL
);

CREATE TABLE Prodotto (
    Id_Prodotto INT IDENTITY(1,1) PRIMARY KEY,
    Nome NVARCHAR(100) NOT NULL,
    CodProdotto NVARCHAR(20) NOT NULL UNIQUE,
    Prezzo FLOAT NOT NULL
);

CREATE TABLE Ordini (
    ID_Ordine INT IDENTITY(1,1) PRIMARY KEY,
    ID_Cliente INT NOT NULL,
    DataOrdine DATE NOT NULL,
    TotalePagato FLOAT NOT NULL,
    Resto FLOAT NOT NULL,
    FOREIGN KEY (ID_Cliente) REFERENCES Clienti(ID_Cliente)
);

CREATE TABLE DettagliOrdine (
    ID_DettagliOrdine INT IDENTITY(1,1) PRIMARY KEY,
    ID_Ordine INT NOT NULL,
    ID_Prodotto INT NOT NULL,
    Quantita INT NOT NULL,
    PrezzoUnitario FLOAT NOT NULL,
    Subtotale FLOAT NOT NULL,
    FOREIGN KEY (ID_Ordine) REFERENCES Ordini(ID_Ordine),
    FOREIGN KEY (ID_Prodotto) REFERENCES Prodotto(Id_Prodotto)
);

INSERT INTO Prodotto (Nome, CodProdotto, Prezzo) VALUES
('Profumo ALFA', 'A', 2.70),
('Profumo BETA', 'B', 4.50),
('Colore Capelli Biondo', 'CB', 6.40),
('Colore Capelli Testa di Moro', 'CTM', 7.25),
('Colore Capelli Corvino', 'CC', 4.67),
('Colore Capelli Rosso', 'CR', 6.44),
('Rossetto', 'R', 9.45),
('Fard', 'F', 4.98),
('Dopobarba', 'D', 7.85),
('Schiuma per Barba', 'S', 3.95);