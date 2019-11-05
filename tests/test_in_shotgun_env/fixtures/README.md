This config folder is here for setting up test configuration for functional test in shotgun environment

The pick_environment.py under "config/core/hook" is executed during each test setUp(),
it will decide whether to use asset.yml or test.yml for the configuration of the test engine and app

The file structure under "config/core/schema" should match the template structures in config/core/templates.yml

The set up of test engine and app are written in config/env/asset.yml

Unsolved problem:
    currently, the templates in info.yml of this project should contains a "fields" element if the corresponding
    template requires fields in templates.yml
    but this action is not a necessary for tk-config-magnopus. need further study about this case.


