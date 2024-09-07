# README: Health Data from Influx Scripts

## Overview

This Python script fetches health data (e.g., heart rate, movement, perfusion index, oxygen saturation) from an InfluxDB instance, aggregates it based on the given time interval, and appends it to a CSV file. The script allows for customization of the time range, aggregation window, and output file.

## Features
- **Fetch data from InfluxDB**: Connects to an InfluxDB instance to query and retrieve health data from the specified measurement.
- **Aggregation support**: You can specify a time-based aggregation for averages (e.g., 1 minute, 5 minutes, 1 hour).
- **Flexible date ranges**: Retrieve data from a specified number of days in the past, broken down into chunks.
- **CSV output**: Appends the fetched and filtered data to a CSV file for easy analysis and storage.

## Prerequisites

- Python 3.x
- Required Python libraries: `influxdb-client`, `pandas`, `argparse`
- An InfluxDB instance running locally or remotely
- InfluxDB token, bucket, and organization details configured via environment variables

## Installation

1. Install required Python packages:

   ```bash
   pip install influxdb-client pandas argparse
   ```

2. Set the `INFLUXDB_TOKEN` environment variable with your InfluxDB authentication token:

   ```bash
   export INFLUXDB_TOKEN="your_influxdb_token"
   ```

## Usage

Run the script from the command line:

```bash
python3 fetch_health_data.py [OPTIONS]
```

### Available Options

- `--days`: Number of days in the past to fetch data (default: 1).
- `--day_interval`: Interval in days for fetching data chunks (default: 1). This allows fetching data in chunks, e.g., day-by-day.
- `--aggregate`: Optional aggregation window. You can specify time intervals for aggregating mean values. Supported values: `1m`, `5m`, `10m`, `30m`, `1h`. If not provided, no aggregation is performed.
- `--output`: Output CSV file name (default: `health_data.csv`).

### Example Commands

1. **Fetch 7 days of data, without aggregation, and output to `health_data.csv`:**

   ```bash
   python fetch_health_data.py --days 7 --output health_data.csv
   ```

2. **Fetch 3 days of data, with 5-minute aggregation, and save to `aggregated_data.csv`:**

   ```bash
   python fetch_health_data.py --days 3 --aggregate 5m --output aggregated_data.csv
   ```

3. **Fetch 1 day of data, with 1-hour aggregation, and append to an existing file `output.csv`:**

   ```bash
   python fetch_health_data.py --days 1 --aggregate 1h --output output.csv
   ```

## Output Structure

The output CSV contains the following columns:

- `year`: Last two digits of the year when the data was recorded.
- `day_of_year`: The day of the year (1-365/366).
- `day_of_week`: The day of the week (0 = Monday, 6 = Sunday).
- `hour`, `minute`, `second`: Timestamp components of the data.
- `bpm`: Heart rate in beats per minute.
- `movement`: Movement data.
- `pi`: Perfusion index.
- `spo2`: Blood oxygen saturation.

Each row represents data recorded at a specific timestamp.

## Data Filtering

Rows are filtered to ensure the following conditions:

- `bpm` and `spo2` values must be greater than 0.
- Any rows with missing `bpm`, `movement`, `pi`, or `spo2` are dropped from the final CSV.

## Notes

- Ensure your InfluxDB instance is up and running.
- The `token`, `org`, and `url` for the InfluxDB connection are set within the script or via environment variables.

## Troubleshooting

- **No valid data found for range**: This message is displayed when no matching data is retrieved from the InfluxDB for a given time range.
- **Missing data columns**: Ensure your InfluxDB contains the specified measurement and fields (`bpm`, `movement`, `pi`, `spo2`).

## License

This project is licensed under the Apache-2.0 License.
