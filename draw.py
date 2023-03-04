from __future__ import annotations

from argparse import ArgumentParser
import json
from PIL import Image, ImageDraw, ImageFont

from load_settings import settings
from tree import *


class Vec2:
    def __init__(self, x: int | float, y: int | float) -> None:
        """A two-dimensional vector. Can be used to specify a location on the canvas.

        :param x: X component of the vector (horizontal distance to the left edge in pixels)
        :param y: Y component of the vector (vertical distance to the top edge in pixels)
        """
        self.x = x
        self.y = y

    def as_tuple(self) -> (int | float, int | float):
        """Convert the vector object into a tuple.

        :return: A tuple containing x and y values
        """
        return self.x, self.y

    def clone(self) -> Vec2:
        """Return a new vector with exactly the same data.

        :return: The new vector
        """
        return Vec2(self.x, self.y)

    def __add__(self, other: Vec2) -> Vec2:
        return Vec2(self.x + other.x, self.y + other.y)

    def __mul__(self, other: int | float | Vec2) -> Vec2:
        if isinstance(other, int) or isinstance(other, float):
            return Vec2(self.x * other, self.y * other)
        elif isinstance(other, Vec2):
            return Vec2(self.x * other.x, self.y * other.y)
    __rmul__ = __mul__

    def __str__(self) -> str:
        return f"<x={self.x}, y={self.y}>"
    __repr__ = __str__


def join(v1: Vec2, v2: Vec2) -> (int | float, int | float, int | float, int | float):
    """Join the vectors together into a tuple of 4 elements.

    :param v1: First vector
    :param v2: Second vector
    :return: The resulting tuple
    """
    return v1.x, v1.y, v2.x, v2.y


class TreeVisualizer:
    def __init__(self, _tree: Tree) -> None:
        """Visualize a tree by drawing a graph."""
        self.tree = _tree
        self.n = settings["d"] * 2

        self.bl_size = Vec2(settings["block-width"], settings["block-height"])
        self.node_size = self.bl_size * Vec2(self.n, 3)
        self.ch_size = Vec2(self.node_size.x / (self.n + 1), settings["block-height"])
        self.margin = Vec2(settings["margin"], settings["margin"])
        self.separation = Vec2(settings["horizontal-separation"], settings["vertical-separation"])

        self.font = ImageFont.truetype(settings["font-family"], settings["font-size"])

        # temporary data used when drawing graphs
        self.dimensions = None
        self.positions = None

    def _draw_node(self, canvas: ImageDraw, node: Node, connect_to_parent: bool = False,
                   connect_to_right: bool = False):
        """Draw the specified node at the location recorded in `self.positions`.

        :param canvas: The canvas to draw on
        :param node: The node to be drawn
        :param connect_to_parent: Specifies whether to draw the line connecting to the parent
        :param connect_to_right: Specifies whether to draw the line connecting to the leaf on the right
        """
        pos = self.positions[node.name]

        # Draw the rectangles
        canvas.rectangle(join(pos, pos + self.bl_size * Vec2(self.n, 1)), outline=0x000000)
        for i in range(self.n):
            upper_left = pos + self.bl_size * Vec2(i, 1)
            canvas.rectangle(join(upper_left, upper_left + self.bl_size), outline=0x000000)
        for i in range(self.n + 1):
            upper_left = pos + self.ch_size * Vec2(i, 2)
            canvas.rectangle(join(upper_left, upper_left + self.ch_size), outline=0x000000)

        # Draw the name
        center = pos + self.bl_size * Vec2(self.n, 1) * 0.5
        canvas.text(center.as_tuple(), node.name, anchor="mm", font=self.font, fill=0x000000)

        # Draw the data
        for (i, data) in enumerate(node.data_arr):
            center = pos + self.bl_size * Vec2(i + 0.5, 1.5)
            canvas.text(center.as_tuple(), str(data), anchor="mm", font=self.font, fill=0x000000)

        # Draw connection to parent
        if connect_to_parent and node.parent is not None:
            start = pos + self.node_size * Vec2(0.5, 0)
            end = self.positions[node.parent.name] + self.ch_size * Vec2(node.parent.children.index(node) + 0.5, 3)
            canvas.line(join(start, end), fill=0x000000, width=1)

        if connect_to_right and node in self.tree.nodes[-1][:-1]:
            start = pos + self.ch_size * Vec2(self.n + 1, 2.5)
            end = start + self.separation * Vec2(1, 0)
            canvas.line(join(start, end), fill=0x000000, width=1)

    def _draw_tree(self, canvas: ImageDraw) -> None:
        """Draw the entire tree using the information in `self.positions`.

        :param canvas: The canvas to draw on
        """
        for level in self.tree.nodes:
            for node in level:
                self._draw_node(canvas, node, connect_to_parent=True, connect_to_right=True)

    def analyze_tree(self) -> None:
        """Calculate the dimensions of the image and positions of each node."""
        count = Vec2(self.tree.nleaves(), self.tree.nlevels())
        self.dimensions = self.margin * 2 + self.node_size * count + self.separation * (count + Vec2(-1, -1))

        j = count.y - 1

        # calculate position of leaves
        self.positions = {
            leaf.name: self.margin + (self.node_size + self.separation) * Vec2(i, j)
            for (i, leaf) in enumerate(self.tree.nodes[-1])
        }

        # calculate position of other nodes
        for level in reversed(self.tree.nodes[:-1]):
            j -= 1
            pos = self.margin + (self.node_size.y + self.separation.y) * Vec2(0, j)
            for node in level:
                if len(node.children) == 0:
                    pos.x += (self.node_size.x + self.separation.x)
                else:
                    pos.x = sum([self.positions[child.name].x for child in node.children]) / len(node.children)
                self.positions[node.name] = pos.clone()

    def export(self, path: str) -> None:
        """Export the image in PNG format to a file.

        :param path: The path to the destination file
        """
        self.analyze_tree()
        print(self.dimensions)
        with Image.new("RGB", self.dimensions.as_tuple(), 0xffffff) as image:
            canvas = ImageDraw.Draw(image)
            self._draw_tree(canvas)
            with open(path, 'wb') as out:
                image.save(out, "PNG")


if __name__ == "__main__":
    # parse arguments
    parser = ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("-o", "--out")
    args = parser.parse_args()

    # initialize
    tree = Tree()
    with open(args.input, "r") as fp:
        tree.load(json.load(fp))
    print(tree)

    # draw
    vis = TreeVisualizer(tree)
    vis.export(args.out)
