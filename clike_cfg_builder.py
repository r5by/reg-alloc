from cfg_builder import CFGBuilder, CFG
from clike_instruction import CStyleInstruction
from instr_type import InstrType, IS_BLK, IS_INSTR, IS_BLK_E, IS_RET, IS_BRANCH
from bb import BasicBlock

class ClikeCFGBuilder(CFGBuilder):
    def __init__(self, lines):
        super().__init__(lines)

    def parse_instructions(self):
        self.instructions = []

        for idx, line in enumerate(self.lines):
            stripped_line = line.strip()
            instr = CStyleInstruction(idx, stripped_line)

            if instr.mask & IS_BLK_E:
                # pass block end mark to the previous instruction
                self.instructions[-1].mask |= IS_BLK_E

            # Add instruction if it's an actual instruction
            if instr.mask & IS_INSTR:
                self.instructions.append(instr)

    def identify_leaders(self, bb_enabled=False):
        self.leaders = set()
        self.leaders.add(0)  # First instruction is always a leader

        for idx, instr in enumerate(self.instructions):
            if not bb_enabled:
                self.leaders.add(idx) # every instruction is a block leader if basic block is disabled
                continue

            if instr.operation == 'func':
                self.leaders.add(idx + 1) # the first instruction in function body is always a leader

            if instr.mask & IS_BLK:
                self.leaders.add(idx) # blk start instruction is always a leader

            if instr.mask & IS_BLK_E:
                if idx + 1 < len(self.instructions): # blk end instruction's next instruction is always a leader
                    self.leaders.add(idx + 1)

            if instr.mask & IS_BRANCH:
                self.leaders.add(idx)
                if idx + 1 < len(self.instructions):
                    self.leaders.add(idx + 1)

            if instr.mask & IS_RET:
                self.leaders.add(idx)

    def build_basic_blocks(self):
        sorted_leaders = sorted(self.leaders)
        leader_to_block = {}
        for i, leader in enumerate(sorted_leaders):
            block = BasicBlock(i)
            leader_to_block[leader] = block
            self.basic_blocks.append(block)
            self.cfg.V.append(block)

        ctrl_stack = []
        current_block = None
        for idx, instr in enumerate(self.instructions):

            # pop control block boarders
            if instr.operation == 'func' or instr.mask & IS_BRANCH:
                ctrl_stack.append(idx)
            elif instr.mask & IS_BLK_E:
                prev_ctrl = ctrl_stack.pop()
                self.ctrl_boaders[prev_ctrl] = idx

            # pop leader instruction id's
            if idx in self.leaders:
                current_block = leader_to_block[idx]

            current_block.add_instruction(instr)
            if instr.mask & IS_BLK_E:
                current_block.is_end_blk = True

            self.instr_2_blk_id.append(current_block.id)

    def build_cfg_edges(self):
        total_blocks = len(self.basic_blocks)
        instr_idx_to_block_id = self.instr_2_blk_id

        for blk_id, block in enumerate(self.basic_blocks):
            blk_leader = block.instructions[0]
            blk_leader_idx = self.instructions.index(blk_leader)
            next_blk_id = blk_id + 1 if blk_id + 1 < total_blocks else None

            # handle branch block
            if blk_leader.mask & IS_BRANCH:

                # 1) Edge from condition to control body
                ctrl_body_blk_id = blk_id + 1
                if ctrl_body_blk_id >= total_blocks:
                    raise ValueError(f'Unfinished control block detected: {block.instructions}')

                block.succ.add(ctrl_body_blk_id)
                self.basic_blocks[ctrl_body_blk_id].pred.add(blk_id)
                self.cfg.E.append((blk_id, ctrl_body_blk_id))

                # if the control block is a loop, then add
                # Edge from last block in loop body back to condition
                ctrl_end_instr_idx = self.ctrl_boaders[blk_leader_idx]
                ctrl_body_last_blk_id = self.instr_2_blk_id[ctrl_end_instr_idx]
                if blk_leader.operation == 'while':
                    block.pred.add(ctrl_body_last_blk_id)
                    self.basic_blocks[ctrl_body_last_blk_id].succ.add(blk_id)
                    self.cfg.E.append((ctrl_body_last_blk_id, blk_id))

                # 2) Edge from condition to block after the control block
                after_blk_instr_idx = ctrl_end_instr_idx + 1
                if after_blk_instr_idx >= len(self.instructions):
                    continue # no more instructions after this control block

                after_ctrl_blk_id = instr_idx_to_block_id[after_blk_instr_idx]
                block.succ.add(after_ctrl_blk_id)
                self.basic_blocks[after_ctrl_blk_id].pred.add(blk_id)
                self.cfg.E.append((blk_id, after_ctrl_blk_id))
                continue

            elif blk_leader.mask & IS_RET:
                # Return statement; no successors
                continue

            # Sequential flow to the next block
            if next_blk_id is not None and not block.is_end_blk:
                block.succ.add(next_blk_id)
                self.basic_blocks[next_blk_id].pred.add(blk_id)
                self.cfg.E.append((blk_id, next_blk_id))

    def cleanup(self):
        self.ctrl_boaders = {} # dict of control blocks, inclusive format: blk_start_instr_id ==> blk_end_instr_id
        self.instr_2_blk_id = [] # get block id of given instruction id
        self.basic_blocks = []
        self.cfg = CFG()

    def merge_basic_blocks(self):
        # pseudo merge, we actually rebuild the entire cfg for easy impl.
        self.cleanup()
        self.identify_leaders(bb_enabled=True)
        self.build_basic_blocks()
        self.build_cfg_edges()
