import sqlite3
from pathlib import Path

import pandas as pd


CSV_FILE = Path("cell-count.csv")
SCHEMA_FILE = Path("schema.sql")
DATABASE_FILE = Path("cell_counts.db")

CELL_POPULATIONS = [
    "b_cell",
    "cd8_t_cell",
    "cd4_t_cell",
    "nk_cell",
    "monocyte",
]


def create_database():
    connection = sqlite3.connect(DATABASE_FILE)

    with open(SCHEMA_FILE, "r") as schema_file:
        schema_sql = schema_file.read()

    connection.executescript(schema_sql)

    return connection


def load_subjects(connection, dataframe):
    subject_columns = [
        "subject",
        "project",
        "condition",
        "age",
        "sex",
        "treatment",
        "response",
    ]

    subjects = dataframe[subject_columns].drop_duplicates(
        subset=["subject"]
    )

    subjects = subjects.rename(
        columns={"subject": "subject_id"}
    )

    subjects.to_sql(
        "subjects",
        connection,
        if_exists="append",
        index=False,
    )


def load_samples(connection, dataframe):
    samples = dataframe[
        [
            "sample",
            "subject",
            "sample_type",
            "time_from_treatment_start",
        ]
    ].copy()

    samples.columns = [
        "sample_id",
        "subject_id",
        "sample_type",
        "time_from_treatment_start",
    ]

    samples.to_sql(
        "samples",
        connection,
        if_exists="append",
        index=False,
    )


def load_cell_counts(connection, dataframe):
    cell_counts = dataframe.melt(
        id_vars=["sample"],
        value_vars=CELL_POPULATIONS,
        var_name="population",
        value_name="count",
    )

    cell_counts = cell_counts.rename(
        columns={"sample": "sample_id"}
    )

    cell_counts.to_sql(
        "cell_counts",
        connection,
        if_exists="append",
        index=False,
    )


def main():
    if DATABASE_FILE.exists():
        DATABASE_FILE.unlink()

    dataframe = pd.read_csv(CSV_FILE)

    connection = create_database()

    try:
        load_subjects(connection, dataframe)
        load_samples(connection, dataframe)
        load_cell_counts(connection, dataframe)

        connection.commit()
    finally:
        connection.close()

    print(f"Database created: {DATABASE_FILE}")


if __name__ == "__main__":
    main()