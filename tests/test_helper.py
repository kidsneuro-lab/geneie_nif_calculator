import sys
import pytest
from typing import Literal
import re
import logging

# Assuming the function you provided is inside a module called motif_module

sys.path.append('nif_calculator')
from nif_calculator.helper import NIFAnnotator

# Set up logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

class TestNIFCalculation:
    def test_calc_nif_known_donor_seq(self, donor_motif_stats):
        sequence = 'ATCGGTGCAAGT'
        expected_result = {'U5': {
                                'E4_D5': {
                                    'seq': 'ATCGGTGCA',
                                    'pctl': 0.0,
                                    'freq': 0
                                }
                            },
                            'U1': {
                                'E3_D6': {
                                    'seq': 'TCGGTGCAA',
                                    'pctl': 0.0,
                                    'freq': 0
                                },
                                'E2_D7': {
                                    'seq': 'CGGTGCAAG',
                                    'pctl': 0.0,
                                    'freq': 0
                                }
                            },
                            'U6': {
                                'E1_D8': {
                                    'seq': 'GGTGCAAGT',
                                    'pctl': 0.0193762132371837,
                                    'freq': 2
                                }
                            }}
        result = NIFAnnotator.calc_nif(sequence, 'donor', donor_motif_stats)
        assert result == expected_result
        
    def test_calc_nif_known_acceptor_seq(self, acceptor_motif_stats):
        sequence = 'AATTGTAAGAA'
        expected_result = {'ACC': {
                                'A9_A1': {
                                    'seq': 'AATTGTAAG',
                                    'pctl': 0.0437847502076319,
                                    'freq': 4
                                },
                                'A8_E1': {
                                    'seq': 'ATTGTAAGA',
                                    'pctl': 0.0125765578525753,
                                    'freq': 1
                                },
                                'A7_E2': {
                                    'seq': 'TTGTAAGAA',
                                    'pctl': 0.0459776698592195,
                                    'freq': 4
                                }
                            }}
        result = NIFAnnotator.calc_nif(sequence, 'acceptor', acceptor_motif_stats)
        assert result == expected_result

class TestSequenceExtraction:
    def test_get_sequence_zones_one_zone(self):
        sequence = "ATCGGTGCAAGT"
        zones = {'U5': {
                    'E4_D5': {
                        'offset': (-4, 5),
                        'disp_offset_start': 1,
                        'disp_offset_len': 9
                    }
                }}
        expected_result = {'U5': {
                                'E4_D5': {
                                    'seq': 'ATCGGTGCA'
                                }
                            }}
        result = NIFAnnotator.get_sequence_zones(zones, sequence)
        assert result == expected_result

    def test_get_sequence_zones_two_zones(self):
        sequence = "ATCGGTGCAAGT"
        zones = {'U5': {
                'E4_D5': {
                    'offset': (-4, 5),
                    'disp_offset_start': 1,
                    'disp_offset_len': 9
                    }
                },
                'U1': {
                    'E3_D6': {
                        'offset': (-3, 6),
                        'disp_offset_start': 2,
                        'disp_offset_len': 9
                    }
                }}
        expected_result = {'U5': {
                                'E4_D5': {
                                    'seq': 'ATCGGTGCA'
                                }
                            },
                            'U1': {
                                'E3_D6': {
                                    'seq': 'TCGGTGCAA'
                                }
                            }}
                            
        result = NIFAnnotator.get_sequence_zones(zones, sequence)
        assert result == expected_result

class TestMotifExtraction:
    def test_donor_motif_extraction_multiple(self):
        sequence = "ATCGGTGCAAGTCGACCT"
        expected_result = [{'motif_type': 'donor', 'start': 0, 'seq': 'ATCGGTGCAAGT'},
                            {'motif_type': 'donor', 'start': 2, 'seq': 'CGGTGCAAGTCG'},
                            {'motif_type': 'donor', 'start': 6, 'seq': 'GCAAGTCGACCT'}]
        result = NIFAnnotator.extract_motifs(sequence, 'donor')
        assert result == expected_result

    def test_donor_motif_extraction_single(self):
        sequence = "ATCGGTGAAAGTAT"
        expected_result = [{'motif_type': 'donor', 'start': 0, 'seq': 'ATCGGTGAAAGT'}]
        result = NIFAnnotator.extract_motifs(sequence, 'donor')
        assert result == expected_result

    def test_donor_motif_extraction_none(self):
        sequence = "ATCGATGAAAGTAT"
        expected_result = []
        result = NIFAnnotator.extract_motifs(sequence, 'donor')
        assert result == expected_result

    def test_acceptor_motif_extraction_multiple(self):
        sequence = "TGCTCCCCTCTTTTGCCTCAGGGAACGCCCCATGTACAGCCGGGA"
        expected_result = [{'motif_type': 'acceptor', 'start': 12, 'seq': 'TTGCCTCAGGG'},
                            {'motif_type': 'acceptor', 'start': 30, 'seq': 'CATGTACAGCC'}]
        result = NIFAnnotator.extract_motifs(sequence, 'acceptor')
        assert result == expected_result

    def test_acceptor_motif_extraction_single(self):
        sequence = "TGCTCCCCTCTTTTGCCTCAGGGAACGCCCCATGTACAACCGGGA"
        expected_result = [{'motif_type': 'acceptor', 'start': 12, 'seq': 'TTGCCTCAGGG'}]
        result = NIFAnnotator.extract_motifs(sequence, 'acceptor')
        assert result == expected_result

    def test_acceptor_motif_extraction_none(self):
        sequence = "TGCTCCCCTCTTTTGCCTCATGGAACGCCCCATGTACAACCGGGA"
        expected_result = []
        result = NIFAnnotator.extract_motifs(sequence, 'acceptor')
        assert result == expected_result