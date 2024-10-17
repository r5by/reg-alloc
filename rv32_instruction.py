import re
from instr_type import InstrType

class RV32Instructions(InstrType):

    def __init__(self, line_num, text):
        super().__init__(line_num, text)

        # assembly-related
        self.label = None
        self.opcode = None
        self.operands = []

        # init
        self.parse_instruction()
        self.analyze_defs_uses()

    def parse_instruction(self):
        # Check for label
        if ':' in self.text:
            parts = self.text.split(':')
            self.label = parts[0].strip()
            rest = ':'.join(parts[1:]).strip()
        else:
            rest = self.text

        # Parse opcode and operands
        if rest:
            tokens = rest.strip().split(None, 1)
            self.opcode = tokens[0]
            if len(tokens) > 1:
                operands = tokens[1]
                self.operands = [operand.strip() for operand in operands.split(',')]

    def analyze_defs_uses(self):
        if not self.opcode:
            return
        opcode = self.opcode
        operands = self.operands

        # Pattern to match registers (including virtual ones)
        # todo> update this to match only rv32i valid register names
        reg_pattern = re.compile(r'^(x[0-9]+|[a-z]+[0-9]*|v[0-9]+)$')

        def is_register(s):
            return reg_pattern.match(s) is not None

        # Update instruction parsing to recognize virtual registers
        # Handle R-type instructions
        if opcode in {'add', 'sub', 'mul', 'sll', 'srl', 'sra', 'or', 'and', 'xor', 'slt', 'sltu'}:
            if len(operands) >= 3:
                rd, rs1, rs2 = operands[:3]
                if is_register(rd):
                    self.defs.add(rd)
                if is_register(rs1):
                    self.uses.add(rs1)
                if is_register(rs2):
                    self.uses.add(rs2)
        # Handle I-type instructions
        elif opcode in {'addi', 'andi', 'ori', 'xori', 'slli', 'srli', 'srai', 'slti', 'sltiu', 'li', 'lui'}:
            if len(operands) >= 2:
                rd, rs1 = operands[:2]
                if is_register(rd):
                    self.defs.add(rd)
                if is_register(rs1) and opcode != 'li':
                    self.uses.add(rs1)
        # Handle load and store instructions
        elif opcode in {'lw', 'lb', 'lh', 'lbu', 'lhu'}:
            if len(operands) >= 2:
                rd, mem_operand = operands[:2]
                if is_register(rd):
                    self.defs.add(rd)
                base_reg = self.extract_base_reg(mem_operand)
                if is_register(base_reg):
                    self.uses.add(base_reg)
        elif opcode in {'sw', 'sb', 'sh'}:
            if len(operands) >= 2:
                rs2, mem_operand = operands[:2]
                if is_register(rs2):
                    self.uses.add(rs2)
                base_reg = self.extract_base_reg(mem_operand)
                if is_register(base_reg):
                    self.uses.add(base_reg)
        # Handle branch instructions
        elif opcode in {'beq', 'bne', 'blt', 'bge', 'bltu', 'bgeu'}:
            if len(operands) >= 2:
                rs1, rs2 = operands[:2]
                if is_register(rs1):
                    self.uses.add(rs1)
                if is_register(rs2):
                    self.uses.add(rs2)
        # Handle jump and move instructions
        elif opcode == 'mv':
            if len(operands) >= 2:
                rd, rs = operands[:2]
                if is_register(rd):
                    self.defs.add(rd)
                if is_register(rs):
                    self.uses.add(rs)
        elif opcode == 'jr':
            if len(operands) >= 1:
                rs = operands[0]
                if is_register(rs):
                    self.uses.add(rs)
        elif opcode == 'j':
            pass  # No defs or uses
        elif opcode == 'jal' or opcode == 'jalr':
            if len(operands) >= 1:
                rd = operands[0]
                if is_register(rd):
                    self.defs.add(rd)
        elif opcode == 'ret':
            self.uses.add('ra')
        # Add more instructions as needed

    def extract_base_reg(self, mem_operand):
        # Extracts the base register from memory operand like offset(reg)
        if '(' in mem_operand and ')' in mem_operand:
            base_reg = mem_operand[mem_operand.find('(')+1:mem_operand.find(')')]
            return base_reg.strip()
        return None