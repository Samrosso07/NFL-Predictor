"""
03_modelo_elo.py

Calcula ratings Elo partido a partido para todo el histórico (2005-2025),
aplicando ventaja de local (HFA) y regresión a la media entre temporadas.
Valida la precisión del modelo y guarda el historial con los ratings.
"""

import pandas as pd

K_FACTOR = 20
HFA = 65
ELO_INICIAL = 1500


def calcular_probabilidad(rating_local, rating_visita, hfa=HFA):
    diferencia = (rating_local + hfa) - rating_visita
    return 1 / (1 + 10 ** (-diferencia / 400))


def regresion_media(rating, elo_inicial=ELO_INICIAL):
    return (2 / 3 * rating) + (1 / 3 * elo_inicial)


def calcular_historial_elo(df):
    equipos = pd.concat([df["home_team"], df["away_team"]]).unique()
    ratings = {equipo: ELO_INICIAL for equipo in equipos}

    historial_elo = []
    temporada_actual = df["season"].min()

    for _, row in df.iterrows():
        if row["season"] > temporada_actual:
            for equipo in ratings:
                ratings[equipo] = regresion_media(ratings[equipo])
            temporada_actual = row["season"]

        equipo_local = row["home_team"]
        equipo_visita = row["away_team"]

        elo_local_pre = ratings[equipo_local]
        elo_visita_pre = ratings[equipo_visita]

        prob_local = calcular_probabilidad(elo_local_pre, elo_visita_pre)
        prob_visita = 1 - prob_local

        if row["result"] > 0:
            res_local, res_visita = 1, 0
        elif row["result"] < 0:
            res_local, res_visita = 0, 1
        else:
            res_local, res_visita = 0.5, 0.5

        ratings[equipo_local] = elo_local_pre + K_FACTOR * (res_local - prob_local)
        ratings[equipo_visita] = elo_visita_pre + K_FACTOR * (res_visita - prob_visita)

        registro = row.to_dict()
        registro["elo_local_pre"] = round(elo_local_pre, 2)
        registro["elo_visita_pre"] = round(elo_visita_pre, 2)
        registro["prob_local"] = round(prob_local, 4)
        registro["elo_local_post"] = round(ratings[equipo_local], 2)
        registro["elo_visita_post"] = round(ratings[equipo_visita], 2)

        historial_elo.append(registro)

    return pd.DataFrame(historial_elo)


def validar_modelo(df_historial):
    df_validar = df_historial[df_historial["result"] != 0].copy()

    df_validar["prediccion_correcta"] = (
        ((df_validar["prob_local"] > 0.5) & (df_validar["result"] > 0))
        | ((df_validar["prob_local"] < 0.5) & (df_validar["result"] < 0))
    )

    acierto_global = df_validar["prediccion_correcta"].mean() * 100
    print(f"🎯 Precisión Global Histórica (2005-2025): {acierto_global:.2f}%")

    acierto_2025 = df_validar[df_validar["season"] == 2025]["prediccion_correcta"].mean() * 100
    print(f"🎯 Precisión Temporada 2025: {acierto_2025:.2f}%")


def main(
    ruta_entrada="data/nfl_historico_clean.csv",
    ruta_salida="data/nfl_historico_con_elo.csv",
):
    df = pd.read_csv(ruta_entrada)
    df_historial = calcular_historial_elo(df)
    validar_modelo(df_historial)

    df_historial.to_csv(ruta_salida, index=False)
    print(f"💾 Historial con cálculo Elo guardado en '{ruta_salida}'")
    return df_historial


if __name__ == "__main__":
    main()