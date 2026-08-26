# NFL Elo Predictor 2026
 
> Modelo de predicción de la temporada NFL 2026 usando un sistema de rating Elo
> entrenado con 21 años de datos históricos, con simulación de playoffs y
> actualización automática semanal.
 
🔗 **[Ver demo en vivo](tu-link-aquí)**
 
## Qué hace
 
Este proyecto predice los resultados de la temporada NFL 2026 partido por
partido, proyecta la tabla de posiciones final, y estima la probabilidad de
cada equipo de llegar a playoffs — todo actualizado automáticamente cada
semana conforme se juegan los partidos reales.
 
## Metodología
 
### Sistema de rating Elo
 
Cada equipo tiene un rating numérico que representa su fuerza en un momento
dado. Se actualiza después de cada partido según qué tan sorprendente fue el
resultado — el mismo enfoque que usó FiveThirtyEight para NFL.
 
- **Rating inicial:** 1500
- **K-factor:** 20
- **Ventaja de local (HFA):** 65 puntos
- **Regresión a la media entre temporadas:** 2/3 del rating anterior + 1/3 de 1500
- **Ajuste por margen de victoria:** el cambio de rating se escala según qué
  tan grande fue el margen de la victoria (un multiplicador logarítmico sobre
  la diferencia de puntos), en vez de tratar por igual una victoria por 1
  punto y una por 30
### Simulación Monte Carlo para playoffs
 
En vez de una sola predicción fija por partido, la temporada completa se
simula 10,000 veces:
 
- En cada simulación, los resultados se deciden aleatoriamente según la
  probabilidad calculada para cada partido, y los ratings Elo se actualizan
  dinámicamente conforme avanza esa temporada simulada
- Al final de cada simulación se aplican las reglas de clasificación a
  playoffs (7 equipos por conferencia: 4 campeones de división + 3 wild cards)
- El resultado final es el % de simulaciones en las que cada equipo clasificó
**Nota de metodología:** los desempates de récord usan una versión
simplificada de 2 niveles (enfrentamiento directo, luego resolución
aleatoria), no las ~12 reglas oficiales completas de desempate de la NFL.
 
## Resultados de validación
 
Probado retrospectivamente contra temporadas ya jugadas:
 
- Precisión histórica global (2005-2025): **61.79%** *(actualiza este número
  si cambió tras incorporar el ajuste por margen de victoria)*
- Precisión temporada 2025: **60.21%**
## Funcionalidades de la interfaz
 
- Calendario semanal que distingue partidos ya jugados (marcador real + ✓/✗
  según si el modelo acertó) de partidos futuros (probabilidad de victoria)
- Tabla de posiciones proyectada, agrupada por conferencia y división, con
  probabilidad de playoffs por equipo
- Gráfica de evolución del rating Elo de cada equipo a lo largo de 21
  temporadas
- Fecha de "última actualización" visible
- Tema claro/oscuro
## Actualización automática
 
El pipeline completo — refrescar datos, recalcular el modelo Elo, generar
predicciones y exportar los archivos de la interfaz — corre automáticamente
cada semana vía GitHub Actions, sin intervención manual. El sitio en GitHub
Pages se redespliega solo cada vez que el pipeline actualiza los datos.
 
## Stack técnico
 
- **Python** (pandas, nfl_data_py) para el modelo, la validación y las
  simulaciones
- **HTML / CSS / JavaScript + Chart.js** para la interfaz
- **GitHub Actions** para la automatización semanal
- **GitHub Pages** para el despliegue
## Limitaciones y trabajo futuro
 
- No incorpora lesiones, cambios de roster ni jugadores rookies
- Los desempates de playoffs usan una versión simplificada, no las reglas
  oficiales completas de la NFL
- **Trabajo futuro:** comparar las predicciones del modelo contra las líneas
  de apuestas de Vegas, como benchmark adicional de validación
## Cómo correrlo localmente
 
1. Clona este repositorio
2. Crea un entorno virtual con **Python 3.11** (versiones más recientes
   tienen problemas de compatibilidad con las dependencias del proyecto)
3. Instala las dependencias: `pip install -r requirements.txt`
4. Corre el pipeline en orden: limpieza de datos → modelo Elo → predicciones
   → exportación
5. Sirve la carpeta de la interfaz con un servidor local (por ejemplo,
   `python -m http.server`) y ábrela en el navegador