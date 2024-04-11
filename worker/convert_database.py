import argparse
import sqlite3


# Define the parser object
parser = argparse.ArgumentParser(
    description="Convert detections database to birds database"
)

# Add arguments for the old and new databases
parser.add_argument(
    "--old-db", required=True, help="Path to the old detections database"
)
parser.add_argument('--new-db', required=True, help='Path to the new birds database')

# Parse the arguments
args = parser.parse_args()

# Check if both the old and new databases are provided
if args.old_db and args.new_db:
    # Make the new database.
    new_conn = sqlite3.connect(args.new_db)
    new_cursor = new_conn.cursor()
    new_cursor.execute(
        "CREATE TABLE birds (id INTEGER PRIMARY KEY, recording_date DATETIME, filename TEXT, confidence REAL, common_name TEXT, scientific_name TEXT);"
    )
    # Connect to the old database
    conn = sqlite3.connect(args.old_db)
    cursor = conn.cursor()

    # SQL query to select all rows from the detections table
    query = "SELECT Date, Time, Sci_Name, Com_Name, Confidence, Lat, Lon, Cutoff, Week, Sens, Overlap, File_Name FROM detections"

    # Execute the query and retrieve the results
    cursor.execute(query)
    results = cursor.fetchall()

    # Loop through each row in the results
    for row in results:
        # Extract the desired fields from the current row
        date = row[0]
        time = row[1]
        datetime = f"{date} {time}"
        sci_name = row[2]
        com_name = row[3]
        confidence = row[4]
        file_name = row[11]

        # Insert the data into the new database
        new_cursor.execute(
            "INSERT INTO birds (recording_date, filename, confidence, common_name, scientific_name) VALUES (?, ?, ?, ?, ?)",
            (datetime, file_name, confidence, com_name, sci_name),
        )

    # Close the cursors and connections
    new_conn.commit()
    cursor.close()
    new_cursor.close()
    conn.close()
    new_conn.close()
else:
    print("Error: Both old and new databases must be provided")
