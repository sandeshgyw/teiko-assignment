import pandas as pd


df = pd.read_csv("cell-count.csv")

print("Shape:")
print(df.shape)

print("\nColumns:")
print(df.columns.tolist())

print("\nMissing values:")
print(df.isna().sum())

print("\nUnique samples:")

print(df["sample"].nunique())

print("\nUnique subjects:")

print(df["subject"].nunique())

samples_per_subject = df.groupby("subject")["sample"].count()

print("\nSamples per subject:")

print(samples_per_subject.value_counts()) 


