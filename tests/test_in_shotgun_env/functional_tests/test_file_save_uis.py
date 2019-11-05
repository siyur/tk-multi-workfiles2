"""
Copyright (c) Magnopus, LLC. All Rights Reserved.
"""
import sys
import time
import unittest

import sgtk
import tank_vendor
# from maya import cmds
# from sgtk.platform.qt import QtCore, QtGu
from mock import MagicMock
from PySide import QtCore, QtTest
from tests.test_in_shotgun_env.workfiles_app_test_base import WorkApiTestBase


class TestFileSaveUIs(WorkApiTestBase):

    def setUp(self):
        super(TestFileSaveUIs, self).setUp()
        self.mockgun.create("Asset", {"code": "test_name"
                                    })
        self.FileSavedialog = self._open_file_save_dialog()
        self.test_file_save_form = self.FileSavedialog._widget

    def _open_file_save_dialog(self):
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

    def test_file_save_exists(self):
        """
        test whether the file save UI exists after executing engine command
        """
        self.assertIsNotNone(self.FileSavedialog)

    def test_file_save_cancel(self):
        """
        test whether if can close the app by click cancel button
        """
        cancel_button = self.test_file_save_form._ui.cancel_btn
        cancel_button.clicked.emit()
        self.assertFalse(self.test_file_save_form.isVisible())

    def test_click_save(self):
        """
        test whether save button is enabled
        test whether save button will save current mock data to the temp path
        """
        #  todo: result_poller.ShundownHint's QtCore.QMetaObject.invokeMethod(self, "_do_invoke", QtCore.Qt.BlockingQueuedConnection was executed but it is unable to invoke the "_do_invoke" method
        # we have tried to use QtCore.Qt.QueuedConnection or QtCore.Qt.DirectConnection, they can invoke the method, but the emit method in "_do_invoke" is not received
        # the _task_resolve_sandbox_users is always pending and never get through, because it is waiting for the upstream task "_task_construct_work_area" to complete, which never did
        save_button = self.test_file_save_form._ui.save_btn
        self.assertTrue(save_button.isEnabled()) # the save button should be enabled if the file data are valid

    def test_click_save_with_empty_context_should_save_button_be_deactivated(self):
        """
        test whether save button is enabled
        test whether save button will save current mock data to the temp path
        """
        self.tk.context_empty()

        save_button = self.test_file_save_form._ui.save_btn
        self.assertFalse(save_button.isEnabled())

    def close_all_workfiles_app_dialogs(self):
        """
        Closes all open publish dialogs.
        This is needed for cleanup after the test is run.
        """
        current_engine = sgtk.platform.current_engine()
        for dialog in current_engine.created_qt_dialogs:
            dialog.close()

    def tearDown(self):
        self.close_all_workfiles_app_dialogs()
        super(TestFileSaveUIs, self).tearDown()


if __name__ == '__main__':
    unittest.main(verbosity=2)