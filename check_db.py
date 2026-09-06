import sqlite3


connection = sqlite3.connect("cell_counts.db")
cursor = connection.cursor()

tables = [
    "subjects",
    "samples",
    "cell_counts",
]

for table in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    print(f"{table}: {count}")

print("\nSample check:")

cursor.execute("""
    SELECT
        s.sample_id,
        s.subject_id,
        s.sample_type,
        s.time_from_treatment_start,
        c.population,
        c.count
    FROM samples s
    JOIN cell_counts c
        ON s.sample_id = c.sample_id
    WHERE s.sample_id = 'sample00000'
    ORDER BY c.population
""")

rows = cursor.fetchall()

for row in rows:
    print(row)

connection.close()