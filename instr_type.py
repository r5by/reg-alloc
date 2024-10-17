from abc import ABC, abstractmethod


IS_INSTR    = 0b00001       # normal instruction
IS_RET      = 0b00010       # return
IS_BRANCH   = 0b00100       # branch (while loop or if branch)
IS_BLK      = 0b01000       # Block start
IS_BLK_E    = 0b10000       # Block end

class InstrType(ABC):

    def __init__(self, line_num, text):
        self.line_num = line_num
        self.text = text.strip()
        self.defs = set()
        self.uses = set()
        self.mask = 0  # Initialize mask

    @abstractmethod
    def parse_instruction(self):
        pass

    @abstractmethod
    def analyze_defs_uses(self):
        pass
