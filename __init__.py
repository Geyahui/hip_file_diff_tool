from imp import reload
import sys

from . import api 
from . import ui 
# reload(api)
# reload(ui)
print(1234)
sys.modules["api"] = api
sys.modules["ui"] = ui