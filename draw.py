from __future__ import annotations
from argparse import ArgumentParser
import json
from itertools import chain
import math

from load_settings import settings
from tree import *

from PIL import Image, ImageDraw, ImageFont


def arrowedLine(canvas, ptA: Vec2, ptB: Vec2, width=1, color=settings['color']):
    """Draw line from ptA to ptB with arrowhead at ptB"""
    # Get drawing context
    # Draw the line without arrows
    canvas.line(flatten_vectors(ptA, ptB), width=width, fill=color)

    # Now work out the arrowhead
    # = it will be a triangle with one vertex at ptB
    # - it will start at 95% of the length of the line
    # - it will extend 8 pixels either side of the line
    x0, y0 = ptA
    x1, y1 = ptB
    # Now we can work out the x,y coordinates of the bottom of the arrowhead triangle
    xb = 0.95*(x1-x0)+x0
    yb = 0.95*(y1-y0)+y0

    # Work out the other two vertices of the triangle
    # Check if line is vertical
    if x0==x1:
       vtx0 = (xb-5, yb)
       vtx1 = (xb+5, yb)
    # Check if line is horizontal
    elif y0==y1:
       vtx0 = (xb, yb+5)
       vtx1 = (xb, yb-5)
    else:
       alpha = math.atan2(y1-y0,x1-x0)-90*math.pi/180
       a = 8*math.cos(alpha)
       b = 8*math.sin(alpha)
       vtx0 = (xb+a, yb+b)
       vtx1 = (xb-a, yb-b)

    #draw.point((xb,yb), fill=(255,0,0))    # DEBUG: draw point of base in red - comment out draw.polygon() below if using this line
    #im.save('DEBUG-base.png')              # DEBUG: save

    # Now draw the arrowhead triangle
    canvas.polygon([vtx0, vtx1, ptB.as_tuple()], fill=color)


class Vec2:
    __slots__ = 'x', 'y'

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

    def __iter__(self):
        return iter((self.x, self.y))

    def clone(self) -> Vec2:
        """Return a new vector with exactly the same data.
        :return: The new vector
        """
        return Vec2(self.x, self.y)

    def __sub__(self, other: Vec2 | tuple) -> Vec2:
        if isinstance(other, Vec2):
            return Vec2(self.x - other.x, self.y - other.y)
        if isinstance(other, tuple):
            return Vec2(self.x - other[0], self.y - other[1])

    def __add__(self, other: Vec2 | tuple) -> Vec2:
        if isinstance(other, Vec2):
            return Vec2(self.x + other.x, self.y + other.y)
        if isinstance(other, tuple):
            return Vec2(self.x + other[0], self.y + other[1])

    def __mul__(self, other: int | float | Vec2) -> Vec2:
        if isinstance(other, int) or isinstance(other, float):
            return Vec2(self.x * other, self.y * other)
        if isinstance(other, Vec2):
            return Vec2(self.x * other.x, self.y * other.y)


    __rmul__ = __mul__


    def __repr__(self) -> str:
        return f'<x={self.x}, y={self.y}>'


def flatten_vectors(*vectors) -> (int | float, int | float, int | float, int | float):

    """Join vectors together into a tuple of len(vecs) * 2 elements.
    :param vectors: vectors to flatten
    :return: The resulting tuple
    """
    return tuple(chain( (v.x, v.y) for v in vectors ))



class TreeVisualizer:

    def __init__(self, _tree: Tree) -> None:
        """Visualize a tree by drawing a graph."""

        self.tree = _tree
        self.n = settings['d']
        self.bl_size = Vec2(settings['block-width'], settings['block-height'])
        self.bl_size_2 = Vec2(settings['block-width'] - 5, settings['block-height'])
        self.node_size = self.bl_size * Vec2(self.n, 3)
        self.ch_size = Vec2(self.node_size.x / (self.n + 1), settings['block-height'])
        self.margin = Vec2(settings['margin'], settings['margin'])
        self.separation = Vec2(settings['horizontal-separation'], settings['vertical-separation'])
        self.font = ImageFont.truetype(settings['font-family'], settings['font-size'])
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

        # draw the rectangles

        start_row = 1 if settings['show-name'] else 0

        # Draw the name
        if settings['show-name']:
            canvas.rectangle(flatten_vectors(pos, pos + self.bl_size * Vec2(self.n, 1)), outline=settings['color'])
            center = pos + self.bl_size * Vec2(self.n, 1) * 0.5
            canvas.text(center.as_tuple(), node.name, anchor='mm', font=self.font, fill=settings['color'])

        # draw row
        top_left = pos - (10, 0)
        bot_right = pos + self.ch_size * Vec2(self.n, start_row + 1) - (10, 0)
        canvas.rectangle(flatten_vectors(top_left, bot_right), outline=settings['color'])
        # draw separators
        for i in range(self.n):
            upper_left = top_left + self.bl_size * Vec2(i, start_row)
            canvas.rectangle(flatten_vectors(upper_left, upper_left + (10, self.bl_size.y)), outline=settings['color'])

        # Draw the data
        for (i, data) in enumerate(node.data_arr):
            center = pos + self.bl_size * Vec2(i + 0.4, start_row + 0.55)
            if isinstance(data, list):
                canvas.text(center.as_tuple(), str(data[0]), anchor='mm', font=self.font, fill=data[1])
            else:
                canvas.text(center.as_tuple(), str(data), anchor='mm', font=self.font, fill=settings['color'])

        # Draw connections or lines to parent
        if connect_to_parent and node.parent is not None:
            child_top = pos + self.bl_size * Vec2(len(node.data_arr) / 2, 0)
            parent_sep = self.positions[node.parent.name] + self.bl_size * Vec2(node.parent.children.index(node) + 0.5, 3 - (2 - start_row)) - (self.bl_size.x - 24, 0)
            arrowedLine(canvas, parent_sep, child_top)

        if connect_to_right and node in self.tree.nodes[-1][:-1]:
            child_end = pos + self.ch_size * Vec2(self.n, 2.5 - (2 - start_row)) - (10, 0)
            sibling_start = child_end + self.separation * Vec2(1.7, 0)
            arrowedLine(canvas, child_end, sibling_start)
            # canvas.line(flatten_vectors(start, end), fill=settings['color'], width=1)

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
        with Image.new('RGB', self.dimensions.as_tuple(), settings['background']) as image:
            canvas = ImageDraw.Draw(image)
            self._draw_tree(canvas)
            image.save(path, 'PNG')


if __name__ == '__main__':
    # parse arguments
    parser = ArgumentParser()
    parser.add_argument('--input', default='in.json')
    parser.add_argument('-o', '--out', default='out.png')
    args = parser.parse_args()
    # initialize
    tree = Tree()
    with open(args.input, 'r') as fp:
        tree.load(json.load(fp))
    print(tree)
    # draw
    vis = TreeVisualizer(tree)
    vis.export(args.out)
