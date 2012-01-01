#!/usr/bin/env python

"sets up one of the tnt components"

import os
import sys
sys.path.insert(0, '.') # Not sure why we need this

from distutils.core import setup
from src._project_info import PROJECT_INFO
from src._component_info import COMPONENT_INFO
from src._version import VERSION_INFO

MANIFEST_EXTRA = "MANIFEST.in.extra"


def main():
    cmdclasses = {}
    # 'test' is the parameter as it gets added to setup.py
    PROJECT_INFO.update(VERSION_INFO)

    setup(
          name = PROJECT_INFO["name"],
          description = PROJECT_INFO["description"],
          version = PROJECT_INFO["Revision"],
          packages = PROJECT_INFO["packages"],
          package_data = PROJECT_INFO.get("package_data", {}),
          package_dir = PROJECT_INFO["package_dir"],
          data_files = PROJECT_INFO.get("data_files"),
          author = PROJECT_INFO["author"],
          author_email = PROJECT_INFO["author_email"],
          long_description = PROJECT_INFO["long_description"],
          scripts = PROJECT_INFO.get("scripts"),
          provides = PROJECT_INFO["provides"],
          classifiers = PROJECT_INFO["classifiers"],
          url = 'http://192.168.33.200/secure/TaskBoard.jspa',
         )

if __name__ == "__main__":
    PROJECT_INFO.update(COMPONENT_INFO)
    if os.path.isfile(MANIFEST_EXTRA):
        append_manifest_data = open(MANIFEST_EXTRA).read()
        if append_manifest_data:
            open("MANIFEST.in", 'a').write(append_manifest_data)
    main()
