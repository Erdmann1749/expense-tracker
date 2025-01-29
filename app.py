import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
from datetime import datetime

# Datenbank initialisieren
def init_expenses_db():
    conn = sqlite3.connect("expense_tracker/expenses.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT,
                    category TEXT,
                    amount REAL,
                    store TEXT
                )''')
    conn.commit()
    conn.close()

# Funktion zum Speichern einer Ausgabe
def add_expense(date, category, amount, store):
    conn = sqlite3.connect("expense_tracker/expenses.db")
    c = conn.cursor()
    c.execute("INSERT INTO expenses (date, category, amount, store) VALUES (?, ?, ?, ?)",
              (date, category, amount, store))
    conn.commit()
    conn.close()

# Funktion zum Laden der Ausgaben
def get_expenses():
    conn = sqlite3.connect("expense_tracker/expenses.db")
    df = pd.read_sql("SELECT * FROM expenses", conn)
    conn.close()
    return df

def init_store_db():
    conn = sqlite3.connect("expense_tracker/expenses.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS stores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT
                )''')
    conn.commit()
    conn.close()

def add_store(name):
    conn = sqlite3.connect("expense_tracker/expenses.db")
    c = conn.cursor()
    c.execute("INSERT INTO stores (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()

# Funktion zum Laden der Stores
def get_stores():
    conn = sqlite3.connect("expense_tracker/expenses.db")
    store_names = pd.read_sql("SELECT name FROM stores", conn)
    conn.close()
    return store_names

# Initialisiere die Datenbank beim ersten Start
init_expenses_db()
init_store_db()

# Streamlit UI
st.title("Essensausgaben Tracker")
name = st.text_input("Füge einen Laden hinzu")
if st.button("Laden der DB hinzufügen"):
    store_names = get_stores()
    if name.lower() nots in [x.lower() for x in store_names["name"]]:
        add_store(name)
    st.rerun()

# Eingabeformular
column_1, column_2, column_3, column_4 = st.columns(4)
with column_1:
    date = st.date_input("Datum", datetime.today())
with column_2:
    category = st.selectbox("Kategorie", ["Einkauf", "Lieferung", "Restaurant"])
with column_3:
    amount = st.number_input("Betrag (€)", min_value=0.0, format="%.2f")
with column_4:
    stores = get_stores()
    print(stores)
    store = st.selectbox("Laden", stores)

if st.button("Hinzufügen"):
    add_expense(date.strftime('%Y-%m-%d'), category, amount, store)
    st.success("Ausgabe hinzugefügt!")

df = get_expenses()
if len(df) > 0:
    # Anzeigen der gespeicherten Daten
    st.write("### Bisherige Ausgaben")
    st.dataframe(df)

    # Auswertung der Ausgaben
    df["date"] = pd.to_datetime(df["date"])
    df_weekly = df.groupby(pd.Grouper(key="date", freq="W"))["amount"].sum()

    st.write("### Wöchentliche Ausgaben")
    fig, ax = plt.subplots()
    df_weekly.plot(kind="bar", ax=ax)
    st.pyplot(fig)


