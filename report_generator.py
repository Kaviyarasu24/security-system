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


def append_daily_excel(vehicle_records, date_str=None, excel_dir="outputs"):
	"""Append vehicle_records to a daily Excel file named DD_MM_YYYY.xlsx.

	- If the file exists, read it and append new rows.
	- If not, create a new Excel file with the data.

	Returns the path to the Excel file written, or None on failure.
	"""

	from datetime import datetime

	if date_str is None:
		date_str = datetime.now().strftime("%d_%m_%Y")

	os.makedirs(excel_dir, exist_ok=True)

	excel_path = os.path.join(excel_dir, f"{date_str}.xlsx")

	# Prepare dataframe from records
	records = list(vehicle_records.values())

	if not records:
		df_new = pd.DataFrame(columns=[
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
		df_new = pd.DataFrame.from_records(records)

	# Ensure consistent columns
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
		if c not in df_new.columns:
			df_new[c] = None

	df_new = df_new[cols]

	try:
		if os.path.exists(excel_path):
			# Read existing and append
			try:
				df_existing = pd.read_excel(excel_path)
			except Exception:
				# If the existing file is corrupt or unreadable, overwrite
				df_existing = pd.DataFrame(columns=cols)

			# Concatenate
			df_concat = pd.concat([df_existing, df_new], ignore_index=True)

			# Write back (overwrite)
			df_concat.to_excel(excel_path, index=False)
		else:
			# New file
			df_new.to_excel(excel_path, index=False)

		return excel_path

	except PermissionError:
		# File may be open in Excel
		return None
	except Exception:
		return None
