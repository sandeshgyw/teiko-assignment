import sqlite3

from pathlib import Path

import pandas as pd

import streamlit as st

from load_data import main as load_database

DATABASE_FILE = "cell_counts.db"

def ensure_database():

    needs_rebuild = not Path(DATABASE_FILE).exists()

    if not needs_rebuild:

        connection = sqlite3.connect(DATABASE_FILE)

        tables = connection.execute(

            """

            SELECT name

            FROM sqlite_master

            WHERE type='table'

            """

        ).fetchall()

        connection.close()

        table_names = {table[0] for table in tables}

        required_tables = {

            "subjects",

            "samples",

            "cell_counts",

        }

        needs_rebuild = not required_tables.issubset(table_names)

    if needs_rebuild:

        load_database()

ensure_database()

st.set_page_config(

    page_title="Teiko Immune Cell Analysis",

    layout="wide",

)

st.title("Immune Cell Analysis Dashboard")

st.write(
    "Interactive results from the immune cell frequency, "
    "statistical comparison, and subset analyses."
)


@st.cache_data
def load_frequency_data():
    return pd.read_csv("cell_frequencies.csv")


@st.cache_data
def load_statistical_results():
    return pd.read_csv("statistical_results.csv")


@st.cache_data
def load_part4_data():
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

    baseline_data = pd.read_sql_query(
        baseline_query,
        connection,
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

    average_b_cell = pd.read_sql_query(
        average_b_cell_query,
        connection,
    )

    connection.close()

    return baseline_data, average_b_cell


frequency_data = load_frequency_data()
statistical_results = load_statistical_results()
baseline_data, average_b_cell = load_part4_data()


st.header("Relative Cell Frequencies")

population_options = sorted(
    frequency_data["population"].unique()
)

selected_population = st.selectbox(
    "Select an immune cell population",
    population_options,
)

filtered_frequency_data = frequency_data[
    frequency_data["population"] == selected_population
]

st.dataframe(
    filtered_frequency_data,
    use_container_width=True,
)


st.header("Responder vs Nonresponder Analysis")

st.dataframe(
    statistical_results,
    use_container_width=True,
)

significant_results = statistical_results[
    statistical_results["significant"] == True
]

if significant_results.empty:
    st.info(
        "No immune cell population remained statistically "
        "significant after Benjamini-Hochberg correction "
        "at an FDR threshold of 0.05."
    )
else:
    st.success(
        "One or more immune cell populations were statistically significant."
    )

st.image(
    "response_boxplots.png",
    caption="Responder vs nonresponder relative-frequency distributions",
    use_container_width=True,
)


st.header("Baseline and Subset Analysis")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Samples per Project")

    project_counts = (
        baseline_data.groupby("project")["sample_id"]
        .nunique()
        .reset_index(name="samples")
    )

    st.dataframe(
        project_counts,
        use_container_width=True,
    )


with col2:
    st.subheader("Subjects by Response")

    response_counts = (
        baseline_data.groupby("response")["subject_id"]
        .nunique()
        .reset_index(name="subjects")
    )

    st.dataframe(
        response_counts,
        use_container_width=True,
    )


with col3:
    st.subheader("Subjects by Sex")

    sex_counts = (
        baseline_data.groupby("sex")["subject_id"]
        .nunique()
        .reset_index(name="subjects")
    )

    st.dataframe(
        sex_counts,
        use_container_width=True,
    )


st.subheader("Average B-cell Count")

average_value = average_b_cell.loc[
    0,
    "average_b_cell_count",
]

st.metric(
    "Melanoma male responders at time 0",
    f"{average_value:,.2f}",
)

st.caption(
    "Average includes all treatment types and sample types."
)