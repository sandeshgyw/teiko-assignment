import sqlite3

import pandas as pd
from scipy.stats import mannwhitneyu
from statsmodels.stats.multitest import multipletests
import matplotlib.pyplot as plt

DATABASE_FILE = "cell_counts.db"


connection = sqlite3.connect(DATABASE_FILE)

query = """
    SELECT
        s.subject_id,
        s.sample_id AS sample,
        s.sample_type,
        s.time_from_treatment_start,
        sub.condition,
        sub.treatment,
        sub.response,
        c.population,
        c.count,
        c.count * 100.0 /
            SUM(c.count) OVER (PARTITION BY s.sample_id) AS percentage
    FROM samples s
    JOIN subjects sub
        ON s.subject_id = sub.subject_id
    JOIN cell_counts c
        ON s.sample_id = c.sample_id
    WHERE sub.condition = 'melanoma'
        AND sub.treatment = 'miraclib'
        AND s.sample_type = 'PBMC'
"""

dataframe = pd.read_sql_query(query, connection)

connection.close()


print("Rows:", len(dataframe))

print("\nUnique subjects:")
print(dataframe["subject_id"].nunique())

print("\nSubjects by response:")
print(
    dataframe.groupby("response")["subject_id"]
    .nunique()
)

print("\nSamples by response:")
print(
    dataframe.groupby("response")["sample"]
    .nunique()
)

print("\nTime points:")
print(
    dataframe["time_from_treatment_start"]
    .value_counts()
    .sort_index()
)


subject_frequencies = (
    dataframe.groupby(
        ["subject_id", "response", "population"],
        as_index=False,
    )["percentage"]
    .mean()
)

print("\nSubject-level frequency data:")
print(subject_frequencies.head())

print("\nRows:", len(subject_frequencies))

print("\nSubjects represented:")
print(subject_frequencies["subject_id"].nunique())


populations = subject_frequencies["population"].unique()

results = []

for population in populations:
    population_data = subject_frequencies[
        subject_frequencies["population"] == population
    ]

    responders = population_data[
        population_data["response"] == "yes"
    ]["percentage"]

    nonresponders = population_data[
        population_data["response"] == "no"
    ]["percentage"]

    statistic, p_value = mannwhitneyu(
        responders,
        nonresponders,
        alternative="two-sided",
    )

    results.append(
        {
            "population": population,
            "responder_median": responders.median(),
            "nonresponder_median": nonresponders.median(),
            "u_statistic": statistic,
            "p_value": p_value,
        }
    )


results_dataframe = pd.DataFrame(results)

reject, adjusted_p_values, _, _ = multipletests(
    results_dataframe["p_value"],
    alpha=0.05,
    method="fdr_bh",
)

results_dataframe["adjusted_p_value"] = adjusted_p_values
results_dataframe["significant"] = reject

print("\nStatistical results:")
print(results_dataframe)

results_dataframe.to_csv(
    "statistical_results.csv",
    index=False,
)


fig, axes = plt.subplots(
    nrows=1,
    ncols=len(populations),
    figsize=(16, 5),
    sharey=True,
)

for axis, population in zip(axes, populations):
    population_data = subject_frequencies[
        subject_frequencies["population"] == population
    ]

    responders = population_data[
        population_data["response"] == "yes"
    ]["percentage"]

    nonresponders = population_data[
        population_data["response"] == "no"
    ]["percentage"]

    axis.boxplot(
        [responders, nonresponders],
        tick_labels=["Responder", "Nonresponder"],
    )

    axis.set_title(population)
    axis.set_xlabel("Response")

axes[0].set_ylabel("Relative frequency (%)")

fig.suptitle(
    "Immune Cell Relative Frequencies by Treatment Response"
)

fig.tight_layout()

plt.savefig(
    "response_boxplots.png",
    dpi=300,
    bbox_inches="tight",
)

plt.close()

print("\nBoxplots saved: response_boxplots.png")