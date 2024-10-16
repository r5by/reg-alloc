import matplotlib.pyplot as plt
import networkx as nx

class Instruction:
    def __init__(self, line_num, text):
        self.line_num = line_num
        self.text = text.strip()
        self.label = None
        self.opcode = None
        self.operands = []
        self.parse_instruction()

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

class BasicBlock:
    def __init__(self, id):
        self.id = id
        self.instructions = []
        self.predecessors = set()
        self.successors = set()

    def add_instruction(self, instr):
        self.instructions.append(instr)

class CFG:
    '''
        A Control Flow Graph (CFG) contains:
            1) list of vertices (V), a.k.a nodes repr. basic blocks of code
            2) list of directed edges (E), simply as tuples of vertices.
    '''
    def __init__(self):
        self.V = []  # List of basic blocks
        self.E = []  # List of edges (tuples of basic blocks)

class CFGBuilder:
    def __init__(self, assembly_lines):
        self.assembly_lines = assembly_lines
        self.instructions = []
        self.labels = {}
        self.basic_blocks = []
        self.cfg = CFG()

        # construct the cfg
        self.build_cfg()

    def parse_instructions(self):
        for idx, line in enumerate(self.assembly_lines):
            instr = Instruction(idx, line)
            self.instructions.append(instr)
            if instr.label:
                self.labels[instr.label] = idx  # Map label to instruction index

    def identify_leaders(self):
        self.leaders = set()
        self.leaders.add(0)  # First instruction is a leader

        for idx, instr in enumerate(self.instructions):
            if instr.opcode and (instr.opcode.startswith('j') or instr.opcode.startswith('b')):
                # Next instruction is a leader (if any)
                if idx + 1 < len(self.instructions):
                    self.leaders.add(idx + 1)
                # Target of the jump or branch is a leader
                if instr.operands:
                    target_label = instr.operands[-1]
                    if target_label in self.labels:
                        target_idx = self.labels[target_label]
                        self.leaders.add(target_idx)
            elif instr.label:
                # Instruction with label is a leader
                self.leaders.add(idx)

    def build_basic_blocks(self):
        sorted_leaders = sorted(self.leaders)
        leader_to_block = {}
        for i, leader in enumerate(sorted_leaders):
            block = BasicBlock(i)
            leader_to_block[leader] = block
            self.basic_blocks.append(block)
            self.cfg.V.append(block)

        # Assign instructions to basic blocks
        current_block = None
        for idx, instr in enumerate(self.instructions):
            if idx in self.leaders:
                current_block = leader_to_block[idx]
            current_block.add_instruction(instr)

    def build_cfg_edges(self):
        instr_to_block = {}
        for block in self.basic_blocks:
            for instr in block.instructions:
                instr_to_block[instr.line_num] = block

        for block in self.basic_blocks:
            last_instr = block.instructions[-1]
            idx = last_instr.line_num
            if last_instr.opcode and (last_instr.opcode.startswith('j') or last_instr.opcode.startswith('b')):
                # Jump or branch instruction
                if last_instr.opcode == 'j':
                    # Unconditional jump
                    target_label = last_instr.operands[0]
                    if target_label in self.labels:
                        target_idx = self.labels[target_label]
                        target_block = instr_to_block[target_idx]
                        block.successors.add(target_block)
                        target_block.predecessors.add(block)
                        self.cfg.E.append((block, target_block))
                else:
                    # Conditional branch
                    # Edge to branch target
                    target_label = last_instr.operands[-1]
                    if target_label in self.labels:
                        target_idx = self.labels[target_label]
                        target_block = instr_to_block[target_idx]
                        block.successors.add(target_block)
                        target_block.predecessors.add(block)
                        self.cfg.E.append((block, target_block))
                    # Edge to fall-through block
                    if idx + 1 < len(self.instructions):
                        fall_through_block = instr_to_block.get(idx + 1)
                        if fall_through_block and fall_through_block != block:
                            block.successors.add(fall_through_block)
                            fall_through_block.predecessors.add(block)
                            self.cfg.E.append((block,                               fall_through_block))
            else:
                # Sequential flow to the next block
                if idx + 1 < len(self.instructions):
                    next_block = instr_to_block.get(idx + 1)
                    if next_block and next_block != block:
                        block.successors.add(next_block)
                        next_block.predecessors.add(block)
                        self.cfg.E.append((block, next_block))

    def build_cfg(self):
        self.parse_instructions()
        self.identify_leaders()
        self.build_basic_blocks()
        self.build_cfg_edges()

    def plot_cfg(self):
        G = nx.DiGraph()
        # Add nodes
        for idx, block in enumerate(self.cfg.V):
            node_label = f'v{idx}'
            # Optionally, add instructions to the node label
            instr_texts = [instr.text for instr in block.instructions]
            instr_summary = '\n'.join(instr_texts)
            G.add_node(node_label, label=node_label, instr=instr_summary)
        # Add edges
        for edge in self.cfg.E:
            src_idx = self.cfg.V.index(edge[0])
            dest_idx = self.cfg.V.index(edge[1])
            src_label = f'v{src_idx}'
            dest_label = f'v{dest_idx}'
            G.add_edge(src_label, dest_label)
        # Position nodes using a layout
        pos = nx.spring_layout(G)
        # Draw nodes
        nx.draw_networkx_nodes(G, pos, node_color='lightblue', node_size=200)
        # Draw edges
        nx.draw_networkx_edges(G, pos, arrowstyle='->', arrowsize=20)
        # Draw labels
        labels = {node: node for node in G.nodes()}
        nx.draw_networkx_labels(G, pos, labels, font_size=10)
        # Optionally, display instruction summaries
        # For longer blocks, you might want to disable this
        node_instrs = nx.get_node_attributes(G, 'instr')
        for node, (x, y) in pos.items():
            instrs = node_instrs[node]
            plt.text(x, y - 0.1, instrs, fontsize=8, ha='center', va='top')
        plt.axis('off')
        plt.show()

    def print_cfg(self):
        print('Vertices (Basic Blocks):')
        for idx, block in enumerate(self.cfg.V):
            print(f'v{idx}:')
            for instr in block.instructions:
                print(f'  {instr.text}')
        print('\nEdges:')
        for edge in self.cfg.E:
            src = self.cfg.V.index(edge[0])
            dest = self.cfg.V.index(edge[1])
            print(f'(v{src}, v{dest})')

    def print_detailed_cfg(self):
        print('Detailed CFG:')
        for idx, block in enumerate(self.cfg.V):
            print(f'Basic Block v{idx}:')
            for instr in block.instructions:
                print(f'  {instr.line_num}: {instr.text}')
            succ_ids = [self.cfg.V.index(succ) for succ in block.successors]
            pred_ids = [self.cfg.V.index(pred) for pred in block.predecessors]
            print(f'  Successors: {[f"v{s}" for s in succ_ids]}')
            print(f'  Predecessors: {[f"v{p}" for p in pred_ids]}')
            print()

# Example usage:
if __name__ == '__main__':
    assembly_code = [
        'foo:', # <--leader
        'addi sp, sp, -12',
        'sw s0, 8(sp)',
        'sw s1, 4(sp)',
        'sw s2, 0(sp)', #4,

        'li s2, 10', # 5, z=>s2
        'li s0, 0', # x=>s0
        'li s1, 1', # 7, y=>s1

        'loop_start:', # 8, <--leader
        'blt s0, a0, loop_body', # n=>a0
        'j loop_end', # 10, <--leader

        'loop_body:', # 11, <--leader
        'slli t0, s0, 1',
        'add s2, t0, s1', # s2<=z=x*2+y
        'addi s0, s0, 1', # s0<=x++
        'add s1, s0, s2', # y = x + z
        'j loop_start', # 16,

        'loop_end:', #17, <--leader
        'mv a0, s1',
        'lw s2, 0(sp)',
        'lw s1, 4(sp)',
        'lw s0, 8(sp)',
        'addi sp, sp, 12',
        'jr ra'
    ]

    cfg_builder = CFGBuilder(assembly_code)
    cfg_builder.print_detailed_cfg()
    cfg_builder.print_cfg()
    cfg_builder.plot_cfg()
