# Copyright (c) 2018 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import os
import sgtk
import sgtk.platform.qt
import tank
from tank_test.tank_test_base import TankTestBase # noqa
from tank_test.tank_test_base import setUpModule
from mock_context import MockContext

# the following imports are needed to override the entire TankTestBase
import shutil
from tank_vendor.shotgun_api3.lib import mockgun
from tank.util.user_settings import UserSettings
from tank_vendor import yaml

class WorkApiTestBase(TankTestBase):
    """
    Baseclass for all Shotgun Utils unit tests.

    This sets up the fixtures, starts an engine and provides
    the following members:

    - self.framework_root: The path on disk to the framework bundle
    - self.engine: The test engine running
    - self.app: The test app running
    - self.framework: The shotgun utils fw running

    In your test classes, import module functionality like this::

        self.shotgun_model = self.framework.import_module("shotgun_model")

    """
    def setUp(self):
        """
        Fixtures setup
        """
        os.environ["WORKFILE2_TEST"] = "1"
        repo_root = os.path.normpath(
            os.path.join(
                os.path.dirname(__file__),
                "..", ".."
            )
        )
        external_repo_root = os.path.normpath(
            os.path.join(
                os.path.dirname(__file__),
                "..", "..", "..", "..", ".."
            )
        )
        external_repo_root = os.path.join(external_repo_root, "git_repos_external", "shotgunsoftware", "tk-shell")

        os.environ["REPO_ROOT"] = repo_root
        os.environ["SHOTGUN_EXTERNAL_REPOS_ROOT"] = os.path.dirname(external_repo_root)

        setUpModule()
        super(WorkApiTestBase, self).setUp()

        self.setup_fixtures()

        # set up an environment variable that points to the root of the
        # framework so we can specify its location in the environment fixture
        self.framework_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        os.environ["APP_ROOT"] = self.framework_root

        # now make a context
        self.current_user = self.mockgun.create("HumanUser", {"login": "jane.doe"})
        step_entity = self.mockgun.create("Step", {"code": "Model",
                                                   "short_name": "mdl",
                                                   "sg_tank_name": "Model"
                                                   })
        custom_entity = self.mockgun.create("Asset", {})
        # see context._task_from_sg about how this context to going to be added
        # this entity will not contain HumanUser entity as a context
        task_entity = self.mockgun.create("Task", {"content": "High Resolution",
                                                   "step":  {"type": "Step", "id": step_entity["id"]},
                                                   "project": {"type": "Project", "id": self.project["id"]}, # use the project from tank_test_base
                                                   "entity": {"type": "Asset", "id": custom_entity["id"]}
                                                   })
        # add pipeline configuration
        self.add_to_sg_mock_db(self.project)
        self.add_to_sg_mock_db(self.current_user)
        self.add_to_sg_mock_db(step_entity)
        self.add_to_sg_mock_db(custom_entity)
        self.add_to_sg_mock_db(task_entity)

        data = {
            "tk":  self.tk,
            "project": self.project,
            "entity": task_entity.get("entity"),
            "step": step_entity,
            "task": task_entity,
            "user": self.current_user,
        }

        # todo: somehow context._task_from_sg() doesn't return the name of project and step
        """
        using context_from_entity(), the context dictionary is created by context._task_from_sg()
        however the context dictionary returned by context._task_from_sg() only contains  elements of "name", "id" and "type"
            >>> context = self.tk.context_from_entity(task_entity["type"], task_entity["id"])
        and this is not how the context is created when shotgun is launched. 
        Instead, the tk-engine and tk-multi-launchapp calls context.deserialize(context_str) to create context,
        it will call _from_dict(dict_data), which will take all values of entities in: "project", "entity", "user", "step", "task", "additional_entities", "source_entity"
        This is th efunction we use, because the entities we use contains many custom fields and they need to be included in the context.
        """
        # use overwritten method to create context
        context = MockContext._from_dict(data)

        # and start the engine
        if tank.platform.current_engine():
            tank.platform.current_engine().destroy()
        self.engine = sgtk.platform.start_engine("tk-shell", self.tk, context)
        self.app = self.engine.apps["tk-multi-workfiles2"]

        self.image_path = os.path.join(repo_root, "icon_256.png")
        self.dark_image_path = os.path.join(repo_root, "icon_256_dark.png")

        # Local import since the QtGui module is set only after engine startup.
        from sgtk.platform.qt import QtCore, QtGui

        self.QtGui = QtGui
        self.QtCore = QtCore

        # Instantiate the QApplication singleton if missing.
        if QtGui.QApplication.instance() is None:
            QtGui.QApplication([])

        self.image = QtGui.QPixmap(self.image_path)

    def tearDown(self):
        """
        Fixtures teardown
        """
        # engine is held as global, so must be destroyed.
        cur_engine = sgtk.platform.current_engine()
        if cur_engine:
            cur_engine.destroy()

        # important to call base class so it can clean up memory
        super(WorkApiTestBase, self).tearDown()
