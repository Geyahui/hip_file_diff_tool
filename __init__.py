from imp import reload
import sys

from . import api as hdf_api
from . import ui as hdf_ui
reload(hdf_api)
reload(hdf_ui)
sys.modules["hdf_api"] = hdf_api
sys.modules["hdf_ui"] = hdf_ui