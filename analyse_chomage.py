"""Chômage au Maroc : import des données, statistiques et graphiques.

Usage :  python analyse_chomage.py          (utilise les CSV locaux)
         python analyse_chomage.py --wb     (compare aussi avec l'API Banque mondiale)
Dépendances : pip install pandas matplotlib requests
"""
import sys
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

DATA = Path(__file__).parent / "data"
OUT = Path(__file__).parent / "figures"
OUT.mkdir(exist_ok=True)

# 1) Import
serie = pd.read_csv(DATA / "chomage_maroc_annuel.csv")
cat = pd.read_csv(DATA / "chomage_par_categorie.csv")

# 2) Statistiques simples
serie["variation_pts"] = serie["taux_chomage_pct"].diff().round(1)
avant = serie[serie.annee <= 2019]["taux_chomage_pct"].mean()
apres = serie[serie.annee >= 2020]["taux_chomage_pct"].mean()
print(f"Moyenne 2010-2019 : {avant:.1f} %  |  Moyenne 2020-2025 : {apres:.1f} %")
print(f"Pic : {serie.loc[serie.taux_chomage_pct.idxmax(), 'annee']} "
      f"({serie.taux_chomage_pct.max()} %)")
print(serie.tail(8).to_string(index=False))

# 3) Graphique 1 : évolution du taux de chômage
fig, ax = plt.subplots(figsize=(9, 5))
ax.plot(serie.annee, serie.taux_chomage_pct, marker="o", color="#c0392b", label="HCP")
if "--wb" in sys.argv:
    import requests
    url = ("https://api.worldbank.org/v2/country/MAR/indicator/SL.UEM.TOTL.ZS"
           "?format=json&per_page=100&date=2010:2025")
    rows = requests.get(url, timeout=30).json()[1]
    wb = pd.DataFrame(rows)[["date", "value"]].dropna()
    wb["date"] = wb["date"].astype(int)
    ax.plot(wb.date, wb.value, marker="s", ls="--", color="#2980b9",
            label="Banque mondiale (estimation OIT)")
ax.axvspan(2019.5, 2020.5, alpha=0.15, color="grey")
ax.annotate("Covid-19 + sécheresse", (2020, serie.taux_chomage_pct.min() + 0.3), ha="center")
ax.set(title="Taux de chômage au Maroc, 2010-2025", xlabel="Année",
       ylabel="% de la population active (15 ans et +)")
ax.grid(alpha=0.3); ax.legend()
fig.tight_layout(); fig.savefig(OUT / "evolution_chomage.png", dpi=150)

# 4) Graphique 2 : inégalités par catégorie
c = cat.sort_values("taux_chomage_pct")
fig, ax = plt.subplots(figsize=(9, 5))
ax.barh(c.groupe + " (" + c.annee.astype(str) + ")", c.taux_chomage_pct, color="#34495e")
for y, v in enumerate(c.taux_chomage_pct):
    ax.text(v + 0.3, y, f"{v} %", va="center")
ax.set(title="Le chômage frappe surtout jeunes, femmes, diplômés et urbains",
       xlabel="Taux de chômage (%)")
fig.tight_layout(); fig.savefig(OUT / "chomage_par_categorie.png", dpi=150)
print("Graphiques enregistrés dans", OUT)
