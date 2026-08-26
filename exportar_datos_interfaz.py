"""
Exporta las predicciones de tu modelo a los archivos JSON que consume
nfl_elo_interfaz.html (standings.json, matchups.json y meta.json).

Corre este script desde la raíz de tu proyecto (NFL-Predictor/),
con el entorno venv311 activado.
"""
import pandas as pd
import json
from datetime import datetime, timezone

# ------------------------------------------------------------------
# 1) Carga tus CSVs ya generados
# ------------------------------------------------------------------
posiciones_2026 = pd.read_csv('data/nfl_standings_2026.csv')
predicciones_2026 = pd.read_csv('data/nfl_predicciones_2026.csv')
# Trae los marcadores reales (NaN si el partido aún no se ha jugado)
calendario_2026 = pd.read_csv('data/nfl_calendario_2026_clean.csv')

print("Columnas de posiciones_2026:", posiciones_2026.columns.tolist())
print("Columnas de predicciones_2026:", predicciones_2026.columns.tolist())

# ------------------------------------------------------------------
# 2) Genera standings.json
#    (montecarlo.py corre después y le agrega el campo po_pct)
# ------------------------------------------------------------------
standings_dict = {}
for _, row in posiciones_2026.iterrows():
    victorias = row['Victorias_Proyectadas']
    equipo = row['Equipo']
    standings_dict[equipo] = {
        'w': round(victorias, 1),
        'l': round(17 - victorias, 1)
    }

with open('standings.json', 'w', encoding='utf-8') as f:
    json.dump(standings_dict, f, ensure_ascii=False, indent=2)

print(f"standings.json generado con {len(standings_dict)} equipos")

# ------------------------------------------------------------------
# 3) Cruzar predicciones con marcadores reales (Mejora 1 - Fase H)
# ------------------------------------------------------------------
cols_marcador = ['season', 'week', 'home_team', 'away_team', 'home_score', 'away_score']
predicciones_2026 = predicciones_2026.merge(
    calendario_2026[cols_marcador],
    on=['season', 'week', 'home_team', 'away_team'],
    how='left'
)


def evaluar_partido(row):
    """Determina si el partido ya se jugó y si el modelo acertó al favorito."""
    jugado = pd.notna(row['home_score']) and pd.notna(row['away_score'])
    if not jugado:
        return pd.Series({'jugado': False, 'homeScore': None, 'awayScore': None, 'acierto': None})

    home_score = int(row['home_score'])
    away_score = int(row['away_score'])

    if home_score == away_score:
        acierto = None  # empate: no aplica acierto/fallo
    else:
        favorito_local = row['prob_local'] > 0.5
        gano_local = home_score > away_score
        acierto = favorito_local == gano_local

    return pd.Series({
        'jugado': True,
        'homeScore': home_score,
        'awayScore': away_score,
        'acierto': acierto
    })


predicciones_2026 = predicciones_2026.join(predicciones_2026.apply(evaluar_partido, axis=1))

# ------------------------------------------------------------------
# 4) Genera matchups.json (agrupado por semana)
# ------------------------------------------------------------------
matchups_por_semana = {}
for week, grupo in predicciones_2026.groupby('week'):
    matchups_por_semana[str(int(week))] = [
        {
            'home': row['home_team'],
            'away': row['away_team'],
            'homePct': round(row['prob_local'] * 100),
            'awayPct': round((1 - row['prob_local']) * 100),
            'jugado': bool(row['jugado']),
            'homeScore': row['homeScore'] if pd.notna(row['homeScore']) else None,
            'awayScore': row['awayScore'] if pd.notna(row['awayScore']) else None,
            'acierto': row['acierto'] if pd.notna(row['acierto']) else None,
        }
        for _, row in grupo.iterrows()
    ]

with open('matchups.json', 'w', encoding='utf-8') as f:
    json.dump(matchups_por_semana, f, ensure_ascii=False, indent=2)

print(f"matchups.json generado con {len(matchups_por_semana)} semanas")


with open('meta.json', 'w', encoding='utf-8') as f:
    json.dump({'last_updated': datetime.now(timezone.utc).isoformat()}, f, indent=2)

print("meta.json generado (timestamp intermedio)")