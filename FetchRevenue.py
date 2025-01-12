import requests
import csv
import logging
import sys
import json
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# API URLs and headers
APIS = {
    "TPEX ESB": "https://www.tpex.org.tw/openapi/v1/t187ap05_R",
    "TPEX MB": "https://www.tpex.org.tw/openapi/v1/mopsfin_t187ap05_O",
    "TWSE": "https://openapi.twse.com.tw/v1/opendata/t187ap05_P"
}
HEADERS = {
    "accept": "application/json",
    "If-Modified-Since": "Mon, 26 Jul 1997 05:00:00 GMT",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache"
}

def fetch_api_data(api_url, headers):
    try:
        logging.info(f"Fetching data from API: {api_url}")
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()  # Check for HTTP errors
        data = response.json()  # Parse JSON response
        logging.info(f"Successfully fetched {len(data)} records from the API.")
        return data
    except requests.exceptions.RequestException as e:
        logging.error(f"HTTP error occurred: {e}")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    return []

def write_json_to_csv(json_data, csv_file, mode='w'):
    if not json_data:
        logging.error("No data available to write to CSV.")
        return

    # Extract headers dynamically from the JSON data
    headers = json_data[0].keys()

    try:
        with open(csv_file, mode=mode, encoding='utf-8-sig', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            if mode == 'w':
                writer.writeheader()  # Write header only once for 'write' mode
            writer.writerows(json_data)
        logging.info(f"Data successfully written to {csv_file}.")
    except Exception as e:
        logging.error(f"Failed to write data to CSV: {e}")

def write_summary_json(file_name, label, message):
    """Write a summary JSON file with the number of companies."""
    summary = {
        "schemaVersion": 1,
        "label": label,
        "message": str(message),
        "color": "blue"
    }
    try:
        with open(file_name, 'w', encoding='utf-8') as file:
            json.dump(summary, file, ensure_ascii=False, indent=4)
        logging.info(f"Summary JSON written to {file_name}.")
    except Exception as e:
        logging.error(f"Failed to write summary JSON: {e}")

def main():
    # Determine the output CSV file name
    if len(sys.argv) == 2:
        output_csv = sys.argv[1]
    elif len(sys.argv) == 1:
        # Use today's date as the default file name
        today = datetime.now().strftime("%Y%m%d")
        output_csv = f"{today}.csv"
        logging.info(f"No file name provided. Using default: {output_csv}")
    else:
        logging.error("Usage: python FetchRevenue.py [<output_csv_file>]")
        sys.exit(1)

    # Iterate over the APIs to fetch data and append it to the CSV
    for api_name, api_url in APIS.items():
        logging.info(f"Processing API: {api_name}")
        data = fetch_api_data(api_url, HEADERS)
        write_mode = 'w' if api_name == "TPEX ESB" else 'a'  # Write header for the first API, append for subsequent
        write_json_to_csv(data, output_csv, mode=write_mode)

        # Write the summary JSON for the number of records
        if api_name == "TPEX ESB":
            write_summary_json("TPEX_ESB.json", "TPEX ESB Monthly Revenue Company", len(data))
        elif api_name == "TPEX MB":
            write_summary_json("TPEX_MB.json", "TPEX MB Monthly Revenue Company", len(data))
        elif api_name == "TWSE":
            write_summary_json("TWSE.json", "TWSE Monthly Revenue Company", len(data))

if __name__ == "__main__":
    main()
