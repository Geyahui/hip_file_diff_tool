import hou
from api.comparators.houdini_base_comparator import HoudiniComparator


class HdaFileComparator(HoudiniComparator):
    """Comparator class for comparing two Houdini HIP files."""
    force_compare_top_node = False
    def get_hda_data(self, hip_path: str) -> dict:
        """
        Retrieve data from a given HIP file.

        :param hip_path: The path to the HIP file.
        :return: A dictionary containing data extracted from the HIP file.
        """
        if not hip_path:
            raise ValueError("No source file specified!")

        hda_node = self._load_hip_file(hip_path)

        hda_node.allowEditingOfContents(True)
        data_dict = {}

        root_path = hda_node.path()
        root_path_new = root_path
        if self.force_compare_top_node:
            root_path_new = hda_node.parent().path()+"/cus_top_node"
        data_dict[root_path_new] = self._extract_node_data(hda_node,root_path_new)
        for node in hda_node.allSubChildren():
            if node.isInsideLockedHDA():
                continue
            path = node.path()
            path  = path.replace(root_path,root_path_new)

            data_dict[path] = self._extract_node_data(node,path)

        return data_dict

    def _load_hip_file(self, hip_path: str) -> None:
        """Load a specified HIP file into Houdini."""
        hou.hipFile.clear()
        hda_definition  = hou.hda.definitionsInFile(hip_path)[0]

        if not hda_definition.isInstalled():
            hou.hda.installFile(hip_path)
        hda_definition.setIsPreferred(1)
        geoNode = hou.node('/obj').createNode('geo')
        # # Create the HDA instance
        new_hda_node = geoNode.createNode(hda_definition.nodeTypeName())
        return new_hda_node


    def compare(self) -> None:
        """Compare the source and target HIP files to identify differences."""
        self._validate_file_paths()

        self.source_nodes = self.get_hda_data(self.source_file)
        self.target_nodes = self.get_hda_data(self.target_file)

        self._handle_deleted_and_edited_nodes()
        self._handle_created_nodes()
        self._handle_created_params()
        self.source_data = self.source_nodes
        self.target_data = self.target_nodes

        self.is_compared = True
