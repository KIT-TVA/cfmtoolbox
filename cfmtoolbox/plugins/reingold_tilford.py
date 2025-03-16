import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from typing import Tuple, List
import numpy as np
from io import BytesIO
from cfmtoolbox import CFM, Cardinality

class GraphLayout:
    """
    This class uses an adaption of the Reingold-Tilford algorithm to calculate the positions of the features in a
    feature model. It guarantees a planar drawing which is leveled and the parent is centered above its children.
    An adaption had to be made to account for the different lengths of feature names.
    """

    def __init__(self, G: nx.DiGraph, root: str) -> None:
        self.G = G
        self.root = root
        self.pos = nx.random_layout(G)
        self.mod = {node: 0 for node in G.nodes}
        self.scale_text = 1
        self.bfs = list(nx.bfs_layers(G=self.G,sources=self.root))
        self.contours = {}

    def _get_children(self, node: str) -> Tuple[bool, List[str]]:
        child =list(self.G.successors(node))
        has_child = len(child) > 0
        return has_child, child

    def _get_parent(self, node: str) -> Tuple[bool, List[str]]:
        parent = list(self.G.predecessors(node))
        has_parent = len(parent) > 0
        return has_parent, parent


    def set_initial_pos(self) -> None:
        """
        Sets the initial positions of the features in the feature model.
        """

        for y in range(len(self.bfs)):
            for i in range(len(self.bfs[y])):
                name = self.bfs[y][i]
                self.pos[name][1] = -y


    def _right_contour(self, node: str) -> List[float]:
        """
        Calculate the right contour of a node. The right contour is the right boundary of the subtree rooted at the node.
        :param node: The node for which the right contour should be calculated
        """

        bfs = list(nx.bfs_layers(self.G, sources=node))
        right_contour = []
        for level in bfs:
            x = self.pos[level[-1]][0] + self.scale_text * len(level[-1])
            right_contour.append(x)
        return right_contour
    
    def _left_contour(self, node: str) -> List[float]:
        """
        Calculate the left contour of a node. The left contour is the left boundary of the subtree rooted at the node.
        :param node: The node for which the left contour should be calculated
        """

        bfs = list(nx.bfs_layers(self.G, sources=node))
        left_contour = []
        for level in bfs:
            x = self.pos[level[0]][0] - self.scale_text * len(level[0])
            left_contour.append(x)
        return left_contour

    def compute_shift(self, node: str) -> Tuple[List[int], List[int]]:
        """
        The shifts are calculated recursively from bottom to top. For each subtree, a contour is calculated that
        describes the left and right boundary of the subtree. These subtrees are then placed as close to each other as
        possible without overlapping. The parent is placed in the middle of the children and the shifts of the children
        are calculated relative to the parent.
        :param node: The node for which the shift should be calculated
        """

        left_contour, right_contour = [- self.scale_text * len(node)], [self.scale_text * len(node)]
        has_child, children = self._get_children(node)
        if not has_child:
            return left_contour, right_contour
        else:
            children_contours = {}
            for child in children:
                children_contours[child] = self.compute_shift(child)

            d = [0 for _ in range(len(children))]
            current_right_contour = children_contours[children[0]][1]
            current_left_contour = children_contours[children[0]][0]
            
            for i in range(1, len(children)):
                sum_left = 0
                sum_right = 0
                next_left_contour = children_contours[children[i]][0]

                for j in range(0, min(len(current_right_contour), len(next_left_contour))):
                    sum_left += next_left_contour[j]
                    sum_right += current_right_contour[j]
                    d[i] = max(d[i], sum_right - sum_left)
                d[i] += 20

                new_right_contour = children_contours[children[i]][1]
                current_height_right = len(new_right_contour) 

                if len(current_right_contour) > current_height_right:
                    # old contour still visible
                    new_right_contour.append(
                        -sum(new_right_contour) - d[i] + sum(current_right_contour[0:current_height_right + 1]))
                    new_right_contour.extend(
                        current_right_contour[current_height_right + 1:len(current_right_contour)])
                current_right_contour = new_right_contour

                current_height_left = len(current_left_contour)
                if (len(next_left_contour)) > current_height_left:
                    # new contour visible
                    current_left_contour.append(
                        -sum(current_left_contour) + d[i] + sum(next_left_contour[0:current_height_left + 1]))
                    current_left_contour.extend(next_left_contour[current_height_left + 1:len(next_left_contour)])

            total_distance = sum(d)
            accumulated_distance = 0
            for i in range(len(children)):
                accumulated_distance += d[i]
                self.mod[children[i]] = accumulated_distance - total_distance / 2

            left_contour.append(self.mod[children[0]] + children_contours[children[0]][0][0] + self.scale_text * len(node))
            left_contour.extend(current_left_contour[1:])

            right_contour.append(self.mod[children[-1]] + children_contours[children[-1]][1][0] - self.scale_text * len(node))
            right_contour.extend(current_right_contour[1:])

            return left_contour, right_contour
        
    def _draw_edges(self, ax, height) -> None:
        """
        Draws the edges between the features in the feature model. 
        :param ax: The axes object of the plot
        :param height: The height of the rectangles
        """

        for edge in self.G.edges():
            start_pos = (self.pos[edge[0]][0], self.pos[edge[0]][1] - height / 2)
            end_pos = (self.pos[edge[1]][0], self.pos[edge[1]][1] + height / 2)
            ax.plot([start_pos[0], end_pos[0]], [start_pos[1], end_pos[1]], color='black', linewidth=1.5, zorder=1)
        
    def _draw_rectangles(self, ax, height, width_scale) -> None:
        """
        Draws the rectangles for the features in the feature model. The rectangles are centered around the x position of the feature.
        :param ax: The axes object of the plot
        :param height: The height of the rectangles
        :param width_scale: The scaling factor for the width of the rectangles
        """

        for node in self.G.nodes:
            x, y = self.pos[node]
            width = len(str(node)) * width_scale
            ax.add_patch(plt.Rectangle((x - width / 2, y - height / 2), width, height, edgecolor='black', facecolor='white'))
            # x, y is the lower left corner -> must be width/2 and height/2
            ax.text(x, y, node, horizontalalignment='center', verticalalignment='center', fontsize=10)

            _, children = self._get_children(node)
            if len(children) > 1:
                child1 = children[0]
                child2 = children[-1]
                x1 = self.pos[child1][0]
                x2 = self.pos[child2][0]
                new_y = self.pos[child1][1] + height / 2
                angle1 = np.degrees(np.arctan2(new_y - (y - height / 2), (x1 - self.pos[node][0]))) % 360
                angle2 = np.degrees(np.arctan2(new_y - (y - height / 2), (x2 - self.pos[node][0]))) % 360
                ax.add_patch(patches.Wedge((x, y - height/2), 1.5 * height, angle1, angle2, edgecolor='black', facecolor='white', fill=True ,zorder=2))

    def _add_cardinality(self, ax, height, cfm: CFM) -> None:
        """
        Adds the group instance cardinality, group type cardinality and instance cardinality to the plot of the cfm model.
        :param ax: The axes object of the plot
        :param height: How high/low the cardinalities should be displayed above/under the features and edges
        :param cfm: The cfm model that should be displayed
        """

        for node in cfm.features:
            x, y = self.pos[node.name]
            children = node.children
            if len(children) > 0:
                child = children[-1].name
                mid_pos = ((x + self.pos[child][0]) / 2, (y + self.pos[child][1]) / 2)
                group_instance_cardinality = self._cardinality_to_display_str(node.group_instance_cardinality, '⟨', '⟩')
                ax.text(mid_pos[0] + 0.3 * height, mid_pos[1] + height, group_instance_cardinality, horizontalalignment='center', verticalalignment='center', fontsize=10, color='black')
            if len(children) > 1:
                group_type_cardinality = self._cardinality_to_display_str(node.group_type_cardinality, '[', ']')
                ax.text(x, y - 2.5 * height / 2, group_type_cardinality, horizontalalignment='center', verticalalignment='center', fontsize=10)

            instance_cardinality = self._cardinality_to_display_str(node.instance_cardinality, '⟨', '⟩')
            shift = height if self.mod[node.name] > 0 else -height
            ax.text(x + 0.5 * shift, y + 1.5 * height / 2, instance_cardinality, horizontalalignment='center', verticalalignment='center', fontsize=10)


    def compute_x(self, node: str) -> None:
        """
        Computes recursively the x position of the node. The x position is calculated by adding the mod value of the node and the parents x position to the x value
        :param node: The node for which the x position should be calculated
        """

        _, parent = self._get_parent(node)
        if node == self.root:
            self.pos[node][0] = 0
        else:
            self.pos[node][0] = self.pos[parent[0]][0] + self.mod[node]
        has_child, children = self._get_children(node)
        if has_child:
            for child in children:
                self.compute_x(child)

    def _set_final_y(self, scale: float) -> None:
        """
        Because of the different ratios of the x and y positions, the y positions have to be scaled to get a better visualization.
        :param scale: The scale factor for the y positions
        """
        
        for node in self.G.nodes:
            self.pos[node][1] *= scale

    def _get_width(self) -> float:
        """
        helper function to get the width of the tree for the scaling
        """

        min = 0
        max = 0
        for level in self.bfs:
            left_pos = self.pos[level[0]][0]
            right_pos = self.pos[level[-1]][0]
            if left_pos < min:
                min = left_pos
            if right_pos > max:
                max = right_pos
        width = max - min
        return width
    
    def _cardinality_to_display_str(self, cardinality: Cardinality, left_bracket: str, right_bracket: str) -> str:
        """
        Converts a cardinality to a string representation that is displayed in the editor.
        :param cardinality: The cardinality to display
        :param left_bracket: The left symbol to use for the intervals
        :param right_bracket: The right symbol to use for the intervals
        :return: The string representation of the cardinality using the specified brackets
        """

        intervals = cardinality.intervals
        if not intervals:
            return f"{left_bracket}{right_bracket}"

        return ", ".join(
            f"{left_bracket}{interval.lower}, {'*' if interval.upper is None else interval.upper}{right_bracket}"
            for interval in intervals
        )

    def display_graph(self, format: str, cfm: CFM, height=20, width=10) -> bytes:
        """
        Plots the entire feature model and saves the model in the desired format.
        :param format: The format in which the image should be saved
        :param cfm: The feature model that should be displayed
        :param height: The height of the image
        :param width: The width of the image
        """

        tree_width = self._get_width()
        scale = tree_width / (2 * len(self.bfs))
        self._set_final_y(scale)
        _, ax = plt.subplots(figsize=(height, width))
        h = scale / 5
        s = scale / 17
        self._draw_edges(ax, h)
        self._draw_rectangles(ax, h, s)
        self._add_cardinality(ax, h, cfm)

        x_values = [self.pos[node][0] for node in self.G.nodes]
        y_values = [self.pos[node][1] for node in self.G.nodes]
        ax.set_xlim(1.2 * min(x_values) - 5, 1.2 * max(x_values) + 5)
        ax.set_ylim(1.2 * min(y_values) - 5, abs(0.2 * min(y_values)) + 5)
        ax.set_aspect('equal')
        plt.axis('off')
        buffer = BytesIO()
        plt.savefig(buffer, format=format, bbox_inches='tight')
        buffer.seek(0)
        plt.close()
        return buffer.getvalue()