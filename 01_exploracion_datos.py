"""
01_exploracion_datos.py

Descarga el histórico de partidos NFL (2005-2025) y el calendario de la
temporada 2026 usando nfl_data_py, y los guarda como CSV para las
siguientes etapas del pipeline.
"""

import pandas as pd
import nfl_data_py as nfl
import os

os.makedirs('data', exist_ok=True)

FEATURES = [
    "game_id", "season", "game_type", "week",
    "away_team", "away_score", "home_team", "home_score", "result",
]


def descargar_historico(years, ruta_salida="data/nfl_partidos_historico.csv"):
    schedules = nfl.import_schedules(years)
    print(f"Partidos cargados: {len(schedules)}")

    schedules[FEATURES].to_csv(ruta_salida, index=False)
    return schedules[FEATURES]


def descargar_calendario_2026(ruta_salida="data/nfl_calendario_2026.csv"):
    schedule_2026 = nfl.import_schedules([2026])
    sch_reg_2026 = schedule_2026[schedule_2026["game_type"] == "REG"].copy()

    total_partidos_2026 = len(sch_reg_2026)
    partidos_pendientes = sch_reg_2026["home_score"].isna().sum()

    print(f"🏈 Partidos de temporada regular 2026 encontrados: {total_partidos_2026} (Esperados: 272)")
    print(f"⏳ Partidos pendientes por jugar (sin marcador): {partidos_pendientes}")

    sch_reg_2026.to_csv(ruta_salida, index=False)
    return sch_reg_2026


if __name__ == "__main__":
    years = list(range(2005, 2026))
    descargar_historico(years)
    descargar_calendario_2026()