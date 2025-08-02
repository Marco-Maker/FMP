import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from tkinter import font

# === PATH FILE ===
FILE_QUOTAZIONI = "Quotazioni_Fantacalcio_Stagione_2025_26.xlsx"
FILE_INTERESSE = "lista_giocatori.xlsx"

# === COLORI TEMA BLU ===
COLORS = {
    'primary': '#1e3a8a',      # Blu scuro
    'secondary': '#3b82f6',    # Blu medio
    'accent': '#60a5fa',       # Blu chiaro
    'light': '#dbeafe',        # Blu molto chiaro
    'white': '#ffffff',
    'text_dark': '#1e293b',
    'text_light': '#64748b',
    'success': '#10b981',
    'warning': '#f59e0b',
    'danger': '#ef4444'
}

# === FUNZIONE: Carica lista giocatori di interesse ===
def carica_lista_interesse(path):
    try:
        df = pd.read_excel(path, header=None)
        ruolo = None
        dati = []
        for _, row in df.iterrows():
            val = str(row[0]).strip()
            if val in ["POR", "DF", "CEN", "ATT"]:
                ruolo = val
            elif val and val != "nan":
                dati.append((ruolo, val.upper()))
        return pd.DataFrame(dati, columns=["Ruolo", "Cognome"])
    except FileNotFoundError:
        return pd.DataFrame(columns=["Ruolo", "Cognome"])

# === Carica i file ===
try:
    quotazioni_df = pd.read_excel(FILE_QUOTAZIONI, header=1)
    quotazioni_df["Cognome"] = quotazioni_df["Nome"].str.split().str[-1].str.upper()
except FileNotFoundError:
    messagebox.showerror("Errore", f"File {FILE_QUOTAZIONI} non trovato!")
    exit()

interesse_df = carica_lista_interesse(FILE_INTERESSE)
quotazioni_df["Interesse"] = quotazioni_df["Cognome"].isin(interesse_df["Cognome"])

# === Gruppi per tab ===
tabs_data = {
    "🥅 Portieri": quotazioni_df[quotazioni_df["R"].str.startswith("P")],
    "🛡️ Difensori": quotazioni_df[quotazioni_df["R"].str.startswith("D")],
    "⚽ Centrocampisti": quotazioni_df[quotazioni_df["R"].str.startswith("C")],
    "🎯 Attaccanti": quotazioni_df[quotazioni_df["R"].str.startswith("A")],
    "⭐ I Miei Giocatori": quotazioni_df[quotazioni_df["Interesse"]]
}

# === FUNZIONE: aggiorna Excel lista interesse ===
def salva_lista_interesse():
    new_data = interesse_df[["Ruolo", "Cognome"]]
    with pd.ExcelWriter(FILE_INTERESSE, engine="xlsxwriter") as writer:
        startrow = 0
        for ruolo in ["POR", "DF", "CEN", "ATT"]:
            subset = new_data[new_data["Ruolo"] == ruolo]
            pd.DataFrame([ruolo]).to_excel(writer, index=False, header=False, startrow=startrow)
            subset[["Cognome"]].to_excel(writer, index=False, header=False, startrow=startrow+1)
            startrow += len(subset) + 2

# === FUNZIONE: salva dati squadra personalizzati ===
def salva_dati_squadra():
    nome_squadra = entry_squadra.get().strip()
    if not nome_squadra:
        messagebox.showwarning("Attenzione", "Inserisci il nome della squadra!")
        return
    
    try:
        budget = float(entry_budget.get())
    except ValueError:
        messagebox.showwarning("Attenzione", "Inserisci un budget valido!")
        return
    
    # Calcola il fattore di conversione (1000 è il valore base FVM)
    fattore = budget / 1000
    
    # Crea una copia del dataframe con i valori convertiti
    df_squadra = quotazioni_df.copy()
    df_squadra["FVM_Personalizzato"] = (df_squadra["FVM"] * fattore).round(0).astype(int)
    
    # Salva solo i giocatori di interesse
    df_interesse = df_squadra[df_squadra["Interesse"]].copy()
    
    # Prepara i dati per il salvataggio
    cols_da_salvare = ["Nome", "Squadra", "R", "FVM", "FVM_Personalizzato"]
    df_finale = df_interesse[cols_da_salvare].copy()
    
    # Nome file
    nome_file = f"{nome_squadra.replace(' ', '_')}_fantacalcio.xlsx"
    
    try:
        with pd.ExcelWriter(nome_file, engine="xlsxwriter") as writer:
            # Foglio principale con tutti i dati
            df_finale.to_excel(writer, sheet_name="Giocatori", index=False)
            
            # Fogli separati per ruolo
            for ruolo, emoji in [("P", "Portieri"), ("D", "Difensori"), ("C", "Centrocampisti"), ("A", "Attaccanti")]:
                df_ruolo = df_finale[df_finale["R"].str.startswith(ruolo)]
                if not df_ruolo.empty:
                    df_ruolo.to_excel(writer, sheet_name=emoji, index=False)
            
            # Foglio riepilogo
            riepilogo_data = {
                "Squadra": [nome_squadra],
                "Budget_Lega": [budget],
                "Totale_Giocatori": [len(df_finale)],
                "Valore_Totale_FVM": [df_finale["FVM"].sum()],
                "Valore_Totale_Personalizzato": [df_finale["FVM_Personalizzato"].sum()],
                "Data_Creazione": [pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")]
            }
            pd.DataFrame(riepilogo_data).to_excel(writer, sheet_name="Riepilogo", index=False)
        
        messagebox.showinfo("Successo", f"Dati salvati in: {nome_file}")
        aggiorna_tabelle()
        
    except Exception as e:
        messagebox.showerror("Errore", f"Errore nel salvataggio: {str(e)}")

# === FUNZIONE CALCOLO FVM PERSONALIZZATO ===
def calcola_fvm_personalizzato():
    try:
        budget = float(entry_budget.get())
        return budget / 1000
    except ValueError:
        return 1.0

# === FUNZIONE: aggiorna flag interesse nel dataframe principale ===
def aggiorna_flag_interesse():
    """Aggiorna il flag di interesse nel dataframe principale"""
    global quotazioni_df
    quotazioni_df["Interesse"] = quotazioni_df["Cognome"].isin(interesse_df["Cognome"])
    # Aggiorna anche la tab "I Miei Giocatori"
    tabs_data["⭐ I Miei Giocatori"] = quotazioni_df[quotazioni_df["Interesse"]]

# === INTERFACCIA GRAFICA ===
root = tk.Tk()
root.title("⚽ Fantacalcio Manager Pro")
root.geometry("1200x900")  # Aumentata l'altezza da 800 a 900
root.configure(bg=COLORS['light'])

# Font personalizzati
title_font = font.Font(family="Segoe UI", size=16, weight="bold")
header_font = font.Font(family="Segoe UI", size=12, weight="bold")
normal_font = font.Font(family="Segoe UI", size=10)

# === STILE TTK ===
style = ttk.Style()
style.theme_use('clam')

# Configura stili personalizzati
style.configure('Title.TLabel', 
                font=title_font, 
                background=COLORS['light'],
                foreground=COLORS['primary'])

style.configure('Header.TLabel',
                font=header_font,
                background=COLORS['light'],
                foreground=COLORS['text_dark'])

style.configure('Custom.TNotebook',
                background=COLORS['light'],
                borderwidth=0)

style.configure('Custom.TNotebook.Tab',
                padding=[20, 10],
                font=header_font,
                background=COLORS['white'],
                foreground=COLORS['text_dark'])

style.map('Custom.TNotebook.Tab',
          background=[('selected', COLORS['primary']),
                     ('active', COLORS['accent'])],
          foreground=[('selected', COLORS['white']),
                     ('active', COLORS['white'])])

style.configure('Treeview',
                background=COLORS['white'],
                foreground=COLORS['text_dark'],
                rowheight=25,
                fieldbackground=COLORS['white'])

style.configure('Treeview.Heading',
                background=COLORS['secondary'],
                foreground=COLORS['white'],
                font=header_font)

# === HEADER PRINCIPALE ===
header_frame = tk.Frame(root, bg=COLORS['primary'], height=80)
header_frame.pack(fill=tk.X)
header_frame.pack_propagate(False)

title_label = tk.Label(header_frame, 
                      text="⚽ FANTACALCIO MANAGER PRO", 
                      font=title_font,
                      bg=COLORS['primary'], 
                      fg=COLORS['white'])
title_label.pack(expand=True)

# === FRAME CONFIGURAZIONE ===
config_frame = tk.Frame(root, bg=COLORS['light'], pady=15)
config_frame.pack(fill=tk.X, padx=20)

# Frame squadra e budget
team_frame = tk.Frame(config_frame, bg=COLORS['light'])
team_frame.pack(fill=tk.X, pady=5)

# Nome squadra
tk.Label(team_frame, text="🏆 Nome Squadra:", 
         font=header_font, bg=COLORS['light'], 
         fg=COLORS['text_dark']).pack(side=tk.LEFT, padx=(0, 10))

entry_squadra = tk.Entry(team_frame, font=normal_font, width=20, 
                        bg=COLORS['white'], fg=COLORS['text_dark'],
                        relief='solid', bd=1)
entry_squadra.pack(side=tk.LEFT, padx=(0, 20))

# Budget lega
tk.Label(team_frame, text="💰 Budget Lega:", 
         font=header_font, bg=COLORS['light'], 
         fg=COLORS['text_dark']).pack(side=tk.LEFT, padx=(0, 10))

entry_budget = tk.Entry(team_frame, font=normal_font, width=10,
                       bg=COLORS['white'], fg=COLORS['text_dark'],
                       relief='solid', bd=1)
entry_budget.insert(0, "1000")
entry_budget.pack(side=tk.LEFT, padx=(0, 20))

# Checkbox interesse
mostra_solo_interesse = tk.BooleanVar()
checkbox_interesse = tk.Checkbutton(team_frame, 
                                   text="👀 Mostra solo giocatori di interesse",
                                   variable=mostra_solo_interesse,
                                   font=normal_font,
                                   bg=COLORS['light'],
                                   fg=COLORS['text_dark'],
                                   activebackground=COLORS['light'])
checkbox_interesse.pack(side=tk.LEFT, padx=(0, 20))

# Pulsante salva squadra
btn_salva_squadra = tk.Button(team_frame, text="💾 Salva Dati Squadra",
                             command=salva_dati_squadra,
                             font=header_font,
                             bg=COLORS['success'],
                             fg=COLORS['white'],
                             relief='flat',
                             padx=20, pady=8,
                             cursor='hand2')
btn_salva_squadra.pack(side=tk.RIGHT)

# === NOTEBOOK PER I TAB ===
notebook = ttk.Notebook(root, style='Custom.TNotebook')
notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))

treeviews = {}

# === FUNZIONE: carica tabella ===
def carica_tabella(tree, tab_name):
    tree.delete(*tree.get_children())
    
    # Determina quale dataframe usare in base al tab
    if tab_name == "⭐ I Miei Giocatori":
        # Per la tab "I Miei Giocatori", usa sempre i dati aggiornati
        df_filtered = quotazioni_df[quotazioni_df["Interesse"]]
    elif tab_name == "🥅 Portieri":
        df = quotazioni_df[quotazioni_df["R"].str.startswith("P")]
        df_filtered = df[df["Interesse"]] if mostra_solo_interesse.get() else df
    elif tab_name == "🛡️ Difensori":
        df = quotazioni_df[quotazioni_df["R"].str.startswith("D")]
        df_filtered = df[df["Interesse"]] if mostra_solo_interesse.get() else df
    elif tab_name == "⚽ Centrocampisti":
        df = quotazioni_df[quotazioni_df["R"].str.startswith("C")]
        df_filtered = df[df["Interesse"]] if mostra_solo_interesse.get() else df
    elif tab_name == "🎯 Attaccanti":
        df = quotazioni_df[quotazioni_df["R"].str.startswith("A")]
        df_filtered = df[df["Interesse"]] if mostra_solo_interesse.get() else df
    else:
        df_filtered = quotazioni_df
    
    fattore = calcola_fvm_personalizzato()
    
    for _, row in df_filtered.iterrows():
        fvm_personalizzato = int(row["FVM"] * fattore)
        interesse_icon = "⭐" if row["Interesse"] else "⚪"
        tree.insert("", "end", values=(
            row["Nome"], 
            row["Squadra"],
            row["FVM"],
            fvm_personalizzato,
            interesse_icon
        ))

# === FUNZIONE: ordinamento colonne ===
def sort_column(tree, col, reverse):
    data = [(tree.set(k, col), k) for k in tree.get_children("")]
    try:
        if col in ["FVM", "FVM_Pers"]:
            data.sort(key=lambda t: float(t[0]), reverse=reverse)
        else:
            data.sort(key=lambda t: t[0], reverse=reverse)
    except ValueError:
        data.sort(key=lambda t: t[0], reverse=reverse)
    
    for index, (val, k) in enumerate(data):
        tree.move(k, "", index)
    tree.heading(col, command=lambda: sort_column(tree, col, not reverse))

# === FUNZIONE: rimuovi giocatore ===
def rimuovi_giocatore():
    current_tab = notebook.tab(notebook.select(), "text")
    tree = treeviews[current_tab][0]
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("⚠️ Attenzione", "Seleziona un giocatore da rimuovere.")
        return
    
    nome = tree.item(selected[0])["values"][0]
    cognome = nome.split()[-1].upper()
    global interesse_df
    interesse_df = interesse_df[interesse_df["Cognome"] != cognome]
    
    # Salva immediatamente su file
    salva_lista_interesse()
    
    # Aggiorna il flag di interesse
    aggiorna_flag_interesse()
    
    # Aggiorna tutte le tabelle
    aggiorna_tabelle()
    
    messagebox.showinfo("✅ Successo", f"Giocatore {nome} rimosso dalla lista!")

# === FUNZIONE: aggiungi giocatore selezionato ===
def aggiungi_giocatore():
    current_tab = notebook.tab(notebook.select(), "text")
    tree = treeviews[current_tab][0]
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("⚠️ Attenzione", "Seleziona un giocatore da aggiungere.")
        return
    
    nome = tree.item(selected[0])["values"][0]
    cognome = nome.split()[-1].upper()
    
    ruolo_map = {
        "🥅 Portieri": "POR", 
        "🛡️ Difensori": "DF", 
        "⚽ Centrocampisti": "CEN", 
        "🎯 Attaccanti": "ATT",
        "⭐ I Miei Giocatori": "GENERIC"  # Per la tab dei giocatori di interesse
    }
    
    # Se siamo nella tab "I Miei Giocatori", determina il ruolo dal dataframe
    if current_tab == "⭐ I Miei Giocatori":
        # Trova il ruolo dal dataframe quotazioni
        player_row = quotazioni_df[quotazioni_df["Nome"] == nome]
        if not player_row.empty:
            ruolo_orig = player_row.iloc[0]["R"]
            if ruolo_orig.startswith("P"):
                ruolo = "POR"
            elif ruolo_orig.startswith("D"):
                ruolo = "DF"
            elif ruolo_orig.startswith("C"):
                ruolo = "CEN"
            elif ruolo_orig.startswith("A"):
                ruolo = "ATT"
            else:
                ruolo = None
        else:
            ruolo = None
    else:
        ruolo = ruolo_map.get(current_tab, None)
    
    if ruolo is None:
        messagebox.showerror("❌ Errore", "Ruolo non riconosciuto.")
        return
    
    global interesse_df
    if ((interesse_df["Cognome"] == cognome) & (interesse_df["Ruolo"] == ruolo)).any():
        messagebox.showinfo("ℹ️ Info", "Giocatore già presente nella lista di interesse.")
        return
    
    # Aggiungi il giocatore
    nuovo = pd.DataFrame([[ruolo, cognome]], columns=["Ruolo", "Cognome"])
    interesse_df = pd.concat([interesse_df, nuovo], ignore_index=True)
    
    # Salva immediatamente su file
    salva_lista_interesse()
    
    # Aggiorna il flag di interesse
    aggiorna_flag_interesse()
    
    # Aggiorna tutte le tabelle
    aggiorna_tabelle()
    
    messagebox.showinfo("✅ Successo", f"Giocatore {nome} aggiunto alla lista!")

# === FUNZIONE: aggiungi giocatori da testo ===
def aggiungi_da_testo():
    testo = text_area.get("1.0", tk.END).strip()
    if not testo:
        messagebox.showwarning("⚠️ Attenzione", "Inserisci del testo nella text area.")
        return

    global interesse_df
    lines = testo.splitlines()
    ruolo_corrente = None
    aggiunti = 0
    ruoli_validi = {"POR": "POR", "DF": "DF", "CEN": "CEN", "ATT": "ATT"}

    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line in ruoli_validi:
            ruolo_corrente = line
        elif ruolo_corrente is not None:
            cognome = line.upper().split("(")[0].strip()
            if not ((interesse_df["Cognome"] == cognome) & (interesse_df["Ruolo"] == ruolo_corrente)).any():
                nuovo = pd.DataFrame([[ruolo_corrente, cognome]], columns=["Ruolo", "Cognome"])
                interesse_df = pd.concat([interesse_df, nuovo], ignore_index=True)
                aggiunti += 1

    if aggiunti > 0:
        # Salva immediatamente su file
        salva_lista_interesse()
        
        # Aggiorna il flag di interesse
        aggiorna_flag_interesse()
        
        # Aggiorna tutte le tabelle
        aggiorna_tabelle()
        
        messagebox.showinfo("✅ Fatto", f"Aggiunti {aggiunti} giocatori dalla lista.")
        text_area.delete("1.0", tk.END)
    else:
        messagebox.showinfo("ℹ️ Info", "Nessun giocatore nuovo da aggiungere.")

# === Crea tab per ogni ruolo ===
for tab_nome, df in tabs_data.items():
    frame = ttk.Frame(notebook)
    notebook.add(frame, text=tab_nome)

    # Frame per la tabella
    table_frame = tk.Frame(frame, bg=COLORS['white'])
    table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    tree = ttk.Treeview(table_frame, 
                       columns=("Nome", "Squadra", "FVM", "FVM_Pers", "Interesse"), 
                       show="headings",
                       style='Treeview')
    
    # Configura colonne
    tree.heading("Nome", text="👤 Nome", command=lambda _tree=tree: sort_column(_tree, "Nome", False))
    tree.heading("Squadra", text="🏟️ Squadra", command=lambda _tree=tree: sort_column(_tree, "Squadra", False))
    tree.heading("FVM", text="💎 FVM", command=lambda _tree=tree: sort_column(_tree, "FVM", False))
    tree.heading("FVM_Pers", text="💰 FVM Personalizzato", command=lambda _tree=tree: sort_column(_tree, "FVM_Pers", False))
    tree.heading("Interesse", text="⭐ Interesse", command=lambda _tree=tree: sort_column(_tree, "Interesse", False))
    
    tree.column("Nome", width=200)
    tree.column("Squadra", width=120)
    tree.column("FVM", width=80)
    tree.column("FVM_Pers", width=130)
    tree.column("Interesse", width=80)
    
    # Scrollbar
    scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    
    tree.pack(side="left", fill=tk.BOTH, expand=True)
    scrollbar.pack(side="right", fill="y")

    treeviews[tab_nome] = (tree, None)  # Non serve più salvare il dataframe

# === FRAME PULSANTI ===
buttons_frame = tk.Frame(root, bg=COLORS['light'], pady=10)
buttons_frame.pack(fill=tk.X, padx=20)

btn_style = {'font': normal_font, 'relief': 'flat', 'padx': 15, 'pady': 8, 'cursor': 'hand2'}

btn_rimuovi = tk.Button(buttons_frame, text="❌ Rimuovi Giocatore", 
                       command=rimuovi_giocatore,
                       bg=COLORS['danger'], fg=COLORS['white'],
                       **btn_style)
btn_rimuovi.pack(side=tk.LEFT, padx=10)

btn_aggiungi = tk.Button(buttons_frame, text="➕ Aggiungi Giocatore", 
                        command=aggiungi_giocatore,
                        bg=COLORS['success'], fg=COLORS['white'],
                        **btn_style)
btn_aggiungi.pack(side=tk.LEFT, padx=10)

# === FRAME INPUT TESTO CON SCROLL ===
input_frame = tk.LabelFrame(root, text="📝 Aggiungi Giocatori da Lista", 
                           font=header_font, bg=COLORS['light'], 
                           fg=COLORS['text_dark'], pady=10)
input_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

info_label = tk.Label(input_frame, 
                     text="Formato: POR/DF/CEN/ATT su una riga, poi i cognomi dei giocatori uno per riga",
                     font=normal_font, bg=COLORS['light'], fg=COLORS['text_light'])
info_label.pack(anchor="w", padx=10)

# Frame per text area con scrollbar
text_frame = tk.Frame(input_frame, bg=COLORS['light'])
text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

text_area = tk.Text(text_frame, height=6, font=normal_font,
                   bg=COLORS['white'], fg=COLORS['text_dark'],
                   relief='solid', bd=1, wrap=tk.WORD)

# Scrollbar per la text area
text_scrollbar = tk.Scrollbar(text_frame, orient="vertical", command=text_area.yview)
text_area.configure(yscrollcommand=text_scrollbar.set)

text_area.pack(side="left", fill=tk.BOTH, expand=True)
text_scrollbar.pack(side="right", fill="y")

btn_aggiungi_testo = tk.Button(input_frame, text="📋 Aggiungi da Lista", 
                              command=aggiungi_da_testo,
                              bg=COLORS['primary'], fg=COLORS['white'],
                              **btn_style)
btn_aggiungi_testo.pack(pady=10)

# === FUNZIONE: aggiorna tutte le tabelle ===
def aggiorna_tabelle():
    for tab_nome, (tree, _) in treeviews.items():
        carica_tabella(tree, tab_nome)

# Event binding
checkbox_interesse.config(command=aggiorna_tabelle)
entry_budget.bind('<KeyRelease>', lambda e: aggiorna_tabelle())

# Carica tabelle iniziali
aggiorna_tabelle()

# Avvia l'applicazione
root.mainloop()