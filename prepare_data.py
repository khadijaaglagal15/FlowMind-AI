
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "data" / "Online Retail.xlsx"
OUTPUT_FILE = BASE_DIR / "data" / "sales_real.csv"

print("Lecture du fichier Excel...")

df = pd.read_excel(INPUT_FILE)

print(f"Nombre de lignes initial : {len(df)}")
print("Colonnes disponibles :", df.columns.tolist())

# Vérifier les colonnes nécessaires
required = [
    "InvoiceNo",
    "StockCode",
    "Description",
    "Quantity",
    "InvoiceDate",
    "UnitPrice",
    "Country",
]

missing = set(required) - set(df.columns)

if missing:
    raise ValueError(f"Colonnes manquantes : {sorted(missing)}")

# Garder les colonnes utiles
df = df[required].copy()

# Nettoyer les données
df["Description"] = df["Description"].astype("string").str.strip()
df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce")
df["UnitPrice"] = pd.to_numeric(df["UnitPrice"], errors="coerce")
df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], errors="coerce")

# Exclure les factures annulées (numéros commençant par C)
df["InvoiceNo"] = df["InvoiceNo"].astype("string").str.strip()
df = df[~df["InvoiceNo"].str.upper().str.startswith("C", na=False)]

# Exclure les valeurs invalides et les retours négatifs
df = df.dropna(
    subset=["InvoiceNo", "StockCode", "Description",
            "Quantity", "UnitPrice", "InvoiceDate", "Country"]
)

df = df[
    (df["Description"] != "")
    & (df["Quantity"] > 0)
    & (df["UnitPrice"] > 0)
].copy()

# Calculer le montant de chaque ligne en GBP
df["TotalAmount"] = df["Quantity"] * df["UnitPrice"]

# Préparer le CSV pour l'analyse
df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

print(f"Nombre de lignes après nettoyage : {len(df)}")
print(f"Chiffre d'affaires total : £{df['TotalAmount'].sum():,.2f}")
print(f"Nombre de produits : {df['Description'].nunique()}")
print(f"Nombre de pays : {df['Country'].nunique()}")
print(f"Fichier créé : {OUTPUT_FILE}")
print("\nAperçu :")
print(df.head())
