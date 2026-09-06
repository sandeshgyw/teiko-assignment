.PHONY: setup pipeline dashboard

setup:
	python3 -m pip install -r requirements.txt

pipeline:
	python3 load_data.py
	python3 calculate_frequencies.py
	python3 run_statistics.py
	python3 query_subsets.py

dashboard:
	python3 -m streamlit run dashboard_app.py