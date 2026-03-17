"""Analyse simple d'annonces immobilières.

Ce script charge des annonces depuis ``annonces.csv``, calcule le prix au m²,
nettoie les données aberrantes, produit des statistiques de marché et classe
chaque annonce selon son positionnement relatif à la moyenne.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict

import matplotlib.pyplot as plt
import pandas as pd


INPUT_FILE = Path("annonces.csv")
OUTPUT_FILE = Path("resultat.csv")
HISTOGRAM_FILE = Path("histogramme_prix_m2.png")


def charger_et_preparer_donnees(csv_path: Path) -> pd.DataFrame:
    """Charge les annonces et applique le nettoyage demandé."""
    df = pd.read_csv(csv_path)

    # Suppression des lignes incomplètes.
    df = df.dropna(subset=["prix", "surface", "ville"])

    # Sécurise les types pour éviter les erreurs de calcul.
    df["prix"] = pd.to_numeric(df["prix"], errors="coerce")
    df["surface"] = pd.to_numeric(df["surface"], errors="coerce")
    df = df.dropna(subset=["prix", "surface"])

    # Évite les divisions par zéro et valeurs non pertinentes.
    df = df[df["surface"] > 0]

    # Calcul du prix au m² et filtrage des valeurs extrêmes.
    df["prix_m2"] = df["prix"] / df["surface"]
    df = df[df["prix_m2"] <= 15000]

    return df.reset_index(drop=True)


def classifier_annonce(prix_m2: float, moyenne_prix_m2: float) -> str:
    """Retourne la classification d'une annonce selon la moyenne du marché."""
    if prix_m2 < 0.9 * moyenne_prix_m2:
        return "sous-évalué"
    if prix_m2 <= 1.1 * moyenne_prix_m2:
        return "marché"
    return "surévalué"


def analyser_bien(prix: float, surface: float, moyenne_prix_m2: float) -> Dict[str, float | str]:
    """Analyse un bien et retourne prix estimé, écart marché et classification."""
    if surface <= 0:
        raise ValueError("La surface doit être strictement positive.")

    prix_m2 = prix / surface
    prix_estime = moyenne_prix_m2 * surface
    ecart_marche = prix - prix_estime
    classification = classifier_annonce(prix_m2, moyenne_prix_m2)

    return {
        "prix_estime": round(prix_estime, 2),
        "ecart_marche": round(ecart_marche, 2),
        "classification": classification,
    }


def afficher_resume(df: pd.DataFrame, moyenne: float, mediane: float, ecart_type: float) -> None:
    """Affiche un résumé des indicateurs dans la console."""
    print("=== Résumé Radar Immo V0 ===")
    print(f"Nombre d'annonces retenues : {len(df)}")
    print(f"Moyenne prix/m²          : {moyenne:.2f} €")
    print(f"Médiane prix/m²          : {mediane:.2f} €")
    print(f"Écart-type prix/m²       : {ecart_type:.2f} €")


def generer_histogramme(df: pd.DataFrame, output_path: Path) -> None:
    """Génère l'histogramme du prix au m²."""
    plt.figure(figsize=(8, 5))
    plt.hist(df["prix_m2"], bins=10, color="steelblue", edgecolor="black")
    plt.title("Distribution des prix au m²")
    plt.xlabel("Prix au m² (€)")
    plt.ylabel("Nombre d'annonces")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def main() -> None:
    """Point d'entrée principal du script."""
    df = charger_et_preparer_donnees(INPUT_FILE)

    if df.empty:
        raise ValueError("Aucune annonce exploitable après nettoyage.")

    moyenne = df["prix_m2"].mean()
    mediane = df["prix_m2"].median()
    ecart_type = df["prix_m2"].std()

    df["classification"] = df["prix_m2"].apply(lambda x: classifier_annonce(x, moyenne))

    afficher_resume(df, moyenne, mediane, ecart_type)

    # Exemple d'analyse d'un bien type à partir de la première annonce.
    exemple = analyser_bien(df.loc[0, "prix"], df.loc[0, "surface"], moyenne)
    print("\nExemple analyser_bien (première annonce) :")
    print(exemple)

    df.to_csv(OUTPUT_FILE, index=False)
    generer_histogramme(df, HISTOGRAM_FILE)

    print(f"\nRésultats sauvegardés dans : {OUTPUT_FILE}")
    print(f"Histogramme sauvegardé dans : {HISTOGRAM_FILE}")


if __name__ == "__main__":
    main()
