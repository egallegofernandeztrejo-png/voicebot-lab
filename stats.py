import pandas as pd

df = pd.read_csv("data/llamadas.csv", parse_dates=["inicio"])

print(df.shape)       # (filas, columnas)
print(df.head())      # las 5 primeras
print(df.dtypes)      # tipos que ha inferido