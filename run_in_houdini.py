# -*- coding:utf-8 -*-
#!/usr/bin/env python
from imp import reload

import os
from functools import partial
from datetime import datetime
from collections import  OrderedDict
import time
import hou

from hip_file_diff_tool.ui import hda_diff_window
reload(hda_diff_window)

from PySide2.QtCore import  Qt
from PySide2.QtWidgets import  QListWidgetItem


def run():
    
    if "compare_win" not in globals():
        global compare_win
        compare_win = None
    
    try:
        compare_win.deleteLater()
        compare_win = None
    except:
        compare_win = None
    def  compare(_win,path_a,path_b,label_a = None,label_b = None):
        if not label_a:
            label_a = path_a
        if not label_b:
            label_b = path_b
        _win.source_file_line_edit.setText(label_a)
        _win.target_file_line_edit.setText(label_b)
        _win.source_file_line_edit.setRealPath(path_a)
        _win.target_file_line_edit.setRealPath(path_b)
        _win.handle_compare_button_click()
        _win.show()

    compare_win = hda_diff_window.HdaDiffWindow(None)
    compare_win.keep_curret_scene = True
    compare_win.setParent(hou.qt.mainWindow(), Qt.Window)
    file_dir = os.path.dirname(__file__)
    compare(compare_win,file_dir+"/test/hda/T2_MapReviewer1.hda",file_dir+"/test/hda/T2_MapReviewer1xx.hda")
    compare_win.show()


def exect_in_houdini():
    #拷贝一下代码 直接在houdini 中运行
    from imp import reload
    import sys
    if "F:/UGit" not in sys.path:
        sys.path.append("F:/UGit")
    #import hip_file_diff_tool
    #reload(hip_file_diff_tool)
    from hip_file_diff_tool import run_in_houdini
    reload(run_in_houdini)
    run_in_houdini.run()

if __name__ == '__main__':
    run()
