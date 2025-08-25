from imp import reload
import hou
from api.comparators import houdini_base_comparator
reload(houdini_base_comparator)
from api.comparators.houdini_base_comparator import HoudiniComparator

class HdaFileComparator(HoudiniComparator):
    """Comparator class for comparing two Houdini HIP files."""
    def __init__(self, source_file: str, target_file: str):
        super().__init__(source_file, target_file)
        self.force_compare_top_node = False
        self.keep_curret_scene = False
        self.current_definition = None
        self.tmp_definition = []
    def get_hda_data(self, hda_path: str) -> dict:
        """
        Retrieve data from a given HIP file.

        :param hda_path: The path to the HIP file.
        :return: A dictionary containing data extracted from the HIP file.
        """
        if not hda_path:
            raise ValueError("No source file specified!")
        if hda_path.startswith("[NODE]:"):
            hda_path = hda_path.lstrip("[NODE]:")
            hda_node = hou.node(hda_path)
        else:
            hda_node = self._load_hip_file(hda_path)

        hda_node.allowEditingOfContents(True)
        data_dict = {}

        root_path = hda_node.path()
        root_path_new = root_path
        if self.force_compare_top_node:
            #root_path_new = hda_node.parent().path()+"/cus_top_node"
            root_path_new = "/cus_top_node"
        data_dict[root_path_new] = self._extract_node_data(hda_node,root_path_new)
        for node in hda_node.allSubChildren():
            if node.isInsideLockedHDA():
                continue
            path = node.path()
            path  = path.replace(root_path,root_path_new)

            data_dict[path] = self._extract_node_data(node,path)

        return data_dict

    def _load_hip_file(self, hda_path: str) -> None:
        """Load a specified HIP file into Houdini."""
        if not self.keep_curret_scene:
            hou.hipFile.clear()
        hda_definition  = hou.hda.definitionsInFile(hda_path)[0]
        #nodetype = hda_definition.nodeType()  # 环境中没有同名定义会引起报错
        hda_category = hda_definition.nodeTypeCategory() 
        hda_name = hda_definition.nodeTypeName() 
        nodetype = hou.nodeType(hda_category ,hda_name)

        if  nodetype and isinstance(nodetype  ,hou.OpNodeType) :
            if not self.current_definition:
                self.current_definition = nodetype.definition()
            # for definition in nodetype.allInstalledDefinitions():
            #     if definition.isCurrent():
            #         current_def = definition
            #         break
        
        if not hda_definition.isInstalled():
            hou.hda.installFile(hda_path)

        self.tmp_definition.append(hda_definition)
        hda_definition.setIsPreferred(1)
        geoNode = hou.node('/obj/__compare_geo')
        if not geoNode:
            geoNode = hou.node('/obj').createNode('geo','__compare_geo')
        # # Create the HDA instance
        new_hda_node = geoNode.createNode(hda_definition.nodeTypeName())
        return new_hda_node

    def clear_compare_geo(self ):
        geoNode = hou.node('/obj/__compare_geo')
        if  geoNode:
            for child in geoNode.children():
                child.destroy()

    def compare(self) -> None:
        """Compare the source and target HIP files to identify differences."""
        self._validate_file_paths()
        self.clear_compare_geo()
        self.source_nodes = self.get_hda_data(self.source_file)
        self.target_nodes = self.get_hda_data(self.target_file)
        if self.keep_curret_scene:  # hou.hipFile.clear() 会清除非环境hda
            if self.current_definition:
                self.current_definition.setIsPreferred(1)
                for df in self.tmp_definition:
                    if df != self.current_definition:
                        hda_path = df.libraryFilePath()  
                        hou.hda.uninstallFile(hda_path)  #Embedded  也可以删除，除非当前有节点占用
                    
        self._handle_deleted_and_edited_nodes()
        self._handle_created_nodes()
        self._handle_created_params()
        self.source_data = self.source_nodes
        self.target_data = self.target_nodes

        self.is_compared = True

    def _check_file_path(self, path: str, file_type: str) -> None:
        if  path.startswith("[NODE]:"):
            hda_path = path.lstrip("[NODE]:")
            hda_node = hou.node(hda_path)
            if not hou.node(hda_path):
                raise RuntimeError(
                    f"Node Not found {hda_path} "
                )


        else:
            super()._check_file_path(path,file_type)
