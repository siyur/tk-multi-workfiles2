"""
Copyright (c) PyUnit. All Rights Reserved.

Source: http://pyunit.sourceforge.net/notes/reloading.html
"""

import __builtin__
import sys


class RollbackImporter:
    def __init__(self):
        "Creates an instance and installs as the global importer"
        self.previousModules = sys.modules.copy()
        self.realImport = __builtin__.__import__
        __builtin__.__import__ = self._import
        self.newModules = {}

    def _import(self, name, globals=None, locals=None, fromlist=[]):
        result = apply(self.realImport, (name, globals, locals, fromlist))
        self.newModules[name] = 1
        return result

    def uninstall(self):
        for modname in self.newModules.keys():
            if not self.previousModules.has_key(modname):
                # Force reload when modname next imported
                print('Removing module: {0}'.format(modname))
                del (sys.modules[modname])
        __builtin__.__import__ = self.realImport
        self.newModules = {}