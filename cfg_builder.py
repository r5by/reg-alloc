from abc import ABC, abstractmethod

import matplotlib.pyplot as plt
import networkx as nx
from rv32_instruction import RV32Instructions
from clike_instruction import CStyleInstruction
from bb import BasicBlock

class CFG:
    '''
        A Control Flow Graph (CFG) contains:
            1) list of vertices (V), a.k.a nodes repr. basic blocks of code
            2) list of directed edges (E), simply as tuples of vertices.
    '''
    def __init__(self):
        self.V = []  # List of basic blocks
        self.E = []  # List of edges (tuples of block IDs)

class CFGBuilder(ABC):
    def __init__(self, lines):
        self.lines = lines
        self.instructions = []
        self.ctrl_boaders = {} # dict of control blocks, inclusive format: blk_start_instr_id ==> blk_end_instr_id
        self.instr_2_blk_id = [] # get block id of given instruction id
        self.basic_blocks = []
        self.cfg = CFG()
        self.build_cfg()

    @abstractmethod
    def parse_instructions(self):
        pass

    @abstractmethod
    def identify_leaders(self):
        pass

    @abstractmethod
    def build_basic_blocks(self):
        pass

    @abstractmethod
    def build_cfg_edges(self):
        pass

    @abstractmethod
    def merge_basic_blocks(self):
        pass

    def build_cfg(self):
        self.parse_instructions()
        self.identify_leaders()
        self.build_basic_blocks()
        self.build_cfg_edges()
        self.merge_basic_blocks()
        self.perform_liveness_analysis()

    def perform_liveness_analysis(self):
        # Liveness analysis implementation
        pass

    # Other common methods can be defined here



# Example usage:
if __name__ == '__main__':
    # Prepare the C-style instructions
    c_instructions = [
        'int z = 10;',
        'int x = 0;',
        'int y = 1;',
        'while(x < n) {',
        '    z = x * 2 + y;',
        '    x++;',
        '    y = x + z;',
        '}',
        'return y;'
    ]

    # print("Detailed CFG:")
    # # Initialize the CFGBuilder with detailed=True
    # cfg_builder_detailed = CFGBuilder(c_instructions, CStyleInstruction, detailed=True)
    # cfg_builder_detailed.print_liveness()
    # cfg_builder_detailed.plot_cfg()

    print("\nSimplified CFG:")
    # Initialize the CFGBuilder with detailed=False
    cfg_builder_simplified = CFGBuilder(c_instructions, CStyleInstruction, detailed=False)
    cfg_builder_simplified.print_liveness()
    cfg_builder_simplified.plot_cfg()

    # code = [
    #     'foo:', # <--leader
    #     'addi sp, sp, -12',
    #     'sw s0, 8(sp)',
    #     'sw s1, 4(sp)',
    #     'sw s2, 0(sp)', #4,
    #
    #     'li s2, 10', # 5, z=>s2
    #     'li s0, 0', # x=>s0
    #     'li s1, 1', # 7, y=>s1
    #
    #     'loop_start:', # 8, <--leader
    #     'blt s0, a0, loop_body', # n=>a0
    #     'j loop_end', # 10, <--leader
    #
    #     'loop_body:', # 11, <--leader
    #     'slli t0, s0, 1',
    #     'add s2, t0, s1', # s2<=z=x*2+y
    #     'addi s0, s0, 1', # s0<=x++
    #     'add s1, s0, s2', # y = x + z
    #     'j loop_start', # 16,
    #
    #     'loop_end:', #17, <--leader
    #     'mv a0, s1',
    #     'lw s2, 0(sp)',
    #     'lw s1, 4(sp)',
    #     'lw s0, 8(sp)',
    #     'addi sp, sp, 12',
    #     'jr ra'
    # ]
    #
    # cfg_builder = CFGBuilder(code, RV32Instructions)
    # # cfg_builder.print_detailed_cfg()
    # # cfg_builder.print_cfg()
    # cfg_builder.print_liveness()
    # # Optionally, plot the CFG
    # cfg_builder.plot_cfg()
