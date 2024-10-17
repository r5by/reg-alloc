import networkx as nx
import matplotlib.pyplot as plt
from clike_cfg_builder import ClikeCFGBuilder

class CFGAnalyzer:
    def __init__(self, cfg_builder):
        self.cfg_builder = cfg_builder
        self.basic_blocks = cfg_builder.basic_blocks
        self.cfg = cfg_builder.cfg

    def perform_liveness_analysis(self):
        # Initialize live_in and live_out sets
        for block in self.basic_blocks:
            block.live_in = set()
            block.live_out = set()

        changed = True
        while changed:
            changed = False
            # Process blocks in reverse order
            for block in reversed(self.basic_blocks):
                old_live_in = block.live_in.copy()
                old_live_out = block.live_out.copy()

                # LIVEout[n] = union over successors s of LIVEin[s]
                block.live_out = set()
                for succ_id in block.succ:
                    succ_block = self.basic_blocks[succ_id]
                    block.live_out |= succ_block.live_in

                # LIVEin[n] = use[n] union (LIVEout[n] - def[n])
                block.live_in = block.uses | (block.live_out - block.defs)

                if old_live_in != block.live_in or old_live_out != block.live_out:
                    changed = True

    def print_liveness(self):
        for idx, block in enumerate(self.basic_blocks):
            print(f'Basic Block v{idx}:')
            print(f'  Instructions:')
            for instr in block.instructions:
                print(f'    {instr.line_num}: {instr.text}')
            print(f'  Defs: {block.defs}')
            print(f'  Uses: {block.uses}')
            print(f'  Live-in: {block.live_in}')
            print(f'  Live-out: {block.live_out}')
            print()

    def plot_cfg(self):
        G = nx.DiGraph()
        # Add nodes
        for idx, block in enumerate(self.cfg.V):
            node_label = f'v{idx}'
            # Optionally, add instructions to the node label
            instr_texts = [instr.text.strip() for instr in block.instructions]
            instr_summary = '\n'.join(instr_texts)
            G.add_node(node_label, label=node_label, instr=instr_summary)
        # Add edges
        for edge in self.cfg.E:
            src_id, dest_id = edge
            src_label = f'v{src_id}'
            dest_label = f'v{dest_id}'
            G.add_edge(src_label, dest_label)
        # Use the graphviz 'dot' layout for vertical arrangement
        try:
            pos = nx.nx_pydot.graphviz_layout(G, prog='dot')
        except:
            # If pygraphviz is not installed, fall back to spring_layout
            print("PyGraphviz is not installed. Please install it to get a better layout.")
            pos = nx.spring_layout(G)
        # Draw nodes
        nx.draw_networkx_nodes(G, pos, node_color='lightblue', node_size=1500)
        # Draw edges
        nx.draw_networkx_edges(G, pos, arrowstyle='->', arrowsize=20)
        # Draw labels
        labels = {node: node for node in G.nodes()}
        nx.draw_networkx_labels(G, pos, labels, font_size=10)
        # Optionally, display instruction summaries
        node_instrs = nx.get_node_attributes(G, 'instr')
        for node, (x, y) in pos.items():
            instrs = node_instrs[node]
            plt.text(x, y - 30, instrs, fontsize=8, ha='center', va='top')
        plt.axis('off')
        plt.show()


if __name__ == '__main__':
    with open('./data/foo.c', 'r') as f:
        c_instructions = f.readlines()
    # c_instructions = [
    #     'int z = 10;',
    #     'int x = 0;',
    #     'int y = 1;',
    #     'while(x < n) {',
    #     '    z = x * 2 + y;',
    #     '    if (z > 20) {',
    #     '    x++;',
    #     '    y = x + z;',
    #     '}',
    #     'return y;'
    # ]

    # Build CFG for C-like code
    cfg_builder = ClikeCFGBuilder(c_instructions, detailed=False)
    # Analyze CFG
    cfg_analyzer = CFGAnalyzer(cfg_builder)
    cfg_analyzer.perform_liveness_analysis()
    cfg_analyzer.print_liveness()
    cfg_analyzer.plot_cfg()