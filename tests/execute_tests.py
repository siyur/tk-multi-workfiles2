"""
To execute the functional tests,
    - the python interpreter should set to the location of Python in Shotgun
    - the following projects:
      tk-core, tk-framework-shotgunutils, tk-framework-qtwidgets, tk-shell
      must live at the location: <workfile_repository_root>/../../shotgunsoftware/

"""

import os
import sys

# get the upper level of repository root
upper_repo_root = os.path.normpath(
            os.path.join(
                os.path.dirname(__file__),
                "..", ".."
            )
        )
# add additional paths
additional_sys_path = [
    os.path.normpath(os.path.join(upper_repo_root, 'tk-multi-workfiles2')),
    os.path.normpath(os.path.join(upper_repo_root, 'tk-multi-workfiles2', 'python', 'tk_multi_workfiles')),
    os.path.normpath(os.path.join(upper_repo_root, 'tk-multi-workfiles2', 'tests', 'python')),
    os.path.normpath(os.path.join(upper_repo_root, 'shotgunsoftware', 'tk-core', 'tests')),
    # the location and version of Pycharm may be different for each device
    r'C:\Program Files (x86)\JetBrains\PyCharm 2019.2\debug-eggs\pycharm-debug.egg'
]

for path in additional_sys_path:
    if path not in sys.path:
        sys.path.append(path)

# Check if debug mode is active.
gettrace = getattr(sys, 'gettrace', None)
if gettrace and gettrace():
    import pydevd
    pydevd.settrace('localhost', port=60059, suspend=False)

# The module 'run_tests' is imported from the tk-core Shotgun package.
import run_tests

tk_multi_workfiles2_tests = os.path.normpath(os.path.join(upper_repo_root, 'tk-multi-workfiles2', 'tests', 'test_in_shotgun_env'))
run_tests.main(["--test-root", tk_multi_workfiles2_tests])