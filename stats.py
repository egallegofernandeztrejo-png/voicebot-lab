import pandas as pd

df = pd.read_csv("data/llamadas.csv", parse_dates=["inicio"])

# 1. Distribución de resultados → SELECT resultado, COUNT(*)*100/total ... GROUP BY resultado
print("== Resultado global ==")
print((df["resultado"].value_counts(normalize=True) * 100).round(1))

# 2. Resultado por motivo → una tabla dinámica (motivo × resultado), en % por fila
print("\n== Resultado por motivo (%) ==")
print((pd.crosstab(df["motivo"], df["resultado"], normalize="index") * 100).round(0))

# 3. Espera media al agente, solo transferidas → WHERE + AVG
transferidas = df[df["resultado"] == "transferida"]
print(f"\nEspera media al agente: {transferidas['espera_agente_seg'].mean():.0f} s")



# 4 Reto (unos 10 min): saca el % de llamadas resueltas en IVR según fallos_reconocimiento. La pista es groupby("fallos_reconocimiento").
#  Hay un dato muy de IVR escondido ahí; cuéntame qué ves

print("\n== Llamadas resueltas en IVR según fallos de reconocimiento (%) ==")
por_fallos = df.groupby("fallos_reconocimiento")["resultado"].apply(
    lambda resultados: resultados.eq("resuelta_ivr").mean() * 100
).round(1)

print(por_fallos)