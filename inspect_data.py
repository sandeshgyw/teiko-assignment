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

subject_columns = [
    "project",
    "condition",
    "age",
    "sex",
    "treatment",
    "response",
]

print("\nMaximum unique values per subject:")

for column in subject_columns:
    max_unique = df.groupby("subject")[column].nunique(dropna=False).max()
    print(f"{column}: {max_unique}")

print("\nSample types per subject:")
print(df.groupby("subject")["sample_type"].nunique().value_counts())

print("\nTime points per subject:")
print(df.groupby("subject")["time_from_treatment_start"].nunique().value_counts())


