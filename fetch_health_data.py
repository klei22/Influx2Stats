import influxdb_client
import os
import argparse
import pandas as pd
from influxdb_client import InfluxDBClient
from datetime import datetime

def main():
    # Setup argparse
    parser = argparse.ArgumentParser(description="Fetch health data from InfluxDB and append to CSV.")
    parser.add_argument("--days", type=int, default=1, help="How many days in the past to fetch the data")
    parser.add_argument("--day_interval", type=int, default=1, help="Interval in days for fetching data chunks")
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

    # Measurement and fields
    measurement = "Health"
    fields = ["bpm", "movement", "pi", "spo2"]
    aggregation = f"|> aggregateWindow(every: {args.aggregate}, fn: mean)" if args.aggregate else ""

    # Loop through the time range in chunks based on day_interval, but in chronological order
    for start_offset in range(args.days, 0, -args.day_interval):
        # Calculate the start and stop time for this chunk
        start_time = f"-{start_offset}d"
        stop_time = f"-{max(0, start_offset - args.day_interval)}d"
        
        query = f"""
        from(bucket: "health_data")
          |> range(start: {start_time}, stop: {stop_time})
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
                    # Get last two digits of the year, the day of the year, and the day of the week as a number (0-6)
                    year = timestamp.year % 100
                    day_of_year = timestamp.timetuple().tm_yday
                    day_of_week = timestamp.weekday()  # Monday is 0, Sunday is 6
                    data[key] = {
                        "year": year,
                        "day_of_year": day_of_year,
                        "day_of_week": day_of_week,
                        "hour": timestamp.hour,
                        "minute": timestamp.minute,
                        "second": timestamp.second
                    }

                # Add the field's value to the appropriate column
                data[key][record.get_field()] = record.get_value()

        # Convert records to DataFrame
        df = pd.DataFrame(data.values())

        # Ensure all required columns exist and fill missing values with NaN
        df = df.reindex(columns=["year", "day_of_year", "day_of_week", "hour", "minute", "second", "bpm", "movement", "pi", "spo2"], fill_value=float('nan'))

        # Drop rows where any of bpm, movement, pi, or spo2 is NaN
        df = df.dropna(subset=["bpm", "movement", "pi", "spo2"])

        # Append DataFrame to CSV
        if not df.empty:
            # Append to the file if it exists, otherwise create it
            df.to_csv(args.output, mode='a', header=not os.path.exists(args.output), index=False)
            print(f"Data from {start_time} to {stop_time} successfully appended to {args.output}")
        else:
            print(f"No valid data found for range {start_time} to {stop_time}.")

if __name__ == "__main__":
    main()

