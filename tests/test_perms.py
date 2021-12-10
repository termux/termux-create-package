#!/usr/bin/env python3
# pylint: disable=invalid-name,global-variable-undefined,global-statement
# pylint: disable=line-too-long,too-many-statements
"""
Title:           test_perms
Description:     Tests for permission functions.
License:         Apache License 2.0
"""

import unittest

import tests_main

TCP = None

# TCP = importlib.import_module("termux-create-package")


class TestPerms(unittest.TestCase):
    "Class to test for permission functions." # noqa

    def setUp(self):
        "setUp." # noqa

        global TCP
        TCP = tests_main.setup_tcp_module()


    def test_dh_and_android_fixperms_for_android(self):
        "Run dh_and_android_fixperms() tests for android." # noqa

        init_config_for_dh_and_android_fixperms_tests(TCP.TERMUX_INSTALLATION_PREFIX)

        TCP.log_debug_no_format(TCP.logger, "\n\n")
        TCP.logger.info("Running dh_and_android_fixperms_for_android")
        tests_list = get_tests_list()
        self.run_tests_dh_and_android_fixperms(tests_list)


    def test_dh_and_android_fixperms_for_linux_distro(self):
        "Run dh_and_android_fixperms() tests for linux distros." # noqa

        init_config_for_dh_and_android_fixperms_tests(TCP.LINUX_DISTRO_INSTALLATION_PREFIX)

        TCP.log_debug_no_format(TCP.logger, "\n\n")
        TCP.logger.info("Running test_dh_and_android_fixperms_for_linux_distro")
        tests_list = get_tests_list()
        self.run_tests_dh_and_android_fixperms(tests_list)


    def run_tests_dh_and_android_fixperms(self, tests_list):
        "Run dh_and_android_fixperms() tests." # noqa

        # TCP.logger.info(TCP.get_list_string(tests_list))

        for i, (label, file_path, file_type, perm_initial, perm_fixed_expected) in enumerate(tests_list):
            TCP.log_debug_no_format(TCP.logger, "\n\n")
            TCP.logger.info("Running test " + str(i + 1) + ": label: \"" + label + "\", \
path: \"" + file_path + "\", type: \"" + file_type + "\", \
perm_initial: \"" + perm_initial + "\", \
perm_fixed_expected: \"" + perm_fixed_expected + "\"")

            (return_value, perm_fixed_returned) = TCP.dh_and_android_fixperms(
                label, file_path, file_type, perm_initial)
            TCP.logger.info("perm_fixed_returned: \"" + str(perm_fixed_returned or "") + "\"")
            self.assertEqual(
                (return_value, perm_fixed_returned),
                (0, perm_fixed_expected))





def init_config_for_dh_and_android_fixperms_tests(installation_prefix):
    "Initialize package config for dh_and_android_fixperms() tests." # noqa

    TCP.CONFIG = TCP.PackageConfig()
    TCP.CONFIG.is_testing = True

    package_name = "test"
    TCP.CONFIG.set_package_name(package_name)

    package_architecture = "aarch64"
    TCP.CONFIG.set_package_architecture(package_architecture)

    package_version = "0.1.0"
    TCP.CONFIG.set_package_version(package_version)

    TCP.CONFIG.set_installation_prefix(installation_prefix)


def get_tests_list():
    "Get list of tests to run." # noqa

    tests = []

    installation_prefix = TCP.CONFIG.installation_prefix
    package_name = TCP.CONFIG.package_name

    tests.append(tuple(("share/doc", installation_prefix + "/share/doc", TCP.FileType.DIRECTORY, "7777", "700" if is_android_prefix() else "755")))
    tests.append(tuple(("share/doc/subdir", installation_prefix + "/share/doc/subdir", TCP.FileType.DIRECTORY, "7777", "700" if is_android_prefix() else "755")))
    tests.append(tuple(("share/doc/subfile", installation_prefix + "/share/doc/subfile", TCP.FileType.REGULAR, "7777", "600" if is_android_prefix() else "644")))
    tests.append(tuple(("share/doc/subsym", installation_prefix + "/share/doc/subsym", TCP.FileType.SYMLINK, "777", "777")))

    tests.append(tuple(("share/doc/subdir/examples", installation_prefix + "/share/doc/subdir/examples", TCP.FileType.DIRECTORY, "7777", "700" if is_android_prefix() else "755")))
    tests.append(tuple(("share/doc/subdir/examples/subdir", installation_prefix + "/share/doc/subdir/examples/subdir", TCP.FileType.DIRECTORY, "7777", "700" if is_android_prefix() else "755")))
    tests.append(tuple(("share/doc/subdir/examples/subfile", installation_prefix + "/share/doc/subdir/examples/subfile", TCP.FileType.REGULAR, "7777", "700" if is_android_prefix() else "755")))



    non_executable_files_dirs = ["share/man", "include", "share/applications", "share/lintian/overrides"]
    for files_dirs in non_executable_files_dirs:
        tests.append(tuple((files_dirs, installation_prefix + "/" + files_dirs, TCP.FileType.DIRECTORY, "7777", "700" if is_android_prefix() else "755")))
        tests.append(tuple((files_dirs + "/subdir", installation_prefix + "/" + files_dirs + "/subdir", TCP.FileType.DIRECTORY, "7777", "700" if is_android_prefix() else "755")))
        tests.append(tuple((files_dirs + "/subfile", installation_prefix + "/" + files_dirs + "/subfile", TCP.FileType.REGULAR, "7777", "600" if is_android_prefix() else "644")))


    if is_android_prefix():
        perl_dir = "lib/perl5/5.30"
    else:
        perl_dir = "lib/" + TCP.CONFIG.package_architecture + "/perl5/5.30"

    tests.append(tuple((perl_dir, installation_prefix + "/" + perl_dir, TCP.FileType.DIRECTORY, "7777", "700" if is_android_prefix() else "755")))
    tests.append(tuple((perl_dir + "/subdir", installation_prefix + "/" + perl_dir + "/subdir", TCP.FileType.DIRECTORY, "7777", "700" if is_android_prefix() else "755")))
    tests.append(tuple((perl_dir + "/subfile", installation_prefix + "/" + perl_dir + "/subfile", TCP.FileType.REGULAR, "7777", "700" if is_android_prefix() else "755")))
    tests.append(tuple((perl_dir + "/subdir.pm", installation_prefix + "/" + perl_dir + "/subdir.pm", TCP.FileType.DIRECTORY, "7777", "700" if is_android_prefix() else "755")))
    tests.append(tuple((perl_dir + "/subfile.pm", installation_prefix + "/" + perl_dir + "/subfile.pm", TCP.FileType.REGULAR, "7777", "600" if is_android_prefix() else "644")))
    tests.append(tuple((perl_dir + "/subfile.pm", installation_prefix + "/" + perl_dir + "/subfile.pm", TCP.FileType.REGULAR, "750", "600" if is_android_prefix() else "644")))  # "go=rX" will set 750 to 755
    tests.append(tuple((perl_dir + "/subfile.pm", installation_prefix + "/" + perl_dir + "/subfile.pm", TCP.FileType.REGULAR, "400", "600" if is_android_prefix() else "644")))  # "go=rX,u+rw" will set 400 to 644

    perl_dir = "share/perl5"
    tests.append(tuple((perl_dir, installation_prefix + "/" + perl_dir, TCP.FileType.DIRECTORY, "7777", "700" if is_android_prefix() else "755")))
    tests.append(tuple((perl_dir + "/subdir", installation_prefix + "/" + perl_dir + "/subdir", TCP.FileType.DIRECTORY, "7777", "700" if is_android_prefix() else "755")))
    tests.append(tuple((perl_dir + "/subfile", installation_prefix + "/" + perl_dir + "/subfile", TCP.FileType.REGULAR, "7777", "700" if is_android_prefix() else "755")))
    tests.append(tuple((perl_dir + "/subdir.pm", installation_prefix + "/" + perl_dir + "/subdir.pm", TCP.FileType.DIRECTORY, "7777", "700" if is_android_prefix() else "755")))
    tests.append(tuple((perl_dir + "/subfile.pm", installation_prefix + "/" + perl_dir + "/subfile.pm", TCP.FileType.REGULAR, "7777", "600" if is_android_prefix() else "644")))
    tests.append(tuple((perl_dir + "/subfile.pm", installation_prefix + "/" + perl_dir + "/subfile.pm", TCP.FileType.REGULAR, "750", "600" if is_android_prefix() else "644")))  # "go=rX" will set 750 to 755
    tests.append(tuple((perl_dir + "/subfile.pm", installation_prefix + "/" + perl_dir + "/subfile.pm", TCP.FileType.REGULAR, "400", "600" if is_android_prefix() else "644")))  # "go=rX,u+rw" will set 400 to 644



    mode_0644_extensions = [
        # Libraries and related files
        '.so.1', '.so', '.la', '.a',
        # Web application related files
        '.js', '.css', '.scss', '.sass',
        # Images
        '.jpeg', '.jpg', '.png', '.gif',
        # OCaml native-code shared objects
        '.cmxs',
        # Node bindings
        '.node'
    ]
    for extension in mode_0644_extensions:
        tests.append(tuple(("subdir" + extension, installation_prefix + "/subdir" + extension, TCP.FileType.DIRECTORY, "7777", "700" if is_android_prefix() else "755")))
        tests.append(tuple(("subfile" + extension, installation_prefix + "/subfile" + extension, TCP.FileType.REGULAR, "7777", "600" if is_android_prefix() else "644")))



    executable_files_dirs = [
        installation_prefix + "/bin",
        "/bin",
        installation_prefix + "/sbin",
        "/sbin",
        installation_prefix + "/games",
        "/etc/init.d"]
    for files_dirs in executable_files_dirs:
        tests.append(tuple((remove_prefix(installation_prefix, files_dirs), files_dirs, TCP.FileType.DIRECTORY, "7777", "700" if TCP.android_rules_apply_to_path(files_dirs + "/") else "755")))
        tests.append(tuple((remove_prefix(installation_prefix, files_dirs) + "/subdir", files_dirs + "/subdir", TCP.FileType.DIRECTORY, "7777", "700" if TCP.android_rules_apply_to_path(files_dirs + "/") else "755")))
        tests.append(tuple((remove_prefix(installation_prefix, files_dirs) + "/subfile", files_dirs + "/subfile", TCP.FileType.REGULAR, "7777", "700" if TCP.android_rules_apply_to_path(files_dirs + "/") else "755")))
        tests.append(tuple((remove_prefix(installation_prefix, files_dirs) + "/subfile", files_dirs + "/subfile", TCP.FileType.REGULAR, "400", "700" if TCP.android_rules_apply_to_path(files_dirs + "/") else "755")))



    extension = ".ali"
    tests.append(tuple(("lib/subdir" + extension, installation_prefix + "/lib/subdir" + extension, TCP.FileType.DIRECTORY, "7777", "700" if is_android_prefix() else "755")))
    tests.append(tuple(("lib/subfile" + extension, installation_prefix + "/lib/subfile" + extension, TCP.FileType.REGULAR, "7777", "500" if is_android_prefix() else "555")))



    node_files = ["cli.js", "bin.js"]
    for file in node_files:
        tests.append(tuple(("lib/nodejs/" + file, installation_prefix + "/lib/nodejs/" + file, TCP.FileType.DIRECTORY, "7777", "700" if is_android_prefix() else "755")))
        tests.append(tuple(("lib/nodejs/" + file, installation_prefix + "/lib/nodejs/" + file, TCP.FileType.REGULAR, "7777", "700" if is_android_prefix() else "755")))
        tests.append(tuple(("lib/nodejs/" + file, installation_prefix + "/lib/nodejs/" + file, TCP.FileType.REGULAR, "400", "700" if is_android_prefix() else "755")))



    tests.append(tuple(("share/bug/" + package_name, installation_prefix + "/share/bug/" + package_name, TCP.FileType.DIRECTORY, "7777", "700" if is_android_prefix() else "755")))
    tests.append(tuple(("share/bug/" + package_name, installation_prefix + "/share/bug/" + package_name, TCP.FileType.REGULAR, "7777", "700" if is_android_prefix() else "755")))
    tests.append(tuple(("share/bug/" + package_name + "/script", installation_prefix + "/share/bug/" + package_name + "/script", TCP.FileType.DIRECTORY, "7777", "700" if is_android_prefix() else "755")))
    tests.append(tuple(("share/bug/" + package_name + "/script", installation_prefix + "/share/bug/" + package_name + "/script", TCP.FileType.REGULAR, "7777", "700" if is_android_prefix() else "755")))
    tests.append(tuple(("share/bug/" + package_name + "/not_script", installation_prefix + "/share/bug/" + package_name + "/not_script", TCP.FileType.DIRECTORY, "7777", "700" if is_android_prefix() else "755")))
    tests.append(tuple(("share/bug/" + package_name + "/not_script", installation_prefix + "/share/bug/" + package_name + "/not_script", TCP.FileType.REGULAR, "7777", "600" if is_android_prefix() else "644")))



    tests.append(tuple(("/etc/sudoers.d/subdir", "/etc/sudoers.d/subdir", TCP.FileType.DIRECTORY, "7777", "755")))
    tests.append(tuple(("/etc/sudoers.d/subfile", "/etc/sudoers.d/subfile", TCP.FileType.REGULAR, "7777", "440")))



    return tests


def remove_prefix(installation_prefix, path):
    "Removes installation_prefix from start."

    return path.replace(installation_prefix + "/", "")


def is_android_prefix():
    "Returns true if installation_prefix starts with '/data/data/<app_package>/files/' \
    and ignore_android_specific_rules is not enabled."

    return TCP.android_rules_apply_to_path(TCP.CONFIG.installation_prefix + "/")


if __name__ == '__main__':
    unittest.main()
