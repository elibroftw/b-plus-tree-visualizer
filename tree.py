from __future__ import annotations

from load_settings import settings


class Node:
    def __init__(self, name: str, data_arr: list, parent: Node | None = None) -> None:
        """Create a single node of a tree.

        :param name: The name of the node
        :param data_arr: The array of data stored in the node
        :param parent: The parent node (will automatically add as child)
        """
        self.name = name
        self.data_arr = data_arr
        self.parent = parent
        if parent is not None:
            parent._add_child(self)
        self.children = []

    def size(self) -> int:
        """Find the number of data stored in the node.

        :return: number of data
        """
        return len(self.data_arr)

    def _add_child(self, child: Node) -> None:
        """Adds a new node as the child of the tree. Doesn't do any checks.

        :param child: The node to add as child
        """
        self.children.append(child)

    def is_full(self) -> bool:
        """Checks if capable of adding more children.

        :return: `True` if having at least one more children than data
        """
        return len(self.children) >= len(self.data_arr) + 1

    def __repr__(self) -> str:
        parent = '' if self.parent is None else f'({self.parent.name})'
        return f'<{self.name} {parent}: {self.data_arr}, {[c.name for c in self.children]}>'


class Tree:
    def __init__(self) -> None:
        """Creates an empty tree."""
        self.nodes = []
        self.enumi = 0

    def load(self, tree_array: list[list[list]], *, append: bool = False) -> None:
        """Create new nodes from a given tree array.

        :param tree_array: The array to read from
        :param append: Will overwrite if set to `False`
        """
        if not append:
            self.nodes = [[]]
            self.enumi = 0

        for level in tree_array:
            i = 0
            new_level = []

            for data_arr in level:
                name = settings['node-name'].format(self.enumi)
                self.enumi += 1
                while i < len(self.nodes[-1]) and self.nodes[-1][i].is_full():
                    i += 1
                parent = self.nodes[-1][i] if i < len(self.nodes[-1]) else None
                new_level.append(Node(name, data_arr, parent))

            if len(self.nodes[-1]) == 0:
                self.nodes.pop(-1)
            self.nodes.append(new_level)

        if len(self.nodes[-1]) == 0:
            self.nodes.pop(-1)

    def nlevels(self) -> int:
        """Find the number of levels in the tree.

        :return: Number of levels
        """
        return len(self.nodes)

    def nnodes(self) -> int:
        """Find the number of nodes in the tree.

        :return: Number of nodes
        """
        return sum([len(level) for level in self.nodes])

    def nleaves(self) -> int:
        """Find the number of leaves in the tree

        :return: Number of leaves
        """
        return 0 if len(self.nodes) == 0 else len(self.nodes[-1])

    def root(self) -> Node | None:
        """Find the root of the tree.

        :return: `Node` root of the tree or `None` if tree is empty
        """
        return None if len(self.nodes) == 0 else self.nodes[0][0]

    def __repr__(self) -> str:
        string = ''
        for level in self.nodes:
            for (i, node) in enumerate(level):
                if i > 0:
                    string += '  '
                string += str(node)
            string += '\n'
        return string
