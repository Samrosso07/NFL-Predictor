
# NFL Elo Predictor 2026
Modelo de predicción de la temporada NFL 2026 usando un sistema de rating Elo entrenado con 20 años de datos históricos.
## Metodología
Este proyecto usa un sistema de rating Elo (el mismo enfoque que usó
FiveThirtyEight para NFL) para estimar la fuerza de cada equipo a
partir de resultados históricos:
- Rating inicial: 1500
- K-factor: 20
- Ventaja de local: 65 puntos
- Regresión a la media entre temporadas: 2/3

## Resultados de validación
Probado retrospectivamente contra temporadas ya jugadas:
- Precisión histórica global (2005-2025): 61.79%
- Precisión temporada 2025: 60.21%

## Stack técnico
- Python (pandas, nfl_data_py) para el modelo
- HTML/CSS/JavaScript para la interfaz
- Desplegado en GitHub Pages

## Limitaciones y trabajo futuro
- No incorpora lesiones, cambios de roster, ni jugadores rookies
- Trabajo futuro: simulación Monte Carlo para probabilidad de
  playoffs, ajuste por margen de victoria

## Cómo correrlo localmente
[instrucciones breves: clonar, activar entorno, instalar dependencias,
correr el script de exportación, abrir con un servidor local]
