"""
04_predicciones_2026.py

A partir de los ratings Elo finales de 2025 (regresados a la media),
predice el resultado de cada partido de la temporada 2026 y proyecta la
tabla de posiciones (victorias/derrotas esperadas) por equipo, conferencia
y división.
"""

import pandas as pd

NFL_ESTRUCTURA = {
    # AFC EAST
    "BUF": {"conferencia": "AFC", "division": "AFC East"},
    "MIA": {"conferencia": "AFC", "division": "AFC East"},
    "NE": {"conferencia": "AFC", "division": "AFC East"},
    "NYJ": {"conferencia": "AFC", "division": "AFC East"},
    # AFC NORTH
    "BAL": {"conferencia": "AFC", "division": "AFC North"},
    "CIN": {"conferencia": "AFC", "division": "AFC North"},
    "CLE": {"conferencia": "AFC", "division": "AFC North"},
    "PIT": {"conferencia": "AFC", "division": "AFC North"},
    # AFC SOUTH
    "HOU": {"conferencia": "AFC", "division": "AFC South"},
    "IND": {"conferencia": "AFC", "division": "AFC South"},
    "JAX": {"conferencia": "AFC", "division": "AFC South"},
    "TEN": {"conferencia": "AFC", "division": "AFC South"},
    # AFC WEST
    "DEN": {"conferencia": "AFC", "division": "AFC West"},
    "KC": {"conferencia": "AFC", "division": "AFC West"},
    "LV": {"conferencia": "AFC", "division": "AFC West"},
    "LAC": {"conferencia": "AFC", "division": "AFC West"},
    # NFC EAST
    "DAL": {"conferencia": "NFC", "division": "NFC East"},
    "NYG": {"conferencia": "NFC", "division": "NFC East"},
    "PHI": {"conferencia": "NFC", "division": "NFC East"},
    "WAS": {"conferencia": "NFC", "division": "NFC East"},
    # NFC NORTH
    "CHI": {"conferencia": "NFC", "division": "NFC North"},
    "DET": {"conferencia": "NFC", "division": "NFC North"},
    "GB": {"conferencia": "NFC", "division": "NFC North"},
    "MIN": {"conferencia": "NFC", "division": "NFC North"},
    # NFC SOUTH
    "ATL": {"conferencia": "NFC", "division": "NFC South"},
    "CAR": {"conferencia": "NFC", "division": "NFC South"},
    "NO": {"conferencia": "NFC", "division": "NFC South"},
    "TB": {"conferencia": "NFC", "division": "NFC South"},
    # NFC WEST
    "ARI": {"conferencia": "NFC", "division": "NFC West"},
    "LA": {"conferencia": "NFC", "division": "NFC West"},
    "SF": {"conferencia": "NFC", "division": "NFC West"},
    "SEA": {"conferencia": "NFC", "division": "NFC West"},
}


def regresion_media(rating, elo_inicial=1500):
    return (2 / 3 * rating) + (1 / 3 * elo_inicial)


def calcular_probabilidad(rating_local, rating_visita, hfa=65):
    diferencia = (rating_local + hfa) - rating_visita
    return 1 / (1 + 10 ** (-diferencia / 400))


def calcular_elo_arranque_2026(df_hist):
    equipos = set(df_hist["home_team"]).union(set(df_hist["away_team"]))
    elo_2025_final = {}

    for equipo in equipos:
        df_equipo = df_hist[(df_hist["home_team"] == equipo) | (df_hist["away_team"] == equipo)]
        ultimo_juego = df_equipo.iloc[-1]

        if ultimo_juego["home_team"] == equipo:
            elo_2025_final[equipo] = ultimo_juego["elo_local_post"]
        else:
            elo_2025_final[equipo] = ultimo_juego["elo_visita_post"]

    return {eq: round(regresion_media(rat), 2) for eq, rat in elo_2025_final.items()}, equipos


def predecir_temporada_2026(df_2026, elo_arranque):
    predicciones_2026 = []

    for _, row in df_2026.iterrows():
        eq_local = row["home_team"]
        eq_visita = row["away_team"]

        elo_local = elo_arranque.get(eq_local, 1500)
        elo_visita = elo_arranque.get(eq_visita, 1500)

        prob_local = calcular_probabilidad(elo_local, elo_visita)

        predicciones_2026.append({
            "season": row["season"],
            "week": row["week"],
            "home_team": eq_local,
            "away_team": eq_visita,
            "prob_local": round(prob_local, 4),
            "prob_visita": round(1 - prob_local, 4),
        })

    df_predicciones = pd.DataFrame(predicciones_2026)
    print(f"🏈 {len(df_predicciones)} partidos de 2026 simulados.")
    return df_predicciones


def calcular_standings(df_predicciones, equipos):
    victorias_esperadas = {equipo: 0.0 for equipo in equipos}

    for _, row in df_predicciones.iterrows():
        victorias_esperadas[row["home_team"]] += row["prob_local"]
        victorias_esperadas[row["away_team"]] += row["prob_visita"]

    df_standings = pd.DataFrame([
        {
            "Equipo": eq,
            "Victorias_Proyectadas": round(wins, 1),
            "Derrotas_Proyectadas": round(17 - wins, 1),
        }
        for eq, wins in victorias_esperadas.items()
    ]).sort_values(by="Victorias_Proyectadas", ascending=False)

    df_standings["Conferencia"] = df_standings["Equipo"].map(lambda x: NFL_ESTRUCTURA[x]["conferencia"])
    df_standings["Division"] = df_standings["Equipo"].map(lambda x: NFL_ESTRUCTURA[x]["division"])
    df_standings = df_standings[["Equipo", "Conferencia", "Division", "Victorias_Proyectadas", "Derrotas_Proyectadas"]]

    return df_standings


def main(
    ruta_historico_elo="data/nfl_historico_con_elo.csv",
    ruta_calendario_2026="data/nfl_calendario_2026_clean.csv",
    ruta_predicciones="data/nfl_predicciones_2026.csv",
    ruta_standings="data/nfl_standings_2026.csv",
):
    df_hist = pd.read_csv(ruta_historico_elo)
    elo_arranque, equipos = calcular_elo_arranque_2026(df_hist)
    print("✅ Ratings ajustados para el inicio de 2026 listos.")

    df_2026 = pd.read_csv(ruta_calendario_2026)
    df_predicciones = predecir_temporada_2026(df_2026, elo_arranque)
    df_predicciones.to_csv(ruta_predicciones, index=False)

    df_standings = calcular_standings(df_predicciones, equipos)
    df_standings.to_csv(ruta_standings, index=False)

    return df_predicciones, df_standings


if __name__ == "__main__":
    main()