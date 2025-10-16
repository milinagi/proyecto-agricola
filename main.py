# ==========================================
# PROYECTO AGRÍCOLA — JORGE ALBERTO RUIZ CABRERA
# ==========================================


import numpy as np
import pandas as pd
import os
from datetime import datetime, timedelta
import matplotlib.patheffects as path_effects
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import matplotlib as mpl
from utils_savefig import enable_autosave, disable_autosave


# Carga del CSV
CSV_PATH = "agricultura_dataset.csv"
assert os.path.exists(CSV_PATH), f"No se encontró el archivo en {CSV_PATH}. Archivos en la carpeta: {os.listdir('.')}"
print("✅ Archivo encontrado correctamente.")
print("------------------------------------------")

try:
    df = pd.read_csv(CSV_PATH, encoding="utf-8")
except UnicodeDecodeError:
    df = pd.read_csv(CSV_PATH, encoding="latin1")

print("✅ CSV cargado con éxito")
print("shape:", df.shape)
df.head()
print("------------------------------------------")


print(df.info())
print("------------------------------------------")

print(df.describe())
print("------------------------------------------")


df_duplicados = df.duplicated().sum()
print("Duplicados:", df_duplicados)

print("Nulos por columna:\n", df.isnull().sum())
print("------------------------------------------")


# Uniques informativos
if "Crop_Type" in df.columns:        print("Cultivos:", df["Crop_Type"].unique())
print()
if "Irrigation_Type" in df.columns:  print("Tipos de riego:", df["Irrigation_Type"].unique())
print()

if "Soil_Type" in df.columns:        print("Tipos de suelo:", df["Soil_Type"].unique())
print()

if "Season" in df.columns:           print("Estaciones:", df["Season"].unique())
print()

print("------------------------------------------")

if "Fertilizer_Used(kg/ha)" in df.columns:
    print("Tipo de fertilizante usado:", df["Fertilizer_Used(kg/ha)"].unique())
print()
 
print("------------------------------------------")
    
print("Nulos por columna (revisión):\n", df.isnull().sum())

print("------------------------------------------")

# 1) Perfilado de dataset
def perfilado_outliers_iqr(df):
    columnas_numericas = df.select_dtypes(include='number').columns
    conteo_atipicos = {}
    for col in columnas_numericas:
        q1, q3 = df[col].quantile([0.25, 0.75])
        iqr = q3 - q1
        lim_inf, lim_sup = q1 - 1.5*iqr, q3 + 1.5*iqr
        conteo_atipicos[col] = int(((df[col] < lim_inf) | (df[col] > lim_sup)).sum())
    print("\n=== Outliers por IQR ===")
    print(pd.Series(conteo_atipicos))

perfilado_outliers_iqr(df)

print("------------------------------------------")

# 2) Aplicación de reglas simples de validación
def validar_rangos_basicos(df):
    reglas = {
        "Farm_Area(ha)": (0.1, 10000),
        "Water_Usage(m³)": (0, 1_000_000),
        "Fertilizer_Used(kg/ha)": (0, 2000),
        "Pesticide_Used(kg/ha)": (0, 200),
        "Rainfall(mm)": (0, 5000),
        "Temperature(°C)": (-10, 50),
        "Yield(tons/ha)": (0, 200),
        "Profit(€)": (-1e9, 1e12),
    }
    fuera = {}
    for col, (lo, hi) in reglas.items():
        if col in df.columns:
            fuera[col] = int((~df[col].between(lo, hi)).sum())
    print("\n=== Validación de rangos ===")
    print(pd.Series(fuera))

validar_rangos_basicos(df)

print("------------------------------------------")

# 3) Limpieza básica
df.drop_duplicates(inplace=True)



print("\n✅ Features creadas (si existían columnas): Water_per_ha, Profit_per_ha")

print("------------------------------------------")

# 4) Creación de 2–3 gráficos claros y accesibles
def CropAndYield():
    data = (df.groupby("Crop_Type")["Yield(tons/ha)"]
              .mean()
              .sort_values(ascending=False)
              .head(10))

    norm = mcolors.Normalize(vmin=data.min(), vmax=data.max())
    cmap = mpl.colormaps['viridis']
    colores = [cmap(norm(value)) for value in data]

    fig, ax = plt.subplots(figsize=(8,5))
    bars = ax.bar(data.index, data.values, color=colores)

    ax.set_ylabel("Rendimiento medio (tons/ha)")
    ax.set_xlabel("PROYECTO BÁSICO JORGE RUIZ")
    ax.set_title("Top 10 cultivos por rendimiento promedio")

    sm = cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=ax)
    cbar.set_label("Rendimiento (tons/ha)")

    fig.tight_layout()
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    plt.show()

def CropAndYield_pie():
    data = (df.groupby("Crop_Type")["Temperature(°C)"]
              .mean()
              .sort_values(ascending=False)
              .head(6))

    norm = mcolors.Normalize(vmin=data.min(), vmax=data.max())
    cmap = mpl.colormaps['viridis'] 
    colores = [cmap(norm(v)) for v in data.values]

    labels = data.index
    values = data.values

    fig, ax = plt.subplots(figsize=(8, 5))
    wedges, texts, autotexts = ax.pie(
        values, labels=labels, colors=colores,
        autopct="%1.1f%%", startangle=90,
        wedgeprops=dict(width=0.45, edgecolor="white", linewidth=1),
        pctdistance=0.8
    )

    for autotext in autotexts:
        autotext.set_color("Black")
        autotext.set_fontsize(10)
        autotext.set_weight("bold")
        autotext.set_path_effects([
            path_effects.Stroke(linewidth=2.5, foreground="white"),
            path_effects.Normal()
        ])

    ax.set_title("Top 6 cultivos por temperatura")
    ax.axis("equal")
    ax.text(0, 0, "TEMPERATURA", ha="center", va="center", fontsize=10)
    plt.tight_layout()
    plt.show()

def dashboard_agricola(df):
    YIELD = "Yield(tons/ha)"
    WATER = "Water_Usage(m³)"
    AREA  = "Farm_Area(ha)"
    SOIL  = "Soil_Type"
    CROP  = "Crop_Type"
    PROFIT = "Profit(€)"

    # Top-5 por beneficio
    s_top = (df.groupby(CROP)[PROFIT]
               .mean()
               .sort_values(ascending=False)
               .head(5))

    # Agua por hectárea
    df = df.copy()
    df["Water_per_ha"] = df[WATER] / df[AREA]
    xy = df[["Water_per_ha", YIELD]].dropna()

    fig, axes = plt.subplots(1, 3, figsize=(16, 6))

    # Barras: Profit por cultivo
    ax = axes[0]
    bars = ax.bar(s_top.index, s_top.values)
    ax.set_title("Cultivo VS Profit")
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    for b in bars:
        h = b.get_height()
        ax.text(b.get_x() + b.get_width()/2, h, f"{h:.1f}€",
                ha="center", va="bottom", fontsize=9)

    # Dispersión: Agua/ha vs Rendimiento
    ax = axes[1]
    ax.scatter(xy["Water_per_ha"], xy[YIELD], alpha=0.6)
    ax.set_title("Agua Por ha vs Rendimiento")
    ax.grid(True, linestyle="--", alpha=0.4)
    if len(xy) >= 2:
        z = np.polyfit(xy["Water_per_ha"], xy[YIELD], 1)
        xp = np.linspace(xy["Water_per_ha"].min(), xy["Water_per_ha"].max(), 100)
        yp = z[0]*xp + z[1]
        ax.plot(xp, yp)

    # Boxplot: Rendimiento por suelo
    ax = axes[2]
    order = ["Arenoso", "Arcilloso", "Franco", "Volcánico"]
    order = [s for s in order if s in df[SOIL].unique()]
    data_by_soil = [df.loc[df[SOIL] == s, YIELD].values for s in order]
    ax.boxplot(data_by_soil, tick_labels=order, showfliers=True)
    ax.set_title("Rendimiento Vs Tipo De Suelo")
    ax.grid(axis="y", linestyle="--", alpha=0.4)

    plt.tight_layout()
    plt.show()

# Guarda las imágenes en una carpeta
def main():
    enable_autosave(dirpath="outputs", prefix="fig", dpi=150)
    try:
        CropAndYield()
        CropAndYield_pie()
        dashboard_agricola(df)
    finally:
        disable_autosave()

if __name__ == "__main__":
    main()