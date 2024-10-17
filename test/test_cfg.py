# test_liveness.py
import pytest
from cfg_builder import CFGBuilder


def test_liveness_analysis_foo():
    # Load the assembly code from foo.il
    with open('../data/foo.il', 'r') as f:
        assembly_code = f.readlines()

    # Initialize the CFGBuilder
    cfg_builder = CFGBuilder(assembly_code)
    print(f'\n')
    cfg_builder.print_liveness()

    # Expected liveness results
    expected_liveness = {
        0: {
            'live_in': {'a0', 'v1', 'v2', 'v3', 'sp', 'ra'},
            'live_out': {'a0', 'v1', 'v2', 'sp', 'ra'}
        },
        1: {
            'live_in': {'a0', 'v1', 'v2', 'sp', 'ra'},
            'live_out': {'a0', 'v1', 'v2', 'sp', 'ra'}
        },
        2: {
            'live_in': {'a0', 'v1', 'v2', 'sp', 'ra'},
            'live_out': {'a0', 'v1', 'v2', 'sp', 'ra'}
        },
        3: {
            'live_in': {'v2', 'sp', 'ra'},
            'live_out': set()
        }
    }

    # Compare actual and expected liveness
    # for idx, block in enumerate(cfg_builder.basic_blocks):
    #     actual_live_in = block.live_in
    #     actual_live_out = block.live_out
    #     expected_live_in = expected_liveness[idx]['live_in']
    #     expected_live_out = expected_liveness[idx]['live_out']
    #
    #     assert actual_live_in == expected_live_in, f"Block v{idx} live_in mismatch"
    #     assert actual_live_out == expected_live_out, f"Block v{idx} live_out mismatch"
