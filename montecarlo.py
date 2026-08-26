import pandas as pd
import numpy as np
import random
import json
from datetime import datetime, timezone

# 1. Parámetros Iniciales y Diccionario de la Liga
ITERACIONES = 10000
K_FACTOR = 20
HFA = 65

# Estructura de la NFL para clasificar divisiones
nfl_estructura = {
    'BUF': {'conf': 'AFC', 'div': 'East'}, 'MIA': {'conf': 'AFC', 'div': 'East'},
    'NE':  {'conf': 'AFC', 'div': 'East'}, 'NYJ': {'conf': 'AFC', 'div': 'East'},
    'BAL': {'conf': 'AFC', 'div': 'North'},'CIN': {'conf': 'AFC', 'div': 'North'},
    'CLE': {'conf': 'AFC', 'div': 'North'},'PIT': {'conf': 'AFC', 'div': 'North'},
    'HOU': {'conf': 'AFC', 'div': 'South'},'IND': {'conf': 'AFC', 'div': 'South'},
    'JAX': {'conf': 'AFC', 'div': 'South'},'TEN': {'conf': 'AFC', 'div': 'South'},
    'DEN': {'conf': 'AFC', 'div': 'West'}, 'KC':  {'conf': 'AFC', 'div': 'West'},
    'LV':  {'conf': 'AFC', 'div': 'West'}, 'LAC': {'conf': 'AFC', 'div': 'West'},
    'DAL': {'conf': 'NFC', 'div': 'East'}, 'NYG': {'conf': 'NFC', 'div': 'East'},
    'PHI': {'conf': 'NFC', 'div': 'East'}, 'WAS': {'conf': 'NFC', 'div': 'East'},
    'CHI': {'conf': 'NFC', 'div': 'North'},'DET': {'conf': 'NFC', 'div': 'North'},
    'GB':  {'conf': 'NFC', 'div': 'North'},'MIN': {'conf': 'NFC', 'div': 'North'},
    'ATL': {'conf': 'NFC', 'div': 'South'},'CAR': {'conf': 'NFC', 'div': 'South'},
    'NO':  {'conf': 'NFC', 'div': 'South'},'TB':  {'conf': 'NFC', 'div': 'South'},
    'ARI': {'conf': 'NFC', 'div': 'West'}, 'LA':  {'conf': 'NFC', 'div': 'West'},
    'SF':  {'conf': 'NFC', 'div': 'West'}, 'SEA': {'conf': 'NFC', 'div': 'West'}
}

# 2. Cargar Datos Base
print("Cargando datos base...")
df_hist = pd.read_csv("data/nfl_historico_con_elo.csv")
df_cal = pd.read_csv("data/nfl_calendario_2026_clean.csv")

# Extraer Elo base 2026 (reseteado)
equipos = list(nfl_estructura.keys())
elo_2026_arranque = {}
for eq in equipos:
    ultimo = df_hist[(df_hist['home_team'] == eq) | (df_hist['away_team'] == eq)].iloc[-1]
    rating_previo = ultimo['elo_local_post'] if ultimo['home_team'] == eq else ultimo['elo_visita_post']
    elo_2026_arranque[eq] = (2/3 * rating_previo) + (1/3 * 1500) # Regresión media

# 3. Funciones Base
def calcular_prob(rating_local, rating_visita):
    diferencia = (rating_local + HFA) - rating_visita
    return 1 / (1 + 10 ** (-diferencia / 400))

def resolver_desempate(eq_a, eq_b, resultados_sim):
    # Regla 1: Enfrentamiento directo (simplificado)
    if (eq_a, eq_b) in resultados_sim and resultados_sim[(eq_a, eq_b)] == 1:
        return eq_a
    elif (eq_b, eq_a) in resultados_sim and resultados_sim[(eq_b, eq_a)] == 1:
        return eq_b
    # Regla 2: Aleatorio
    return eq_a if random.random() > 0.5 else eq_b

# 4. El Motor Monte Carlo
playoffs_counter = {eq: 0 for eq in equipos}
victorias_totales = {eq: 0 for eq in equipos}

print(f"Iniciando {ITERACIONES} simulaciones. Esto tomará un par de minutos...")

for i in range(ITERACIONES):
    # Reiniciar ratings y récords para ESTA simulación específica[cite: 5]
    ratings_sim = elo_2026_arranque.copy()
    wins_sim = {eq: 0 for eq in equipos}
    h2h_sim = {} # Historial head-to-head

    # A. Simular temporada completa partido a partido[cite: 5]
    for _, row in df_cal.iterrows():
        local = row['home_team']
        visita = row['away_team']
        
        prob_local = calcular_prob(ratings_sim[local], ratings_sim[visita])
        
        # Tirar la moneda[cite: 5]
        if random.random() < prob_local:
            wins_sim[local] += 1
            h2h_sim[(local, visita)] = 1
            res_local = 1
        else:
            wins_sim[visita] += 1
            h2h_sim[(visita, local)] = 1
            res_local = 0
            
        # Actualizar Elo dinámico dentro de la simulación[cite: 5]
        prob_visita = 1 - prob_local
        res_visita = 1 - res_local
        ratings_sim[local] += K_FACTOR * (res_local - prob_local)
        ratings_sim[visita] += K_FACTOR * (res_visita - prob_visita)
        
    # B. Aplicar reglas de Playoffs por conferencia[cite: 5]
    clasificados_sim = []
    
    for conf in ['AFC', 'NFC']:
        campeones_division = []
        resto_conferencia = []
        
        # 1. Sacar campeones de división (4 por conferencia)[cite: 5]
        for div in ['East', 'North', 'South', 'West']:
            equipos_div = [eq for eq in equipos if nfl_estructura[eq]['conf'] == conf and nfl_estructura[eq]['div'] == div]
            # Ordenar por victorias, resolviendo desempates si es necesario[cite: 5]
            # (Simplificamos usando una lógica básica de ordenamiento para este MVP)
            equipos_div.sort(key=lambda x: wins_sim[x], reverse=True)
            campeones_division.append(equipos_div[0])
            
            # Guardar a los no campeones para pelear los wildcards
            resto_conferencia.extend(equipos_div[1:])
            
        clasificados_sim.extend(campeones_division)
        
        # 2. Sacar 3 Wildcards[cite: 5]
        resto_conferencia.sort(key=lambda x: wins_sim[x], reverse=True)
        clasificados_sim.extend(resto_conferencia[:3])
        
    # C. Registrar quienes pasaron en ESTA iteración[cite: 5]
    for eq in clasificados_sim:
        playoffs_counter[eq] += 1
    
    # Acumular victorias para sacar el promedio
    for eq in equipos:
        victorias_totales[eq] += wins_sim[eq]

# 5. Generar JSON Final para la Interfaz
print("Calculando probabilidades finales...")
datos_json = []
for eq in equipos:
    win_avg = victorias_totales[eq] / ITERACIONES
    po_pct = (playoffs_counter[eq] / ITERACIONES) * 100
    
    datos_json.append({
        "abbr": eq,
        "conf": nfl_estructura[eq]['conf'],
        "div": nfl_estructura[eq]['div'],
        "w": round(win_avg, 1),
        "l": round(17 - win_avg, 1),
        "po_pct": round(po_pct, 1) # La nueva columna requerida[cite: 5]
    })

# Guardar
with open('standings.json', 'w') as f:
    json.dump(datos_json, f, indent=2)

print("✅ standings.json generado con éxito.")

# 6. Marca de tiempo final del pipeline (Mejora 2 - Fase H)
# Este es el último paso del pipeline, así que esta fecha es la real
# "última actualización" que debe mostrar la interfaz.
with open('meta.json', 'w') as f:
    json.dump({'last_updated': datetime.now(timezone.utc).isoformat()}, f, indent=2)

print("✅ meta.json actualizado con la fecha final del pipeline.")