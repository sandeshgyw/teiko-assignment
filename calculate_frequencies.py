import sqlite3

import pandas as pd


DATABASE_FILE = "cell_counts.db"
OUTPUT_FILE = "cell_frequencies.csv"


def calculate_frequencies():
    connection = sqlite3.connect(DATABASE_FILE)

    query = """
        SELECT
            sample_id AS sample,
            SUM(count) OVER (PARTITION BY sample_id) AS total_count,
            population,
            count,
            count * 100.0 /
                SUM(count) OVER (PARTITION BY sample_id) AS percentage
        FROM cell_counts
        ORDER BY sample_id, population
    """

    dataframe = pd.read_sql_query(query, connection)

    connection.close()

    dataframe.to_csv(OUTPUT_FILE, index=False)

    print(f"Frequency table created: {OUTPUT_FILE}")
    print(f"Rows: {len(dataframe)}")
    print(dataframe.head())

    percentage_totals = dataframe.groupby("sample")["percentage"].sum()

    print(
        "Percentage sum range:",
        percentage_totals.min(),
        percentage_totals.max(),
    )


if __name__ == "__main__":
    calculate_frequencies()