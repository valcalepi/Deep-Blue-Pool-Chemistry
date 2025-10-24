import csv
import pandas as pd
from datetime import datetime

def log_chemistry_data(data, csv_file='pool_log.csv', excel_file='pool_log.xlsx'):
    timestamp = datetime.now().isoformat()
    row = {'Timestamp': timestamp, **data}

    # Append to CSV
    with open(csv_file, mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=row.keys())
        if file.tell() == 0:
            writer.writeheader()
        writer.writerow(row)

    # Append to Excel
    try:
        df = pd.read_excel(excel_file)
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    except FileNotFoundError:
        df = pd.DataFrame([row])
    df.to_excel(excel_file, index=False)

