import sqlite3

import pandas as pd


DATABASE_FILE = "cell_counts.db"


def run_query(connection, query):
    return pd.read_sql_query(query, connection)


def main():
    connection = sqlite3.connect(DATABASE_FILE)

    baseline_query = """
        SELECT
            s.sample_id,
            s.subject_id,
            sub.project,
            sub.sex,
            sub.response
        FROM samples s
        JOIN subjects sub
            ON s.subject_id = sub.subject_id
        WHERE sub.condition = 'melanoma'
            AND sub.treatment = 'miraclib'
            AND s.sample_type = 'PBMC'
            AND s.time_from_treatment_start = 0
    """

    baseline_data = run_query(
        connection,
        baseline_query,
    )

    print("Samples per project:")
    print(
        baseline_data.groupby("project")["sample_id"]
        .nunique()
    )

    print("\nDistinct subjects by response:")
    print(
        baseline_data.groupby("response")["subject_id"]
        .nunique()
    )

    print("\nDistinct subjects by sex:")
    print(
        baseline_data.groupby("sex")["subject_id"]
        .nunique()
    )

    average_b_cell_query = """
        SELECT
            AVG(c.count) AS average_b_cell_count
        FROM samples s
        JOIN subjects sub
            ON s.subject_id = sub.subject_id
        JOIN cell_counts c
            ON s.sample_id = c.sample_id
        WHERE sub.condition = 'melanoma'
            AND sub.sex = 'M'
            AND sub.response = 'yes'
            AND s.time_from_treatment_start = 0
            AND c.population = 'b_cell'
    """

    average_b_cell = run_query(
        connection,
        average_b_cell_query,
    )

    print("\nAverage B-cell count:")
    print(
        round(
            average_b_cell.loc[
                0,
                "average_b_cell_count",
            ],
            2,
        )
    )

    connection.close()


if __name__ == "__main__":
    main()