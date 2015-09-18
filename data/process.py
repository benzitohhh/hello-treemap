#!/usr/bin/env python
"""
Description:
  This script takes in a CSV file (with a header row).
  For each row... it does stuff, and outputs row.

Usage:
  process --file=<FILE> --colnum=<col> [-d <delimiter>]

Options:
  -h --help                         Show this screen
  -f --file=<FILE>                  The input csv file
  -c --colnum=<colnum>              The csv column number of interest (i.e. 0-indexed, so 0, 1, 2 etc..)
  -d --inputdelimiter=<delimiter>   The input delimiter (i.e. "," or "t" for tab) [default: ,]

Examples:
  ./process.py -c input/example.csv -s 2
  ./process.py -c input/example.tsv -s 2 -d t
"""

from docopt import docopt
import csv
import sys
import MySQLdb
import MySQLdb.cursors

import dbconfig # file that contains db config (or add it explicitly below)
DB_CONFIG = dbconfig.LOCAL_CONFIG

# DB_CONFIG = {
#     'host'        : 'localhost',
#     'user'        : 'root',
#     'passwd'      : 'root',
#     'db'          : 'yourdb',
#     'port'        : 3306,
#     'charset'     : 'utf8',
#     'cursorclass' : MySQLdb.cursors.SSCursor
# }

DB_FIELDNAMES = ['priority_date', 'granted_date', 'expiry_date', 'inactive_date']

QUERY = 'SELECT ' + (', ').join(DB_FIELDNAMES) + ' FROM PatentFamily WHERE accession = %s'

def get_db_row(conn, query, params=[]):
    cur = get_cursor(conn)
    cur.execute(query, params)
    row = cur.fetchone()
    cur.close()
    return row

def get_connection():
    return MySQLdb.connect(**DB_CONFIG)

def get_cursor(conn):
    return conn.cursor(MySQLdb.cursors.SSDictCursor)

def main():
    params = docopt(__doc__)
    colnum = int(params['--colnum'])
    inputdelimiter = params['--inputdelimiter']
    if inputdelimiter == "t":
        inputdelimiter = '\t'

    # init db
    conn = get_connection()
        
    # read in csv
    with open(params['--file'], 'rU') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=inputdelimiter) # gets field_names from first line of CSV
        input_fieldnames = reader.fieldnames
        column_of_interest = input_fieldnames[colnum]
        output_fieldnames = input_fieldnames + DB_FIELDNAMES
        writer = csv.DictWriter(sys.stdout, output_fieldnames, dialect='excel')

        # output csv header
        writer.writeheader()

        for csv_row in reader:
            accession = csv_row[column_of_interest]
            accession = accession.split()[0]

            # get extra fields from db (as a dictionary)
            db_row = get_db_row(conn, QUERY, [accession])

            # Add db fields into the csv row
            csv_row.update(db_row)

            # Output csv row
            writer.writerow(csv_row)

    # Close db
    conn.close()
    
if __name__ == '__main__':
    main()
