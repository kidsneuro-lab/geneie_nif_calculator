window_zone_offsets = {
    'donor': {
        # NOTE: Enabling GC decoy donor search for the moment.
        #       This does incur a performance penalty particularly for large introns
        'pattern': r"(?i)(?=(\w{4}GT\w{6}|\w{4}GC\w{6}))",
        # 'pattern': r"(?i)(?=(\w{4}GT\w{6}))",
        'window_length': 9,
        'motif_window': {
            'offset': (-4, 8),
            'annot_site_offset_start': 5,
            'annot_site_offset_len': 2
        },
        'zones': {
            'U5': {
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
                },
                'E2_D7': {
                    'offset': (-2, 7),
                    'disp_offset_start': 3,
                    'disp_offset_len': 9
                }
            },
            'U6': {
                'E1_D8': {
                    'offset': (-1, 8),
                    'disp_offset_start': 4,
                    'disp_offset_len': 9
                }
            }
        }
    },
    'acceptor': {
        'pattern': r"(?i)(?=(\w{7}AG\w{2}))",
        'window_length': 9,
        'motif_window': {
            'offset': (-9, 2),
            'annot_site_offset_start': 8,
            'annot_site_offset_len': 2
        },
        'zones': {
            'ACC': {
                'A9_A1': {
                    'offset': (-9, -1),
                    'disp_offset_start': 1,
                    'disp_offset_len': 9
                },
                'A8_E1': {
                    'offset': (-8, 1),
                    'disp_offset_start': 2,
                    'disp_offset_len': 9
                },
                'A7_E2': {
                    'offset': (-7, 2),
                    'disp_offset_start': 3,
                    'disp_offset_len': 9
                }
            }
        }
    }
}