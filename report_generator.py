import os
import pandas as pd


def generate_reports(vehicle_records, csv_path="outputs/vehicle_report.csv", excel_path="outputs/vehicle_report.xlsx"):
	"""Generate CSV and Excel reports from vehicle_records.

	vehicle_records: dict keyed by id -> record dicts (as produced in main.py)
	Returns a dict with paths written.
	"""

	os.makedirs(os.path.dirname(csv_path), exist_ok=True)

	# Convert records to DataFrame
	records = list(vehicle_records.values())

	if not records:
		# create empty dataframe with expected columns
		df = pd.DataFrame(columns=[
			"id",
			"type",
			"color",
			"plate",
			"entry_time",
			"vehicle_image",
			"plate_image",
			"debug_plate_image",
		])
	else:
		df = pd.DataFrame.from_records(records)

	# Ensure consistent column order
	cols = [
		"id",
		"type",
		"color",
		"plate",
		"entry_time",
		"vehicle_image",
		"plate_image",
		"debug_plate_image",
	]

	for c in cols:
		if c not in df.columns:
			df[c] = None

	df = df[cols]

	# Write CSV
	df.to_csv(csv_path, index=False)

	# Write Excel
	try:
		df.to_excel(excel_path, index=False)
	except Exception:
		# If openpyxl not available or fails, skip Excel but still return CSV
		excel_path = None

	return {"csv": csv_path, "excel": excel_path}
