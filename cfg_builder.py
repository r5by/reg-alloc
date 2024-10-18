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

