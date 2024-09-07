from collections import defaultdict
import os
import sqlite3
from typing import Literal

def load_config_data(motif_type: Literal['donor','acceptor']):
    # Connect to the SQLite database
    motif_stats = defaultdict(lambda: defaultdict(lambda: {'freq': 0, 'pctl': 0.00}))

    conn = sqlite3.connect(os.path.join('nif_calculator', 'resources', 'sj_stats.sqlite'))
    cursor = conn.cursor()

    # Define the query to select rows where window_length is 9
    windows = "'E4_D5','E3_D6','E2_D7','E1_D8'" if motif_type == 'donor' else "'A9_A1','A8_E1','A7_E2'"

    query = f"SELECT window, seq, freq, pctl FROM {motif_type}_stats WHERE window_length = 9 and window IN ({windows})"

    # Execute the query
    cursor.execute(query)

    # Fetch all the rows
    rows = cursor.fetchall()

    conn.close()
    
    # Convert the rows into a list of dictionaries
    for row in rows:
        motif_stats[row[0]][row[1]]['freq'] = row[2]
        motif_stats[row[0]][row[1]]['pctl'] = row[3]

    return motif_stats