import influxdb_client
import os
import argparse
import pandas as pd
from influxdb_client import InfluxDBClient
from datetime import datetime

def main():
    # Setup argparse
    parser = argparse.ArgumentParser(description="Fetch health data from InfluxDB and store into CSV.")
    parser.add_argument("--days", type=int, default=1, help="How many days in the past to fetch the data")
    parser.add_argument("--aggregate", type=str, choices=["1m", "5m", "10m", "30m", "1h", None], default=None,
                        help="Optional mean aggregate for 1 min, 5 min, 10 min, 30 min, 1 hour. Default is no aggregation")
    parser.add_argument("--output", type=str, default="health_data.csv", help="Output CSV file name")
    args = parser.parse_args()

    # InfluxDB connection
    token = os.environ.get("INFLUXDB_TOKEN")
    org = "chromebook"
    url = "http://localhost:8086"
    client = InfluxDBClient(url=url, token=token, org=org)
    query_api = client.query_api()

    # Construct the time range for the query
    time_range = f"-{args.days}d"

    # Measurement and fields
    measurement = "Health"
    fields = ["bpm", "movement", "pi", "spo2"]
    aggregation = f"|> aggregateWindow(every: {args.aggregate}, fn: mean)" if args.aggregate else ""

    query = f"""
    from(bucket: "health_data")
      |> range(start: {time_range})
      |> filter(fn: (r) => r._measurement == "{measurement}")
      |> filter(fn: (r) => r._field == "bpm" or r._field == "movement" or r._field == "pi" or r._field == "spo2")
      {aggregation}
      |> filter(fn: (r) => (r._field != "bpm" or r._value > 0) and (r._field != "spo2" or r._value > 0))
    """

    # Fetch data
    tables = query_api.query(query, org=org)

    # Parse data into a dictionary based on timestamp
    data = {}
    for table in tables:
        for record in table.records:
            timestamp = record.get_time()  # Already a datetime object
            key = (timestamp.hour, timestamp.minute, timestamp.second)

            # Create an entry for each timestamp if it doesn't exist
            if key not in data:
                data[key] = {"hour": timestamp.hour, "minute": timestamp.minute, "second": timestamp.second}

            # Add the field's value to the appropriate column
            data[key][record.get_field()] = record.get_value()

    # Convert records to DataFrame
    df = pd.DataFrame(data.values())

    # Ensure all required columns exist and fill missing values with NaN
    df = df.reindex(columns=["hour", "minute", "second", "bpm", "movement", "pi", "spo2"], fill_value=float('nan'))

    # Save DataFrame to CSV
    if not df.empty:
        df.to_csv(args.output, index=False)
        print(f"Data successfully saved to {args.output}")
    else:
        print("No valid data found for the specified range.")

if __name__ == "__main__":
    main()

