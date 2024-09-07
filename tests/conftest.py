from collections import defaultdict
import pytest

@pytest.fixture(scope="session")
def motif_stats():
    motif_stats = defaultdict(lambda: defaultdict(lambda: {'freq': 0, 'pctl': 0.00}))
    
    
    motif_stats['E4_D5'] = {'ATCGGTGCA':{'pctl':0.01, 'freq':10}}
    motif_stats['E3_D6'] = {'TCGGTGCAA':{'pctl':0.33, 'freq':20}}
    
    return motif_stats
                       