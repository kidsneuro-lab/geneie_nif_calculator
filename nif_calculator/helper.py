from collections import defaultdict
import os
import logging
import re
from typing import Literal
import sqlite3
import statistics

import requests

from nif_calculator.config import window_zone_offsets
from nif_calculator.db import load_config_data

DONOR_STATS = load_config_data('donor')
ACCEPTOR_STATS = load_config_data('acceptor')

logger = logging.getLogger(__name__)

class NIFAnnotator:
    def __init__(self, sequence: str) -> None:
        self.sequence = sequence

    def get_nif_table(self):
        formatted_motif_nifs = []

        motif_nifs = NIFAnnotator.calc_motif_nifs(self.sequence)
        motif_nifs = sorted(motif_nifs,key=lambda x: x['start'])

        for entry in motif_nifs:
            if entry['motif_type'] == 'donor':
                formatted_motif_nif_entry = {
                    'offset': entry['start'],
                    'motif_type': 'Donor',
                    'seq': entry['seq'],
                    'U5': round(entry['nif']['U5']['E4_D5']['pctl'], 2),
                    'U1': round(statistics.mean([entry['nif']['U1']['E3_D6']['pctl'], entry['nif']['U1']['E2_D7']['pctl']]), 2),
                    'U6': round(entry['nif']['U6']['E1_D8']['pctl'], 2),
                    'A9_A1': None,
                    'A8_E1': None,
                    'A7_E2': None
                }
                
                formatted_motif_nifs.append(formatted_motif_nif_entry)

            if entry['motif_type'] == 'acceptor':
                formatted_motif_nif_entry = {
                    'offset': entry['start'],
                    'motif_type': 'Acceptor',
                    'seq': entry['seq'],
                    'U5': None,
                    'U1': None,
                    'U6': None,
                    'A9_A1': round(entry['nif']['ACC']['A9_A1']['pctl'], 2),
                    'A8_E1': round(entry['nif']['ACC']['A9_A1']['pctl'], 2),
                    'A7_E2': round(entry['nif']['ACC']['A9_A1']['pctl'], 2),
                }
                
                formatted_motif_nifs.append(formatted_motif_nif_entry)

        return formatted_motif_nifs

    @staticmethod
    def calc_motif_nifs(sequence: str):
        donor_motifs = NIFAnnotator.extract_motifs(sequence=sequence, motif_type='donor')
        acceptor_motifs = NIFAnnotator.extract_motifs(sequence=sequence, motif_type='acceptor')
        
        for motif in donor_motifs:
            motif['nif'] = NIFAnnotator.calc_nif(motif['seq'], 'donor', DONOR_STATS)

        for motif in acceptor_motifs:
            motif['nif'] = NIFAnnotator.calc_nif(motif['seq'], 'acceptor', ACCEPTOR_STATS)

        donor_motifs.extend(acceptor_motifs)
        return donor_motifs

    @staticmethod
    def calc_nif(seq: str, motif_type: Literal['donor','acceptor'], motif_stats: dict):
        _zones =  NIFAnnotator.get_sequence_zones(zones=window_zone_offsets[motif_type]['zones'], seq=seq)
        zones =  NIFAnnotator.calculate_zone_nifs(zones=_zones, motif_stats=motif_stats)

        return zones

    @staticmethod
    def get_sequence_zones(zones: dict, seq: str) -> dict:    
        seq_zones = {}
        
        for zone in zones.keys():
            logger.debug(f"Getting sequences for Zone: {zone}")
            seq_zones[zone] = {}
            
            for window in zones[zone].keys():
                logger.debug(f"\tGetting sequences for Widnow: {window}")
                
                start = zones[zone][window]['disp_offset_start'] - 1
                end = start + zones[zone][window]['disp_offset_len']
                
                seq_zones[zone][window] = {'seq': seq[start:end]}
                
        return seq_zones

    @staticmethod
    def calculate_zone_nifs(zones: dict, motif_stats: dict) -> dict:
        """
        Calculates NIFs for given zones and motif statistics.

        Parameters:
            zones (dict): The zones with motif sequence information.
            motif_stats (dict): Statistics related to motifs.

        Returns:
            dict: A dictionary with calculated NIFs for the given zones.
        """
        _zones = zones
        
        for zone in _zones.keys():
            logger.debug(f"Zone: {zone}")
            for window in _zones[zone].keys():
                logger.debug(f"  Window: {window}")
                motif = _zones[zone][window]['seq'].upper()
                _zones[zone][window]['freq'] = motif_stats[window][motif]['freq']
                _zones[zone][window]['pctl'] = motif_stats[window][motif]['pctl']
                
                logger.debug(f"    Motif: {motif} - Freq: {_zones[zone][window]['freq']}, Pctl: {_zones[zone][window]['pctl']}")
        
        return _zones

    @staticmethod
    def extract_motifs(sequence: str, motif_type: Literal['donor','acceptor']) -> list[dict[str,int,str]]:
        """
        Extract motifs from the given sequence based on motif_type.
        
        Parameters:
        - sequence: str, the sequence from which to extract motifs
        - motif_type: str, can be 'donor' or 'acceptor' to specify the motif type
        
        Returns:
        - List of dictionaries with motif details (motif_type, start, seq)
        """
        logger.debug(f"sequence={sequence[:50]}...")

        # Ensure the sequence is uppercase for consistent pattern matching
        sequence = sequence.upper()

        # Choose the regex pattern based on the motif_type
        if motif_type == 'donor':
            pattern = re.compile(r"(?i)(?=(\w{4}GT\w{6}|\w{4}GC\w{6}))")
        elif motif_type == 'acceptor':
            pattern = re.compile(r"(?i)(?=(\w{7}AG\w{2}))")
        else:
            raise ValueError("motif_type must be either 'donor' or 'acceptor'")

        # Find all matches
        matches = []
        for match in pattern.finditer(sequence):
            matched_seq = match.group(1)
            
            matches.append({
                'motif_type': motif_type,
                'start': match.start(),
                'seq': matched_seq
            })

        return matches

    @staticmethod
    def split_genomic_location(location: str) -> tuple[str, int, int]:
        # Split the location string into chromosome part and range part
        chrom, range_part = location.split(':')

        # Split the range part into start and end positions
        start, end = range_part.split('-')

        return chrom, int(start), int(end)

    @staticmethod
    def get_nif_list(region: str, strand: Literal['positive','negative']) -> list:
        logger.debug(f"region={region}, strand={strand}")
        strand = 1 if strand == 'positive' else -1

        # Split region into constituents
        chrom, start, end = NIFAnnotator.split_genomic_location(region)

        # Increment start by 1 as it is 0 based
        start += 1

        seq = NIFAnnotator.fetch_sequence(chrom, start, end, strand)
        
        matches = NIFAnnotator.extract_genomic_sequences(start, end, strand, seq)

        return matches

    @staticmethod
    def extract_genomic_sequences(genomic_start: int, genomic_end: int, strand: Literal[1,-1], sequence: str):
        logger.debug(f"genomic_start={genomic_start}, genomic_end={genomic_end}, strand={strand}, sequence={sequence[:50]}...")

        # Ensure the sequence is uppercase for consistent pattern matching
        sequence = sequence.upper()

        # Compile the regex pattern
        pattern = re.compile(r"(?i)(?=(\w{4}GT\w{6}|\w{4}GC\w{6}))")

        matches = []
        for match in pattern.finditer(sequence):
            matched_seq = match.group(1)
            # Calculate the start and end positions on the genome
            seq_start = genomic_start + match.start()
            seq_end = seq_start + len(matched_seq) - 1
            
            matches.append({
                'motif_type': 'donor',
                'start': seq_start,
                'end': seq_end,
                'seq': matched_seq
            })

        return matches
    
    @staticmethod
    def fetch_sequence(chrom: str, genomic_start: int, genomic_end: int, strand: Literal[1,-1]):
        logger.debug(f"chrom={chrom}, genomic_start={genomic_start}, genomic_end={genomic_end}, strand={strand}")
        
        server = "https://rest.ensembl.org"
        ext = f"/sequence/region/human/{chrom}:{genomic_start}..{genomic_end}:{strand}?"
        
        r = requests.get(server + ext, headers={"Content-Type": "text/plain"})
        
        if not r.ok:
            r.raise_for_status()
        
        return r.text