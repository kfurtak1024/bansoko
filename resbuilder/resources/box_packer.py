"""Module exposing utility for packing "boxes" into given size."""
from collections import deque
from dataclasses import dataclass
from typing import Optional, List

from bansoko.graphics import Rect, Size
from resbuilder import ResourceError


class _Node:
    def __init__(self, rect: Rect) -> None:
        self.box_id: Optional[int] = None
        self.rect: Rect = rect
        self.right_child: Optional[_Node] = None
        self.bottom_child: Optional[_Node] = None

    def split(self, right: int, bottom: int) -> None:
        """Split node by creating bottom and right child.

        :param right: the offset for right node
        :param bottom: the offset for bottom node
        """
        if self.is_split:
            return

        self.bottom_child = _Node(Rect.from_coords(
            self.rect.x, self.rect.y + bottom,
            self.rect.w, self.rect.h - bottom))
        self.right_child = _Node(Rect.from_coords(
            self.rect.x + right, self.rect.y,
            self.rect.w - right, bottom))
        self.rect = Rect(self.rect.position, Size(right, bottom))

    @staticmethod
    def find_node_for_box(root_node: "_Node", box_size: Size) -> Optional["_Node"]:
        """Look for a node that will fit box with given size.

        :param root_node: root node to start searching from
        :param box_size: size of the box to find room for
        :return: Node that will fit given box size *OR* None if box cannot be fit anywhere
        """
        node_deque = deque([root_node])

        while node_deque:
            node = node_deque.popleft()
            if node.has_box and node.bottom_child and node.right_child:
                node_deque.appendleft(node.bottom_child)
                node_deque.appendleft(node.right_child)
            elif node.rect.size.can_fit(box_size):
                return node

        return None

    @property
    def has_box(self) -> bool:
        """Is node "occupied". Has the node already assigned box."""
        return self.box_id is not None

    @property
    def is_split(self) -> bool:
        """Is this node a split.

        Split node has both: right and bottom child.
        """
        return self.right_child is not None and self.bottom_child is not None


@dataclass(frozen=True)
class _Box:
    box_id: int
    size: Size


class BoxPacker:
    """Packer for packing boxes into a bigger box with given size."""
    def __init__(self) -> None:
        self.boxes: List[_Box] = []

    def add_box(self, box_size: Size) -> int:
        """Add box to collection of boxes that will be packed during pack() call.

        :param box_size: size of box to be added
        :return: id assigned to given box (look at pack())
        """
        box = _Box(len(self.boxes), box_size)
        self.boxes.append(box)
        return box.box_id

    def pack(self, rect: Rect) -> List[Rect]:
        """Pack all boxes that were added to box packer.

        :param rect: destination rect to pack boxes in
        :return: collection of positions for all packed boxes (coords for given box can be found by
                 using box's id assigned during add_box call)
        """
        if not self.boxes:
            return []

        uv_rects: List[Rect] = [Rect.from_coords(0, 0, 0, 0)] * len(self.boxes)
        sorted_boxes = sorted(self.boxes, key=lambda b: b.size.max_dimension, reverse=True)
        root_node = _Node(rect)

        for box in sorted_boxes:
            node = _Node.find_node_for_box(root_node, box.size)
            if node:
                node.split(box.size.width, box.size.height)
                node.box_id = box.box_id
                uv_rects[box.box_id] = node.rect
            else:
                raise ResourceError(
                    f"Unable to fit box with size ({box.size.width}x{box.size.height})")

        return uv_rects
