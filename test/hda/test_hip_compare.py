import sys
import os
import argparse
import unittest

from hip_file_diff_tool.ui.hip_file_diff_window import HipFileDiffWindow

from hutil.Qt.QtWidgets import QApplication
from hutil.Qt.QtCore import Qt

class TestNodeData(unittest.TestCase):

    def test_initasdsasdon(self):

        args = None
        app = QApplication(sys.argv)
        window = HipFileDiffWindow(args)
        window.show()
        print(1111)
        print(sys.argv[0])
        file_dir = os.path.dirname(__file__)
        window.source_file_line_edit.setText(file_dir+"/aaa.hip")
        window.target_file_line_edit.setText(file_dir+"/bbb.hip")
        sys.exit(app.exec_())



if __name__ == '__main__':
    unittest.main()
