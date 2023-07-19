import csv
import sqlite3

# Open the CSV file
with open('baseball-data.csv', 'r') as csvfile:
    # Read the CSV file
    csvreader = csv.reader(csvfile)
    # Create a SQLite database connection
    conn = sqlite3.connect('database.db')

    # Create a cursor to execute SQL statements
    cursor = conn.cursor()

    # Create the table
    cursor.execute('''CREATE TABLE IF NOT EXISTS baseball_table (
                            YEAR INTEGER,
                            RD INTEGER,
                            PICK INTEGER,
                            TEAM TEXT,
                            PLAYER TEXT,
                            POS TEXT,
                            SCHOOL TEXT,
                            TYPE TEXT,
                            ST TEXT,
                            SIGNED TEXT,
                            BONUS REAL
                            )''')

    # Iterate over each row in the CSV file
    count = 0
    for row in csvreader:
        # Split each row into separate lines
        print(row)
        cursor.execute('INSERT INTO baseball_table VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) ', row)
        print()
        count = count+1
    conn.commit()
    conn.close()

