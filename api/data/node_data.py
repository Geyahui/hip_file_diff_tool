from dataclasses import dataclass, field
from typing import Any
from api.data.item_data import ItemData
from enum import auto, Enum
import hou
class NodeType(Enum):

    NONE = auto()
    HDANODE = auto()
    HDALOCKED = auto()
    Network = auto()
    NORMAL = auto()
    OTHERS = auto()
    def __str__(self):
        return f"{self.name.lower()}"

    def __format__(self, spec):
        return f"{self.name.lower()}"

@dataclass
class NodeData(ItemData):
    """
    A class to represent some of the Houdini node data.
    """

    def __init__(self, node):
        """
        Initialize a new instance of the NodeData class.

        :param name: The name of the node.
        """
        name = ""
        node_type = NodeType.NONE
        if node:
            name = node.name()
            node_type = NodeType.NORMAL
            if isinstance(node,hou.OpNode):
                if node.type().definition():
                    node_type = NodeType.HDANODE
                    if  node.isLockedHDA():
                        node_type = NodeType.HDALOCKED
                #elif node.type().name == "subnet":
                elif  node.isNetwork():
                    node_type = NodeType.Network
            else:
                node_type = NodeType.OTHERS
        self.node_type = node_type
        self.isBypassed = False
        self.is_root = False
        if node and hasattr(node,"isBypassed"):
            self.isBypassed = node.isBypassed()
        if self.isBypassed:
            name = name+"(isBypassed)"
        super().__init__(name)

        

    def add_parm(self, name: str, param: Any) -> None:
        """
        Add a parameter to the node's parameter dictionary.

        :param name: The name of the parameter.
        :param param: The parameter data to be added.
        """
        self.parms[name] = param

    def get_parm_by_name(self, name: str) -> Any:
        """
        Retrieve a parameter by its name from the node's parameter dictionary.

        :param name: The name of the parameter to be retrieved.
        :return: The parameter data associated with the provided name.
        :raises ValueError: If the parameter name is not found
                            in the dictionary.
        """
        if name not in self.parms:
            raise ValueError(
                f"Parameter '{name}' is not found in the dictionary."
            )

        return self.parms[name]

    def __repr__(self):
        return f"{self.name}: {self.state}\n"
