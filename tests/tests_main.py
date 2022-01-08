#!/usr/bin/env python3
"""
Title:        tests_main
Description:  Main tests file providing helper functions.
License:      Apache License 2.0
Usage:        Run from repo root.
              Linux Distros: sudo pip3 install pytest; pytest tests
              Termux: pip3 install pytest; pytest tests
"""

import os
import importlib
import sys


def setup_tcp_module():
    "setUp." # noqa
    tcp = import_path(os.path.dirname(os.path.realpath(__file__)) + "/../src/termux-create-package")
    tcp.set_root_logger_and_log_level(tcp.logging.DEBUG)
    return tcp


def import_path(path):
    "Import module source from path." # noqa

    module_name = os.path.basename(path).replace('-', '_')
    spec = importlib.util.spec_from_loader(
        module_name,
        importlib.machinery.SourceFileLoader(module_name, path)
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    sys.modules[module_name] = module
    return module
