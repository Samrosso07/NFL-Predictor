"""
02_limpieza_datos.py

Estandariza los códigos de franquicias (equipos que se mudaron/renombraron),
filtra las columnas relevantes para el modelo Elo y elimina partidos sin
marcador (cancelaciones). Guarda los datasets limpios listos para el modelo.
"""

import pandas as pd

MAPEO_EQUIPOS = {
    "STL": "LA",
    "SD": "LAC",
    "OAK": "LV",
    "WSH": "WAS",
    "LAR": "LA",
}

COLUMNAS_ELO = [
    "season",
    "week",
    "game_type",
    "home_team",
    "away_team",
    "home_score",
    "away_score",
    "result",  # home_score - away_score
]


def estandarizar(df, mapeo=MAPEO_EQUIPOS):
    df_clean = df.copy()
    df_clean["home_team"] = df_clean["home_team"].map(mapeo).fillna(df_clean["home_team"])
    df_clean["away_team"] = df_clean["away_team"].map(mapeo).fillna(df_clean["away_team"])
    return df_clean


def limpiar_datos(
    ruta_historico="data/nfl_partidos_historico.csv",
    ruta_2026="data/nfl_calendario_2026.csv",
    ruta_hist_clean="data/nfl_historico_clean.csv",
    ruta_2026_clean="data/nfl_calendario_2026_clean.csv",
):
    df_historico = pd.read_csv(ruta_historico)
    df_2026 = pd.read_csv(ruta_2026)

    df_historico_clean = estandarizar(df_historico)
    df_2026_clean = estandarizar(df_2026)

    equipos_hist = set(df_historico_clean["home_team"]) | set(df_historico_clean["away_team"])
    equipos_2026 = set(df_2026_clean["home_team"]) | set(df_2026_clean["away_team"])
    if equipos_hist != equipos_2026:
        print("⚠️ Diferencias de equipos entre datasets:")
        print(f"En histórico pero no en 2026: {equipos_hist - equipos_2026}")
        print(f"En 2026 pero no en histórico: {equipos_2026 - equipos_hist}")

    df_historico_elo = df_historico_clean[COLUMNAS_ELO].copy()
    df_historico_elo = df_historico_elo.sort_values(by=["season", "week"])

    antes = len(df_historico_elo)
    df_historico_elo = df_historico_elo.dropna(subset=["home_score", "away_score"])
    print(f"🧹 Partidos eliminados por valores nulos (cancelaciones): {antes - len(df_historico_elo)}")

    df_2026_elo = df_2026_clean[COLUMNAS_ELO].copy()

    df_historico_elo.to_csv(ruta_hist_clean, index=False)
    df_2026_elo.to_csv(ruta_2026_clean, index=False)
    print("💾 Archivos limpios guardados exitosamente.")

    return df_historico_elo, df_2026_elo


if __name__ == "__main__":
    limpiar_datos()