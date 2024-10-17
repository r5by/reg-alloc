from instr_type import InstrType

class BasicBlock:
    def __init__(self, id):
        self.id = id
        self.is_end_blk = False # is this block end of a control block?
        self.instructions = []

        # predecessors and successors
        self.pred = set()
        self.succ = set()

        # for liveness analysis
        self.defs = set()  # a.k.a "kills"
        self.uses = set()  # a.k.a "gens"
        self.live_in = set()
        self.live_out = set()

    def add_instruction(self, instr: InstrType):
        self.instructions.append(instr)

    def compute_defs_uses(self):
        self.defs = set()
        self.uses = set()
        assigned = set()
        for instr in self.instructions:
            # For each use
            for reg in instr.uses:
                if reg not in assigned:
                    self.uses.add(reg)

            # For each def
            for reg in instr.defs:
                assigned.add(reg)
                self.defs.add(reg)