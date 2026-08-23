"""
Exporta las predicciones de tu modelo a los dos archivos JSON
que consume nfl_elo_interfaz.html (standings.json y matchups.json).

Corre este script desde la raíz de tu proyecto (NFL-Predictor/),
con el entorno venv311 activado.
"""
import pandas as pd
import json

# ------------------------------------------------------------------
# 1) Carga tus CSVs ya generados
# ------------------------------------------------------------------
posiciones_2026 = pd.read_csv('data/nfl_standings_2026.csv')
predicciones_2026 = pd.read_csv('data/nfl_predicciones_2026.csv')


print("Columnas de posiciones_2026:", posiciones_2026.columns.tolist())
print("Columnas de predicciones_2026:", predicciones_2026.columns.tolist())

# ------------------------------------------------------------------
# 2) Genera standings.json
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
# 3) Genera matchups.json (agrupado por semana)
# ------------------------------------------------------------------
matchups_por_semana = {}
for week, grupo in predicciones_2026.groupby('week'):
    matchups_por_semana[str(int(week))] = [
        {
            'home': row['home_team'],
            'away': row['away_team'],
            'homePct': round(row['prob_local'] * 100),
            'awayPct': round((1 - row['prob_local']) * 100)
        }
        for _, row in grupo.iterrows()
    ]

with open('matchups.json', 'w', encoding='utf-8') as f:
    json.dump(matchups_por_semana, f, ensure_ascii=False, indent=2)

print(f"matchups.json generado con {len(matchups_por_semana)} semanas")
