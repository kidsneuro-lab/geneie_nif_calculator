#!/bin/bash

# Assign arguments to variables
DATABASE_FILE="nif_calculator/resources/sj_stats.sqlite"

# Error handling function
handle_error() {
    echo "ERROR: $1"
    exit 1
}

# Remove the database file if it exists
if [ -f "$DATABASE_FILE" ]; then
    echo "Removing existing database file: $DATABASE_FILE"
    rm -f "$DATABASE_FILE" || handle_error "Failed to remove $DATABASE_FILE"
fi

# Generate the SQL commands to create donor_stats and acceptor_stats tables
CREATE_DONOR_STATS_SQL="CREATE TABLE IF NOT EXISTS donor_stats (seq TEXT, freq INTEGER, pctl REAL, window TEXT, window_length INTEGER);"
CREATE_ACCEPTOR_STATS_SQL="CREATE TABLE IF NOT EXISTS acceptor_stats (seq TEXT, freq INTEGER, pctl REAL, window TEXT, window_length INTEGER);"

# Create the tables in the SQLite database
sqlite3 "$DATABASE_FILE" <<EOF
$CREATE_DONOR_STATS_SQL;
$CREATE_ACCEPTOR_STATS_SQL;
EOF

# Check if the table creation was successful
if [ $? -ne 0 ]; then
    handle_error "Failed to create tables in the database $DATABASE_FILE"
fi

echo "Tables 'donor_stats' and 'acceptor_stats' created successfully in $DATABASE_FILE."

# Import the donor_stats TSV file into the SQLite database
sqlite3 "$DATABASE_FILE" <<EOF
.separator "\t"
.import --skip 1 "nif_calculator/resources/ensembl_donor_sj_stats.tsv" "donor_stats"
EOF

# Check if the import was successful
if [ $? -ne 0 ]; then
    handle_error "Failed to import donor_stats TSV file into the database $DATABASE_FILE"
fi

echo "donor_stats TSV file imported successfully into the database $DATABASE_FILE."

# Import the acceptor_stats TSV file into the SQLite database
sqlite3 "$DATABASE_FILE" <<EOF
.separator "\t"
.import --skip 1 "nif_calculator/resources/ensembl_acceptor_sj_stats.tsv" "acceptor_stats"
EOF

# Check if the import was successful
if [ $? -ne 0 ]; then
    handle_error "Failed to import acceptor_stats TSV file into the database $DATABASE_FILE"
fi

echo "acceptor_stats TSV file imported successfully into the database $DATABASE_FILE."

echo "Tables 'donor_stats' and 'acceptor_stats' have been created and populated in the database '$DATABASE_FILE'."
echo "Script completed successfully."
