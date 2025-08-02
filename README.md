# 📊 Fantacalcio Stats & Quotations

Questo progetto è pensato per analizzare, confrontare e utilizzare i dati delle stagioni recenti di Fantacalcio, con particolare riferimento alle **statistiche** e alle **quotazioni ufficiali dei giocatori**.

## 📁 Contenuto del progetto

Il repository contiene i seguenti file principali:

### 1. `Quotazioni_Fantacalcio_Stagione_2025_26`

Contiene le quotazioni ufficiali dei giocatori aggiornate alla stagione **2025/26**, con le seguenti colonne:

* `Id`: Identificativo univoco del giocatore
* `R`: Ruolo
* `RM`: Ruolo Mantra
* `Nome`: Nome del giocatore
* `Squadra`: Squadra di appartenenza
* `Qt.A`: Quotazione attuale
* `Qt.I`: Quotazione iniziale
* `Diff.`: Differenza tra quotazione attuale e iniziale
* `Qt.A M`: Quotazione attuale (Mantra)
* `Qt.I M`: Quotazione iniziale (Mantra)
* `Diff.M`: Differenza quotazione Mantra
* `FVM`: Fantavoto medio
* `FVM M`: Fantavoto medio (Mantra)

---

### 2. `Statistiche_Fantacalcio_Stagione_2024_25`

Contiene le statistiche complete dei giocatori della stagione **2024/25**, con le seguenti colonne:

* `Id`: Identificativo univoco del giocatore
* `R`: Ruolo
* `Rm`: Ruolo Mantra
* `Nome`: Nome del giocatore
* `Squadra`: Squadra di appartenenza
* `Pv`: Presenze con voto
* `Mv`: Media voto
* `Fm`: Fantamedia
* `Gf`: Goal fatti
* `Gs`: Goal subiti
* `Rp`: Rigori parati
* `Rc`: Rigori calciati
* `R+`: Rigori segnati
* `R-`: Rigori sbagliati
* `Ass`: Assist
* `Amm`: Ammonizioni
* `Esp`: Espulsioni
* `Au`: Autogol

---

## 🛠️ Utilizzo previsto

Questi dataset possono essere utilizzati per:

* Analisi delle performance dei giocatori
* Calcolo della convenienza nelle aste
* Supporto per algoritmi di formazione ottimale
* Sviluppo di strumenti di valutazione in tempo reale

---

## 📌 Dipendenze

Per eseguire gli script Python su questi dati, assicurati di avere installato le seguenti librerie:

```bash
pip install pandas numpy matplotlib seaborn
```

---

## 📌 Note

* I file sono in formato `.csv` o `.tsv` e possono essere caricati facilmente tramite `pandas`.
* In caso di problemi con la lettura, verifica l'encoding (es. `utf-8`, `latin1`).

---

Contattami se vuoi uno script di esempio per iniziare subito l'esplorazione dei dati.
