import os
from tank.context import Context
from tank.errors import TankError, TankContextDeserializationError
from tank.template import TemplatePath

class MockContext(Context):
    """
    This class is created in an attempt to create a subclass of context that override some mrthods in the Context class for test purpose
    In workfiles_app_test_base, the engine for test will take an object of MockContext as context
    """

    @classmethod
    def _from_dict(cls, data):
        """
        Creates a Context object based on the arguments found in a dictionary, but
        only the ones that the Context understands.

        This ensures that if a more recent version of Toolkit serializes a context
        and this API reads it that it won't blow-up.

        :param dict data: Data for the context.

        :returns: :class:`Context`
        """
        # Get all argument names except for self.
        return MockContext(
            tk=data.get("tk"),
            project=data.get("project"),
            entity=data.get("entity"),
            step=data.get("step"),
            task=data.get("task"),
            user=data.get("user"),
            additional_entities=data.get("additional_entities"),
            source_entity=data.get("source_entity")
        )

    @property
    def entity_locations(self):
        """
        A list of paths on disk which correspond to the **entity** which this context represents.
        If no folders have been created for this context yet, the value of this property will be an empty list::
            ['/studio.08/demo_project/sequences/AAA/ABC']

        :returns: A list of paths
        """
        project_roots = self._get_project_roots()
        mock_path1 = os.path.join(os.path.normpath(project_roots[0]), "3D", "test_asset_type", "test_Asset", "test_name", "publish")
        mock_path2 = os.path.join(os.path.normpath(project_roots[0]), "3D", "test_asset_type", "test_Asset", "test_name")
        mock_path3 = os.path.join(os.path.normpath(project_roots[0]), "3D", "test_asset_type", "test_Asset")
        mock_path4 = os.path.join(os.path.normpath(project_roots[0]), "3D", "test_asset_type")
        mock_path5 = os.path.join(os.path.normpath(project_roots[0]), "3D")
        return [mock_path1, mock_path2, mock_path3, mock_path4, mock_path5]



    def as_template_fields(self, template, validate=False):
        """
        Override the as_template_field function in tank.context for testing purpose
        The only change here is that it skip the process to  get fields from entity:
            fields = self._fields_from_entity_paths(template)
        and replace it with a static fields dict for test:
            fields = {"Asset": "testing_asset", "sg_asset_type": "test_asset_type"}


        :param template:    :class:`Template` for which the fields will be used.
        :param validate:    If True then the fields found will be checked to ensure that all expected fields for
                            the context were found.  If a field is missing then a :class:`TankError` will be raised
        :returns:           A dictionary of template files representing the context. Handy to pass to for example
                            :meth:`Template.apply_fields`.
        :raises:            :class:`TankError` if the fields can't be resolved for some reason or if 'validate' is True
                            and any of the context fields for the template weren't found.
        """
        # Get all entities into a dictionary
        entities = {}

        if self.entity:
            entities[self.entity["type"]] = self.entity
        if self.step:
            entities["Step"] = self.step
        if self.task:
            entities["Task"] = self.task
        if self.user:
            entities["HumanUser"] = self.user
        if self.project:
            entities["Project"] = self.project

        # If there are any additional entities, use them as long as they don't
        # conflict with types we already have values for (Step, Task, Shot/Asset/etc)
        for add_entity in self.additional_entities:
            if add_entity["type"] not in entities:
                entities[add_entity["type"]] = add_entity

        fields = {}

        # Try to populate fields using paths caches for entity
        if isinstance(template, TemplatePath):

            # first, sanity check that we actually have a path cache entry
            # this relates to ticket 22541 where it is possible to create
            # a context object purely from Shotgun without having it in the path cache
            # (using tk.context_from_entity(Task, 1234) for example)
            #
            # Such a context can result in erronous lookups in the later commands
            # since these make the assumption that the path cache contains the information
            # that is being saught after.
            #
            # therefore, if the context object contains an entity object and this entity is
            # not represented in the path cache, raise an exception.
            if self.entity and len(self.entity_locations) == 0:
                # context has an entity associated but no path cache entries
                raise TankError("Cannot resolve template data for context '%s' - this context "
                                "does not have any associated folders created on disk yet and "
                                "therefore no template data can be extracted. Please run the folder "
                                "creation for %s and try again!" % (self, self.shotgun_url))

            # first look at which ENTITY paths are associated with this context object
            # and use these to extract the right fields for this template
            # fields = self._fields_from_entity_paths(template)
            fields = {"Asset": "testing_asset", "sg_asset_type": "test_asset_type"} # skip the process of checking template, use a generic asset entity

            # filter the list of fields to just those that don't have a 'None' value.
            # Note: A 'None' value for a field indicates an ambiguity and was set in the
            # _fields_from_entity_paths method (!)
            non_none_fields = dict([(key, value) for key, value in fields.iteritems() if value is not None])

            # Determine additional field values by walking down the template tree
            fields.update(self._fields_from_template_tree(template, non_none_fields, entities))
        # get values for shotgun query keys in template
        fields.update(self._fields_from_shotgun(template, entities, validate))

        if validate:
            # check that all context template fields were found and if not then raise a TankError
            missing_fields = []
            for key_name in template.keys.keys():
                if key_name in entities and key_name not in fields:
                    # we have a template key that should have been found but wasn't!
                    missing_fields.append(key_name)
            if missing_fields:
                raise TankError("Cannot resolve template fields for context '%s' - the following "
                                "keys could not be resolved: '%s'.  Please run the folder creation "
                                "for '%s' and try again!"
                                % (self, ", ".join(missing_fields), self.shotgun_url))
        return fields