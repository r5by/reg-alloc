from instr_type import InstrType, IS_BLK, IS_INSTR, IS_BLK_E, IS_RET, IS_BRANCH
import re

pat_func_sign = r'^\s*([a-zA-Z_][a-zA-Z0-9_]*\s+\*?\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*\(([^)]*)\)'
pat_func_args = re.compile(r'\b(?:unsigned\s+)?\w+\s*[\*]*\s*(\w+)')

class CStyleInstruction(InstrType):
    def __init__(self, line_num, text):
        super().__init__(line_num, text)
        self.operation = None
        self.operands = []
        self.parse_instruction()
        self.analyze_defs_uses()

    def parse_instruction(self):
        line = self.text.strip()

        if not line: # skip empty lines
            return

        # Handle block indicators
        # todo> make this able to handle general valid C/C++ blocks of code
        if line.endswith('{'):
            self.mask |= IS_BLK | IS_INSTR
            line = line[:-1].strip()
        elif line == '}':
            self.mask |= IS_BLK_E
            self.operation = 'block_end'
            return
        else:
            self.mask |= IS_INSTR

        # Remove semicolons at the end
        if line.endswith(';'):
            line = line[:-1].strip()

        # Handle control flow statements
        if line.startswith('while'):
            condition = line[line.find('(')+1:line.rfind(')')].strip()
            self.operation = 'while'
            self.operands = [condition]
            self.mask |= IS_BRANCH
        elif line.startswith('if'):
            condition = line[line.find('(')+1:line.rfind(')')].strip()
            self.operation = 'if'
            self.operands = [condition]
            self.mask |= IS_BRANCH
        elif line.startswith('return'):
            expr = line[6:].strip()
            self.operation = 'return'
            self.operands = [expr]
            self.mask |= IS_RET
        elif '++' in line:
            expr = line
            var = line.replace('++', '').strip()
            self.operands = [var, expr]
            self.operation = 'assign'
        elif '=' in line:
            var, expr = line.split('=', 1)
            var = var.strip()
            expr = expr.strip()
            self.operation = 'assign'
            self.operands = [var, expr]
        elif re.match(pat_func_sign, line):
            self.operation = 'func'
            self.operands = re.match(pat_func_sign, line).group(3)
        else:
            self.operation = 'expression'
            self.operands = [line]

    def analyze_defs_uses(self):

        if self.operation == 'assign':
            var = self.operands[0]
            expr = self.operands[1]
            self.defs.update(self.extract_variables(var))
            self.uses.update(self.extract_variables(expr))
        elif self.operation in {'return', 'expression'}:
            expr = self.operands[0]
            self.uses.update(self.extract_variables(expr))
        elif self.operation in {'while', 'if'}:
            condition = self.operands[0]
            self.uses.update(self.extract_variables(condition))
        elif self.operation == 'func':
            args = self.extract_func_args(self.operands)
            self.uses.update(args)

    def extract_func_args(self, arguments):
        # Regular expression pattern to find variable names
        # Looks for optional pointers (*) followed by word characters (alphanumeric + '_')

        # Find all matches in the input string
        variables = pat_func_args.findall(arguments)
        return variables

    def extract_variables(self, expr):
        tokens = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', expr)
        keywords = {'int', 'return', 'while', 'if'}
        variables = set(token for token in tokens if token not in keywords)
        return variables
