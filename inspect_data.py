import pandas as pd


df = pd.read_csv("cell-count.csv")

print("Shape:")
print(df.shape)

print("\nColumns:")
print(df.columns.tolist())

print("\nMissing values:")
print(df.isna().sum())
 
print("\nUnique subjects")
print(df["subject"].nunique())