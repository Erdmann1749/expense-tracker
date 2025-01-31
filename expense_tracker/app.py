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

# Funktion zur Migration der Kategorien
def migrate_categories():
    conn = sqlite3.connect("expense_tracker/expenses.db")
    c = conn.cursor()
    category_mapping = {
        "Einkauf": "Lebensmittelkauf",
        "Lieferung": "Essenslieferung",
        "Restaurant": "Restaurant"
    }
    for old, new in category_mapping.items():
        c.execute("UPDATE expenses SET category = ? WHERE category = ?", (new, old))
    conn.commit()
    conn.close()

def migrate_categories_2():
    conn = sqlite3.connect("expense_tracker/expenses.db")
    c = conn.cursor()
    new = "Take-away"
    stores = [
        "Hachiko Ramen",
        "Saveur Banh Mi",
        "Markt"
    ]
    for store in stores:
        c.execute("UPDATE expenses SET category = ? WHERE store = ?", (new, store))
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
    df["date"] = pd.to_datetime(df["date"])
    df["KW"] = df["date"].dt.strftime("KW %U")
    df = df.sort_values("date", ascending=False).head(10)
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
    return sorted(store_names.name)


# Initialisiere und migriere die Datenbank
init_expenses_db()
init_store_db()
migrate_categories()
migrate_categories_2()


# Streamlit UI
st.title("Essensausgaben Tracker")

column_1, column_2 = st.columns([3, 1])  # Breitenverhältnis anpassen
with column_1:
    name = st.text_input(label="", placeholder="Name des Ladens")
with column_2:
    st.markdown(
        """<style>
        div.stButton { margin-top: 12px; }
        </style>""",
        unsafe_allow_html=True,
    )
    submitted = st.button("Laden hinzufügen")

if submitted:
    store_names = get_stores()
    if name.lower() not in [x.lower() for x in store_names]:
        add_store(name)
    st.rerun()

# Eingabeformular
column_1, column_2, column_3, column_4 = st.columns(4)
with column_1:
    date = st.date_input("Datum", datetime.today())
with column_2:
    category = st.selectbox("Kategorie", ["Essenslieferung", "Lebensmittelkauf", "Take-away Essen", "Restaurant"])
with column_3:
    amount = st.number_input("Betrag (€)", min_value=0.0, format="%.2f")
with column_4:
    stores = get_stores()
    store = st.selectbox("Laden", stores)

if st.button("Hinzufügen"):
    add_expense(date.strftime('%Y-%m-%d'), category, amount, store)
    st.success("Ausgabe hinzugefügt!")

df = get_expenses()
if len(df) > 0:
    # Anzeigen der gespeicherten Daten
    st.write("### Bisherige Ausgaben")
    df["date"] = pd.to_datetime(df["date"]).dt.date
    st.dataframe(df[["date", "category", "amount", "store"]])

    # Auswertung der Ausgaben
    df_weekly_stacked = df.groupby(["KW", "category"])["amount"].sum().unstack().fillna(0)
    df_weekly = df.groupby("KW")["amount"].sum()
    df_weekly = df_weekly.sort_index()  # Ensure chronological order
    df_weekly_rolled = df_weekly.rolling(window=4, min_periods=1).mean()


    st.write("### Wöchentliche Ausgaben")
    fig, ax = plt.subplots()
    df_weekly_stacked.plot(kind="bar", stacked=True, ax=ax)
    df_weekly_rolled.plot(kind="line", color="red", marker="o", ax=ax)
    ax.set_xlabel("Kalenderwoche")
    ax.set_ylabel("Betrag (€)")
    ax.set_xticklabels(df_weekly_stacked.index, rotation=45)
    st.pyplot(fig)


