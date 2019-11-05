"""
Copyright (c) Magnopus, LLC. All Rights Reserved.
"""

import unittest

import sgtk

# from maya import cmds
# from sgtk.platform.qt import QtCore, QtGui
import PySide
from PySide import QtTest
from tests.test_in_shotgun_env.workfiles_app_test_base import WorkApiTestBase


class TestFileSaveOpen(WorkApiTestBase):


    def open_file_save_dialog(self):
        """
        If we try to execute the command directly from the current engine,
        it will create a dialog of type TankQDialog, It stores an instance of type FileSaveForm
        we can access this FileSaveForm instance by calling dialog._widget
        we can now track or test the uis using the instances in FIleSaveForm class

        TankQDialog is the same as QtGui.QDialog
        """
        # the command can be found at the "app" section of the engines yml file in tk-cofig-magnopus
        self.engine.execute_command("File Save...", [])
        for dialog in self.engine.created_qt_dialogs:
            if dialog.windowTitle() == 'Shotgun: File Save':
                return dialog  # a TankQDialog widget created from a FileSaveForm widget
        return None


    def close_all_workfiles_app_dialogs(self):
        """
        Closes all open publish dialogs.

        This is needed for cleanup after the test is run.
        """
        self.test_file_save_form._bg_task_manager.stop_all_tasks()
        current_engine = sgtk.platform.current_engine()
        for dialog in current_engine.created_qt_dialogs:
            dialog.close()

    def tearDown(self):
        self.close_all_workfiles_app_dialogs()
        super(TestFileSaveOpen, self).tearDown()


if __name__ == '__main__':
    unittest.main(verbosity=2)