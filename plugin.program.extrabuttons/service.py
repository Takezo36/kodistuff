# -*- coding: utf-8 -*-
# GNU General Public License v2.0 (see COPYING or https://www.gnu.org/licenses/gpl-2.0.txt)


import sys
print("tttttttttttttttttttttttPythonPython version")
print (sys.version)
print("Version info.")
print (sys.version_info)
# Start the monitor
from resources.lib.Monitor import MyMonitor
MyMonitor().start()
