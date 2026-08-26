"""
Exporta el historial completo de rating Elo de cada equipo, partido a
partido, a lo largo de todas las temporadas disponibles.

Genera team_ratings.json, que consume la pestaña "Evolución de Rating"
de la interfaz (Mejora 3 - Fase H).

Corre este script desde la raíz de tu proyecto (NFL-Predictor/),
con el entorno venv311 activado.
"""
import pandas as pd
import json

df = pd.read_csv('data/nfl_historico_con_elo.csv')
df = df.sort_values(by=['season', 'week'])

equipos = sorted(set(df['home_team']) | set(df['away_team']))

historial_por_equipo = {}

for equipo in equipos:
    registros = []

    # Partidos donde el equipo fue local
    locales = df[df['home_team'] == equipo][['season', 'week', 'elo_local_post']]
    locales = locales.rename(columns={'elo_local_post': 'elo'})

    # Partidos donde el equipo fue visitante
    visitas = df[df['away_team'] == equipo][['season', 'week', 'elo_visita_post']]
    visitas = visitas.rename(columns={'elo_visita_post': 'elo'})

    combinado = pd.concat([locales, visitas]).sort_values(by=['season', 'week'])

    for _, row in combinado.iterrows():
        registros.append({
            'season': int(row['season']),
            'week': int(row['week']),
            'elo': round(float(row['elo']), 1)
        })

    historial_por_equipo[equipo] = registros

with open('team_ratings.json', 'w', encoding='utf-8') as f:
    json.dump(historial_por_equipo, f, ensure_ascii=False, indent=2)

print(f"team_ratings.json generado con {len(historial_por_equipo)} equipos")