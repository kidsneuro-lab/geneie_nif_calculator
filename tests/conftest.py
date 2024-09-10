from collections import defaultdict
import pytest

from nif_calculator.db import load_config_data

@pytest.fixture(scope="session")
def donor_motif_stats():
    return load_config_data("donor")
                       
@pytest.fixture(scope="session")
def acceptor_motif_stats():
    return load_config_data("acceptor")