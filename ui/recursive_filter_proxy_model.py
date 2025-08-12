from typing import Optional, Set

from hutil.Qt.QtCore import Qt,QSortFilterProxyModel, QModelIndex
from hutil.Qt.QtGui import QStandardItem

from hip_file_diff_tool.ui.constants import DATA_ROLE, PATH_ROLE
from hip_file_diff_tool.api.data.item_data import ItemState
from hip_file_diff_tool.api.data.node_data import NodeData,NodeType
from hip_file_diff_tool.api.data.param_data import ParamData

class RecursiveFilterProxyModel(QSortFilterProxyModel):
    """
    Subclass of QSortFilterProxyModel that enables recursive filtering.
    Provides custom behaviors like path-specific filtering.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.path_role = PATH_ROLE
        self.data_role = DATA_ROLE
        self._filtered_paths: Set[str] = set()

    def filterAcceptsRow(
        self, source_row: int, source_parent: QModelIndex
    ) -> bool:
        """Check if a row in the source model should be included in the proxy model."""
        source_index = self.sourceModel().index(source_row, 0, source_parent)
        item_path = self.sourceModel().data(source_index, self.path_role)
        
        # If there's an active filter for paths and the item's path isn't in it, reject this row.
        if self._filtered_paths and item_path not in self._filtered_paths:
            # return True
            return False

        # If source model has a condition to show only edited items
        if (
            hasattr(self.sourceModel(), "show_only_edited")
            and self.sourceModel().show_only_edited
        ):

            if not self.conditionForItem(source_index,source_parent):
                # return True
                return False

        # Check if the current row matches the filter itself
        if self.filter_accepts_row_itself(source_row, source_parent):
            return True

        # Recursively check child items
        for i in range(self.sourceModel().rowCount(source_index)):
            if self.filterAcceptsRow(i, source_index):
                return True
            
        # make sure that value is shown if parent fits condition
        state_value = self.sourceModel().data(source_index, self.data_role).state
        if state_value == ItemState.VALUE and source_parent.isValid():
            if self.filter_accepts_row_itself(source_parent.row(), source_parent.parent()):
                return True

        return False

    def conditionForItem(self, index: QModelIndex,parent_index:QModelIndex) -> bool:
        """
        Check the condition for a given item.

        :param index: QModelIndex representing the item.
        :return: True if the item matches the condition, False otherwise.
        """
        # data = self.sourceModel().data(index, self.data_role)
        data = index.data(self.data_role)
        parent_data = parent_index.data(self.data_role)
        state_value = data.state
        # 参数值类型 始终运行显示
        if state_value ==  ItemState.VALUE:  
            return True
        # 非subnet 类型的节点 Unchange 不显示(不再判子项)
        if isinstance(index.data(self.data_role),NodeData) :
            # if "transform_add" in index.data(self.path_role):
            # if "geo1" in index.data(Qt.DisplayRole):
            #     print(11111111111)
            #     print(index.data(self.data_role).state)
            #     print(index.data(self.data_role).node_type)
            #     print(index.data(self.path_role))
            #     print(index.model().view)
            if index.data(self.data_role).node_type == NodeType.NORMAL:
                if state_value  in [ItemState.UNCHANGED]:
                    return False

        # 参数类型，Create 或者 Delete 时，考虑父项是否为Edited ，如果父项 也是 Create 或者 Delete，则不显示
        if isinstance(index.data(self.data_role),ParamData) :
            if state_value == ItemState.UNCHANGED:
                return False
            else:
                if parent_data.state != ItemState.EDITED:
                    return False
                return True
                
        if state_value not in [ItemState.UNCHANGED]:
            return True

        for i in range(self.sourceModel().rowCount(index)):
            child_index = self.sourceModel().index(i, 0, index)
            if self.conditionForItem(child_index,index):
                return True

        return False

    def filter_accepts_row_itself(
        self, source_row: int, source_parent: QModelIndex
    ) -> bool:
        """Check if the source row itself meets the filter criteria."""
        return super().filterAcceptsRow(source_row, source_parent)

    def itemFromIndex(self, proxy_index: QModelIndex) -> QStandardItem:
        """Retrieve the item from the source model corresponding to the given proxy index."""
        source_index = self.mapToSource(proxy_index)
        return self.sourceModel().itemFromIndex(source_index)

    def indexFromItem(self, item: QStandardItem) -> QModelIndex:
        """Retrieve the proxy model index corresponding to the given QStandardItem."""
        source_index = self.sourceModel().indexFromItem(item)
        return self.mapFromSource(source_index)

    def get_item_by_path(self, path: str) -> Optional[QStandardItem]:
        """
        Retrieve an item by its unique path.

        :param path: Unique path identifier for the item.
        :return: QStandardItem if found, otherwise None.
        """
        item_dictionary = getattr(self.sourceModel(), "item_dictionary", None)
        return item_dictionary.get(path) if item_dictionary else None

    def set_filtered_paths(self, paths: Set[str]) -> None:
        """
        Define a set of paths to filter by.

        :param paths: Set of paths to be used for filtering.
        """
        self._filtered_paths = paths
        self.invalidateFilter()

    def reset_proxy_view(self) -> None:
        """Reset the view by clearing filters and sorting."""
        self.set_filtered_paths(set())  # Clear the paths filter
        self.setFilterFixedString("")
        self.sort(-1)
        self.invalidateFilter()
