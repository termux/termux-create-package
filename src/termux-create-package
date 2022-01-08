#!/usr/bin/env python3
# pylint: disable=invalid-name,global-variable-undefined,global-statement
# pylint: disable=logging-not-lazy,too-few-public-methods,broad-except,no-else-return,no-else-continue
# pylint: disable=line-too-long,too-many-lines,multiple-statements,too-many-branches,too-many-return-statements,too-many-arguments,too-many-locals,too-many-statements,too-many-nested-blocks
"""
Title:           termux-create-package
Description:     Utility to create binary deb packages
Usage:           Run "termux-create-package --help"
Date:            10-Dec-2021
Python version:  3 or higher
License:         Apache License 2.0
"""

import argparse
import collections
import fnmatch
# import grp
import hashlib
import io
import json
import logging
import math
import os
# import pwd
import re
import select
import shutil
import stat
import subprocess
import sys
import tarfile
import tempfile
import time
import traceback
import unicodedata

import importlib
yaml_supported = False
try:
    if importlib.util.find_spec("ruamel.yaml") is not None:
        import ruamel.yaml  # pylint: disable=import-error
        yaml_supported = True
except Exception:
    pass


VERSION = "0.12.0"

logger = None
LOG_LEVELS = [logging.CRITICAL, logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG]
DEFAULT_LOG_LEVEL = logging.WARNING
LOG_LEVEL = DEFAULT_LOG_LEVEL
NO_LOGGER_FORMAT = False
CUSTOM_LOGGER_FORMAT = ""

CONFIG = None

TERMUX_PREFIX = "/data/data/com.termux/files/usr"
TERMUX_INSTALLATION_PREFIX = TERMUX_PREFIX
LINUX_DISTRO_INSTALLATION_PREFIX = "/usr"
DEFAULT_INSTALLATION_PREFIX = TERMUX_INSTALLATION_PREFIX

PACKAGE_CONTROL_FILE_MANDATORY_STRING_FIELDS_LIST = [
    "Package", "Version", "Architecture", "Maintainer"
]

PACKAGE_CONTROL_FILE_BUILD_AND_INSTALL_FIELDS_LIST = [
    "Package", "Source", "Version", "Architecture", "Maintainer", "Installed-Size",
    "Section", "Priority", "Essential"
]

PACKAGE_CONTROL_FILE_RELATIONSHIP_FIELDS_LIST = [
    "Depends", "Pre-Depends", "Recommends", "Suggests",
    "Breaks", "Conflicts", "Replaces",
    "Enhances", "Provides"
]

PACKAGE_CONTROL_FILE_HOME_AND_DESCRIPTION_FIELDS_LIST = [
    "Homepage", "Description"
]

# Define a list of scripts that will be added to the control.tar if they exist
PACKAGE_MAINTAINER_SCRIPTS_LIST = [
    "preinst", "postinst", "prerm", "postrm", "config"
]

# Define a list of other files that will be added to the control.tar if they exist
PACKAGE_OTHER_CONTROL_FILES_LIST = [
    "conffiles", "templates", "shlibs"
]

# Define a list of supported package create info fields
PACKAGE_CREATE_INFO_FIELDS_LIST = [
    "control",
    "installation_prefix", "files_dir",
    "tar_compression", "tar_format",
    "deb_dir", "deb_name", "deb_architecture_tag",
    "control_files_dir", "maintainer_scripts_shebang",
    "conffiles_prefix_to_replace",
    "fix_perms",
    "allow_bad_user_names_and_ids", "ignore_android_specific_rules",
    "data_files"
]

PACKAGE_DATA_FILES_FIELD_ATTRIBUTES_LIST = [
    "source",
    "perm", "fix_perm",
    "source_ownership", "owner_uid", "owner_uname", "owner_gid", "owner_gname",
    "is_conffile"
]

PACKAGE_DATA_FILES_FIELD_ACTIONS_LIST = [
    "ignore", "ignore_if_no_exist",
    "source_readlink", "source_recurse",
    "set_parent_perm",
    "symlink_destinations",
    "set_shebang"
]

PACKAGE_DATA_FILES_ATTRIBUTES_AND_ACTIONS_LIST = []
PACKAGE_DATA_FILES_ATTRIBUTES_AND_ACTIONS_LIST.extend(PACKAGE_DATA_FILES_FIELD_ATTRIBUTES_LIST)
PACKAGE_DATA_FILES_ATTRIBUTES_AND_ACTIONS_LIST.extend(PACKAGE_DATA_FILES_FIELD_ACTIONS_LIST)


class PackageConfig:
    "Deb package config info." # noqa
    # pylint: disable=too-many-instance-attributes

    def __init__(self):
        self.is_testing = False

        self.old_manifest_format = False
        self.yaml_manifest_format = False

        self.manifest_file_path = None
        self.files_dir = None
        self.control_files_dir = None
        self.deb_dir = None
        self.deb_name = None

        self.package_name = None
        self.package_name_escaped = None

        self.package_architecture = None
        self.package_architecture_escaped = None

        self.package_version = None
        self.package_version_escaped = None

        self.installation_prefix = None
        self.installation_prefix_escaped = None

        self.md5sums_file_content = ""
        self.conffiles_file_content = ""

        self.installed_size = 0

        self.package_data_file_mtime = None
        self.package_data_file_perm = None
        self.package_data_file_uid = None
        self.package_data_file_uname = None
        self.package_data_file_gid = None
        self.package_data_file_gname = None

        self.package_control_info_file_mtime = None

        self.fix_perms = True
        self.ignore_android_specific_rules = False
        self.allow_bad_user_names_and_ids = False

        self.package_data_files_dict = collections.OrderedDict()

        self.package_temp_directory_paths_list = []
        self.package_temp_file_paths_list = []


    def set_package_name(self, package_name):
        "set package_name and package_name_escaped" # noqa

        self.package_name = package_name
        if self.package_name:
            self.package_name_escaped = re.escape(self.package_name)
        else:
            self.package_name_escaped = None


    def set_package_architecture(self, package_architecture):
        "set package_architecture and package_architecture_escaped" # noqa

        self.package_architecture = package_architecture
        if self.package_architecture:
            self.package_architecture_escaped = re.escape(self.package_architecture)
        else:
            self.package_architecture_escaped = None


    def set_package_version(self, package_version):
        "set package_version and package_version_escaped" # noqa

        self.package_version = package_version
        if self.package_version:
            self.package_version_escaped = re.escape(self.package_version)
        else:
            self.package_version_escaped = None


    def set_installation_prefix(self, installation_prefix):
        "set installation_prefix and installation_prefix_escaped" # noqa

        self.installation_prefix = installation_prefix
        if self.installation_prefix:
            self.installation_prefix_escaped = re.escape(self.installation_prefix)
        else:
            self.installation_prefix_escaped = None





class LoggerFormatter(logging.Formatter):
    "Logger format class" # noqa

    root_logger_format = "[%(levelname).1s] %(message)s"
    # root_logger_format = "[%(levelname).1s] %(funcName)s: %(message)s"

    named_logger_format = "[%(levelname).1s] %(name)s: %(message)s"
    # named_logger_format = "[%(levelname).1s] %(name)s: %(funcName)s: %(message)s"

    def format(self, record):
        # pylint: disable=protected-access

        if NO_LOGGER_FORMAT:
            self._style._fmt = "%(message)s"
        elif CUSTOM_LOGGER_FORMAT:
            self._style._fmt = CUSTOM_LOGGER_FORMAT
        elif record.name == "root":
            self._style._fmt = self.root_logger_format
        else:
            self._style._fmt = self.named_logger_format
        return super().format(record)


class LoggerLessThanFilter(logging.Filter):
    "Logger log level filtering class" # noqa

    def __init__(self, exclusive_maximum, name=""):
        super(LoggerLessThanFilter, self).__init__(name)
        self.max_level = exclusive_maximum

    def filter(self, record):
        # Non-zero return means the message will be logged
        return 1 if record.levelno < self.max_level else 0


def setup_logger(logger, logger_log_level=None, logger_log_formatter=None):
    "Setup the logger passed with optionally the log level and format passed." # noqa
    # pylint: disable=redefined-outer-name

    if logger_log_level is None or not isinstance(logger_log_level, int):
        if LOG_LEVEL is not None:
            logger_log_level = LOG_LEVEL
        else:
            logger_log_level = DEFAULT_LOG_LEVEL

    if logger_log_formatter is None:
        logger_log_formatter = LoggerFormatter()

    logger.setLevel(logger_log_level)

    # Redirect all messages to stdout
    # console_handler = logging.StreamHandler()
    # console_handler.setLevel(logger_log_level)
    # console_handler.setFormatter(logger_log_formatter)
    # logger.addHandler(console_handler)

    # Redirect INFO and DEEBUG messages to stdout
    console_handler_stdout = logging.StreamHandler(sys.stdout)
    console_handler_stdout.setLevel(logger_log_level)
    console_handler_stdout.addFilter(LoggerLessThanFilter(logging.WARNING))
    console_handler_stdout.setFormatter(logger_log_formatter)
    logger.addHandler(console_handler_stdout)

    # Redirect WARNING and above messages to stderr
    console_handler_stderr = logging.StreamHandler(sys.stderr)
    console_handler_stderr.setLevel(logging.WARNING)
    console_handler_stderr.setFormatter(logger_log_formatter)
    logger.addHandler(console_handler_stderr)


def set_root_logger_and_log_level(log_level):
    "Get the 'root' logger and set it to the global variable logger" # noqa

    global logger
    global LOG_LEVEL

    LOG_LEVEL = log_level
    logger = get_logger()


def get_logger(logger_name=None, logger_log_level=None, logger_log_formatter=None):
    "Returns the logger object for logger_name passed, returns 'root' logger by default." # noqa
    # pylint: disable=redefined-outer-name

    logger_name = "root" if not logger_name else str(logger_name)

    logger = logging.getLogger(logger_name)

    if not logger.handlers:
        setup_logger(logger, logger_log_level, logger_log_formatter)

    return logger


def log_debug_no_format(logger, message=""):
    "Log the message at 'DEBUG' level directly without any format." # noqa
    # pylint: disable=redefined-outer-name

    global NO_LOGGER_FORMAT

    NO_LOGGER_FORMAT = True
    logger.debug(message)
    NO_LOGGER_FORMAT = False





def get_list_string(list_value):
    "Get a string representation of a list." # noqa

    # If directly printed, python used repr() on each element, which
    # escapes backslashes like "\" with "\\", which would not be real
    # value of list items.

    if not list_value or not isinstance(list_value, list) or not list_value: return [] # noqa
    return "['%s']" % "', '".join(map(str, list_value))


def get_regex_or_pattern(list_value):
    "Get a regex OR pattern from a list of strings like '((str1)|(str2))'." # noqa

    if not list_value or not isinstance(list_value, list) or not list_value: return "" # noqa
    return "((%s))" % ")|(".join(map(re.escape, list_value))


def remove_escape_characters(string):
    "Remove 7-bit ansi escape sequence characters from string." # noqa

    # https://stackoverflow.com/a/38662876
    if string is None: return string # noqa
    return re.sub(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]', '', string)


def remove_control_characters(string):
    "Remove control sequence characters from string except '\n' and '\t'." # noqa

    # https://stackoverflow.com/a/19016117
    if string is None: return string # noqa
    return "".join(ch for ch in string if unicodedata.category(ch)[0] != "C" or ch in ["\n", "\t"])


def sanitize_dict(value, is_value=True):
    "Sanitize illegal characters in dictionary keys and values." # noqa
    # pylint: disable=unused-argument,invalid-name

    if isinstance(value, dict):
        new_value = collections.OrderedDict()
        for k, v in value.items():
            if isinstance(v, dict):
                new_value[sanitize_dict(k, False)] = collections.OrderedDict(sanitize_dict(v, True))
            else:
                new_value[sanitize_dict(k, False)] = sanitize_dict(v, True)
        value = new_value
    elif isinstance(value, list):
        value = [sanitize_dict(v, True) for v in value]
    elif isinstance(value, str):
        # If not is_value:
        # print("'" + repr(value) + "'")
        value = remove_escape_characters(value)
        value = remove_control_characters(value)
        # print("'" + repr(value) + "'")
    elif isinstance(value, (int, float)) and not isinstance(value, bool):
        # We must type cast all numbers to strings, otherwise
        # validation of fields like "perm", etc will fail.
        value = str(value)

    return value


def get_branches_of_path(path):
    "Get each branch of a path." # noqa

    # Input: "/dir1/dir2/dir3"
    # Output: ["/dir1", "/dir1/dir2", "/dir1/dir2/dir3"]
    # https://stackoverflow.com/a/34892362/14686958

    if not path or not isinstance(path, str): return [] # noqa
    path = re.sub("[/]+", "/", path)  # replace multiple "/" with single
    if path == "/": return ["/"] # noqa

    if path.endswith("/"): path = path.rstrip("/") # noqa

    # print("\npath: " + path)
    levels = path.split("/")
    branches = []
    for i in range(len(levels)):
        branch = "/".join(levels[:i + 1] + [""])
        if branch != "/" and branch.endswith("/"): branch = branch[:-1] # noqa
        # print("branch " + str(i) + ": " + str(branch))
        branches.extend([branch])

    # print("branches: " + str(branches) + "\n")
    return branches
    # return ["/".join(levels[:i + 1]) for i in range(len(levels))]


def get_unique_parent_paths_list(file_paths_list):
    "Get unique parent paths for all paths in the file_paths_list." # noqa

    # Input: ['/custom/dir', '/usr/share/man/man1/hello-world.1', '/usr/etc/hello-world/hello-world.config', '/usr/bin/hello-world.1', '/usr/bin/hello-world', '/usr/custom/dir/hello-world']
    # Output: ['/custom', '/usr/share/man/man1', '/usr/etc/hello-world', '/usr/bin', '/usr/custom/dir']

    if not file_paths_list or not isinstance(file_paths_list, list): return [] # noqa

    # Find all unique parent paths of paths in the file_paths_list
    # that do not have any parents themselves in the file_paths_list

    # Normalize all paths
    for i, file_path in enumerate(file_paths_list):
        file_paths_list[i] = normalize_path(file_path)

    # print("file_paths_list: " + str(file_paths_list) + "\n")

    # For all current_file_path in file_paths_list
    parent_paths_list = []
    for i, current_file_path in enumerate(file_paths_list):
        # Create a copy of file_paths_list and remove
        # current_file_path from it
        file_paths_list_copy = file_paths_list[:]
        file_paths_list_copy.pop(i)

        # Check if any file_path in file_paths_list_copy is
        # a parent of current_file_path
        has_parent = False
        for file_path in file_paths_list_copy:
            if current_file_path.startswith(file_path + "/"):
                has_parent = True
                break

        # If no parent found and current_file_path is set
        # add parent of current_file_path to
        # parent_paths_list
        if not has_parent and current_file_path:
            if current_file_path == "/":
                parent_paths_list.append("/")
            else:
                # Split, remove basename, then rejoin
                parent_path = "/".join(current_file_path.split("/")[:-1])
                if parent_path:
                    parent_paths_list.append(parent_path)
                else:
                    parent_paths_list.append("/")

    # Remove duplicates
    parent_paths_list = list(collections.OrderedDict.fromkeys(parent_paths_list))
    # print("parent_paths_list: " + str(parent_paths_list) + "\n")
    return parent_paths_list


def normalize_path(path):
    "Returns normalized path." # noqa

    # Normalize path first, then replace multiple "/" with single.
    # This is necessary since python does not remove "//" from the
    # start to maintain compatibility with windows
    return re.sub("[/]+", "/", os.path.normpath(str(path)))


# Based on make_symlink function called by dh_link
# https://github.com/Debian/debhelper/blob/debian/13.1/dh_link
# https://github.com/Debian/debhelper/blob/debian/13.1/lib/Debian/Debhelper/Dh_Lib.pm#L2276
# https://manpages.debian.org/testing/debhelper/dh_link.1.en.html
# https://www.debian.org/doc/debian-policy/ch-files.html#symbolic-links
def make_symlink(dest, src):
    "Creates a symlink from  dest -> src in the temp directory and returns the file path." # noqa
    # pylint: disable=invalid-name

    global CONFIG

    # If dest is not set or of type str
    if not dest or not isinstance(dest, str):
        logger.error("The dest passed to make_symlink function must be set and of type str")
        return (1, None)

    # If src is not set or of type str
    if not src or not isinstance(src, str):
        logger.error("The src passed to make_symlink function must be set and of type str")
        return (1, None)

    original_src = src

    try:
        # Normalize paths to remove "./"
        src = normalize_path(src)
        dest = normalize_path(dest)

        # Remove prefix "/"
        src = src.lstrip("/")
        dest = dest.lstrip("/")

        # If src equals dest
        if src == dest:
            logger.error("Cannot create a symlink to itself for src path \"" + original_src + "\"")
            return (1, None)

        # Policy says that if the link is all within one top level
        # directory, it should be relative. If it's between
        # top level directories, leave it absolute.

        # Split src and dest on "/"
        src_dirs = src.split("/")
        dest_dirs = dest.split("/")

        # If same top level directory
        if len(src_dirs) > 0 and src_dirs[0] == dest_dirs[0]:
            # Figure out how much of a path src and dest share in common

            # Increment x until src_dir and dest_dir are different
            for x in range(len(src_dirs)):  # pylint: disable=consider-using-enumerate
                if src_dirs[x] != dest_dirs[x]:
                    break

            # Build up the new src
            src = ""

            # For 1 to (dest_dir_size -x), append "../" to src to go to parent directory
            for i in range(1, len(dest_dirs) - x):
                src += "../"

            # For x to src_dir_size, append "src_dirs[i]/" to src
            for i in range(x, len(src_dirs)):
                src += src_dirs[i] + "/"

            # If x > src_dir_size and src is empty, set it to "."
            if x > len(src_dirs) and not src:
                # Special case
                src = "."

            # Remove suffix "/"
            src = src.rstrip("/")

        else:
            # Make sure src is an absolute path
            if not src.startswith("/"):
                src = "/" + src

        dest = "/" + dest
        symlink_temp_directory_path = tempfile.mkdtemp()
        CONFIG.package_temp_directory_paths_list.append(symlink_temp_directory_path)
        symlink_path = symlink_temp_directory_path + "/" + os.path.basename(dest)

        # Create symlink from dest -> src at symlink_path
        logger.debug("creating symlink from \"" + dest + "\" -> \"" + src + "\" at \"" + symlink_path + "\"")

        os.symlink(src, symlink_path)

        # If src path symlink does not exist at symlink_path as expected
        if not os.path.islink(symlink_path):
            logger.error("Failed to find symlink from \"" + dest + "\" -> \"" + src + "\" at \"" + symlink_path + "\"")
            return (1, None)

        symlink_target = os.readlink(symlink_path)
        # If symlink created is not for the src
        if symlink_target != src:
            logger.error("The symlink that was created for \"" + dest + "\" -> \"" + src + "\" at \"" + symlink_path + "\" \
is instead targeted at \"" + symlink_target + "\"")
            return (1, None)


        return (0, symlink_path)
    except Exception as err:
        logger.error("Creating a symlink for src path \"" + original_src + "\" failed with err:\n" + str(err))
        return (1, None)


def create_temp_copy_of_file(label, file_path):
    "Create a temp copy of the file at file_path and return the temp_path." # noqa
    # pylint: disable=unused-variable

    global CONFIG

    label = "" if not label else " " + str(label)

    try:
        # Get a temp file path and add it to package_temp_file_paths_list and
        # copy file_path to it
        (fd, temp_path) = tempfile.mkstemp(prefix=os.path.basename(file_path) + "-")
        CONFIG.package_temp_file_paths_list.append(temp_path)
        shutil.copy2(file_path, temp_path, follow_symlinks=True)
        return (0, temp_path)
    except Exception as err:
        logger.error("Creating a temp copy of" + label + " file \"" + str(file_path or "") + "\" at \
\"" + str(temp_path or "") + "\" failed with err:\n" + str(err))
        return (1, None)


def replace_shebang_in_file(label, shebang, file_path):
    "Replace shebang of file at file_path if a shebang already exists." # noqa

    label = "" if not label else " " + str(label)
    orig_shebang = shebang

    # If shebang is not set or of type str or does not start with "#!"
    if not shebang or not isinstance(shebang, str) or not shebang.startswith("#!"):
        logger.error("The replacement shebang \"" + str(shebang or "") + "\" for" + label + " file at \
\"" + str(file_path or "") + "\" passed to replace_shebang_in_file function must be of type str and must start with '#!'")
        return 1

    try:
        # Open file at file_path and read the first_line, ignore
        # non "utf-8" characters to support "binary" files
        # newline characters like "\n" and "\r" are preserved
        with open(file_path, encoding="utf-8", errors="ignore", newline='') as fin:
            first_line = fin.readline()

        # If first_line does not start with "#!"
        if not first_line.startswith("#!"):
            logger.warning("Ignoring setting shebang since" + label + " file does not already have a shebang")
            return 0

        # If first_line ends with "\r\n", then remove any existing
        # "\r" characters from shebang and reapply "\r\n" format.
        if first_line.endswith("\r\n"):
            shebang = shebang.replace("\r", "").replace("\n", "\r\n")
        elif first_line.endswith("\n"):
            shebang = shebang.replace("\r", "")

        if orig_shebang != shebang:
            logger.debug("shebang: \"" + shebang + "\"")

        logger.debug("Setting shebang: \"" + shebang + "\"")

        # Escape "/", "\" and "&" since they will be treated as special
        # by sed replace pattern,
        # The literal newlines must be replaced with "\n" since otherwise
        # sed will fail with "unterminated s command" errors.
        # https://stackoverflow.com/a/29613573/14686958
        shebang = shebang.replace("\\", "\\\\").replace("/", "\\/").replace("&", "\\&").replace("\n", "\\n")
        # logger.debug("escaped_shebang: \"" + shebang + "\"")

        shebang_regex = r'%s' % "1 s/^#!.*$/" + shebang + "/"
        # logger.debug("shebang_regex: \"" + shebang_regex + "\"")

        # Call sed to in-place replace shebang of file at file_path
        sed_command_array = [
            "sed", "-i", "-E", "-e", shebang_regex, file_path
        ]

        (return_value, stdout, stderr) = run_shell_command(sed_command_array)
        if stdout and not stdout.isspace():
            if str(return_value) == "0":
                logger.debug(str(stdout))
            else:
                logger.error(str(stdout))
        if stderr and not stderr.isspace():
            if str(return_value) == "0":
                logger.debug(str(stderr))
            else:
                logger.error(str(stderr))
        if str(return_value) != "0":
            logger.error("sed command to replace shebang with \"" + shebang + "\" in" + label + " file at \
\"" + file_path + "\" failed")
            logger.error(get_list_string(sed_command_array))

        return return_value
    except Exception as err:
        logger.error("Replacing shebang with \"" + shebang + "\" in" + label + " file at \
\"" + str(file_path or "") + "\" failed with err:\n" + str(err))
        return 1





def replace_prefix_in_conffiles(old_prefix, new_prefix, file_path):
    "Replace old_prefix prefix with new_prefix in all entries of conffiles file at file_path." # noqa

    # If old_prefix is not set or of type str or does not start with "/"
    if not old_prefix or not isinstance(old_prefix, str) or not old_prefix.startswith("/"):
        logger.error("The old_prefix \"" + str(old_prefix or "") + "\" for conffiles file at \
\"" + str(file_path or "") + "\" passed to replace_prefix_in_conffiles function must be of type str and must start with '/'")
        return 1

    # If new_prefix is not set or of type str or does not start with "/"
    if not new_prefix or not isinstance(new_prefix, str) or not new_prefix.startswith("/"):
        logger.error("The new_prefix \"" + str(new_prefix or "") + "\" for conffiles file at \
\"" + str(file_path or "") + "\" passed to replace_prefix_in_conffiles function must be of type str and must start with '/'")
        return 1

    try:
        # Open file at file_path and read it to "lines" variable
        # conffiles must not contain non "utf-8" characters, otherwise
        # an exception will be raised
        with open(file_path, encoding="utf-8", errors="strict") as fin:
            lines = fin.readlines()

        # If lines is set
        if lines:
            for i in range(len(lines)):  # pylint: disable=consider-using-enumerate
                # If line starts with old_prefix, then replace only one
                # instance of it with new_prefix
                if lines[i].startswith(old_prefix):
                    # logger.debug("Replacing prefix for \"" + lines[i] + "\" entry in conffiles")
                    lines[i] = lines[i].replace(old_prefix, new_prefix, 1)
                    # logger.debug("update_entry \"" + lines[i] + "\"")

        # Open file at file_path in write mode and write all lines in "lines" list to it
        with open(file_path, "w") as fout:
            for line in lines:
                fout.write(line)

        return 0
    except Exception as err:
        logger.error("Replacing prefix \"" + old_prefix + "\" with \"" + new_prefix + "\" \
in conffiles file at \"" + str(file_path or "") + "\" failed with err:\n" + str(err))
        return 1


def validate_conffile_path(label, path):
    "Returns true if path string is a valid conffile path as per debian policy." # noqa

    label = "" if not label else " " + str(label)

    if not path or not isinstance(path, str): return False # noqa
    path = re.sub("[/]+", "/", path)  # replace multiple "/" with single

    # https://www.debian.org/doc/debian-policy/ch-files.html#configuration-files

    # If path is under "/etc/" or "<installation_prefix>/etc/"
    if re.match('^((/etc/)|(' + CONFIG.installation_prefix_escaped + '/etc/))[^/]+', path):
        return True
    else:
        logger.error("The" + label + " \"" + path + "\" is not a valid conffile path as per debian policy")
        return False


def validate_conffiles_file(conffiles_source, is_file, data_tar_file_path, tar_compression, tar_format):
    "Returns true if conffiles file is valid as per debian policy." # noqa

    # If tar_compression is null or of type str
    if tar_compression is None or not isinstance(tar_compression, str):
        logger.error("The tar_compression \"" + str(tar_compression or "") + "\" passed to validate_conffiles_file function must not be null and of type str")
        return False

    # If tar_format is not set or of type int
    if not tar_format or not isinstance(tar_format, int):
        logger.error("The tar_format \"" + str(tar_format or "") + "\" passed to validate_conffiles_file function must be set and of type int")
        return False

    # https://manpages.debian.org/testing/dpkg-dev/deb-conffiles.5.en.html
    # https://github.com/guillemj/dpkg/blob/1.20.7.1/src/unpack.c#L320

    if is_file:
        conffiles_file_path = conffiles_source
        # Read the conffile_paths from file at conffiles_file_path
        try:
            # File at path must not contain non "utf-8" characters,
            # otherwise an exception will be raised
            with open(conffiles_file_path, "r", encoding="utf-8", errors="strict") as conffiles_file:
                conffile_paths = conffiles_file.read()
                # If conffiles is empty
                if not conffile_paths:
                    logger.error("The conffiles file \"" + conffiles_file_path + "\" must not be empty")
                    return False
                conffile_paths_list = conffile_paths.split("\n")
        except Exception as err:
            logger.error("Opening conffiles file \"" + str(conffiles_file_path or "") + "\" failed with err:\n" + str(err))
            return False

        conffiles_file_label = "\"" + conffiles_file_path + "\""
    else:
        # Read the conffile_paths from the conffiles_source variable
        conffile_paths = conffiles_source

        # If conffile_paths is not set or of type str
        if not conffile_paths or not isinstance(conffile_paths, str):
            logger.error("The conffile_paths \"" + str(conffile_paths or "") + "\" passed to validate_conffiles_file function \
must not be empty and must be of type str")
            return False

        # If conffile_paths is not "utf-8" encodable
        if not is_utf8_encodable(conffile_paths):
            logger.error("The conffiles file content must be 'utf-8' encodable as per debian policy")
            return False

        conffile_paths_list = conffile_paths.split("\n")
        conffiles_file_label = "content"

    try:
        # Open a data_tar_file at data_tar_file_path with read mode and
        # tar_compression and tar_format
        with tarfile.open(data_tar_file_path, mode="r:" + tar_compression, format=tar_format) as data_tar_file:
            logger.debug("Validating conffiles file " + conffiles_file_label)

            for i, conffile_path in enumerate(conffile_paths_list):
                # If not the last line
                if i != len(conffile_paths_list) - 1:
                    # If line is empty
                    if not conffile_path:
                        logger.error("The conffiles file " + conffiles_file_label + " line " + str(i + 1) + " \
is empty, which is not allowed")
                        return False
                # Else if the last line
                else:
                    # If conffile_path is set
                    if conffile_path:
                        logger.error("The conffiles file " + conffiles_file_label + " last line " + str(i + 1) + " \
must be empty")
                        return False
                    else:
                        continue

                # Validate if conffile_path is a valid path as per debian policy
                if not validate_conffile_path("conffiles file " + conffiles_file_label + " path " + str(i + 1), conffile_path):
                    return False

                try:
                    logger.debug(str(i + 1) + ": \"" + conffile_path + "\"")
                    conffile_member = data_tar_file.getmember("." + conffile_path)

                    # If conffile_member not set or is not a regular file
                    if not conffile_member or not conffile_member.isreg():
                        logger.error("The conffile " + str(i + 1) + " file \"" + conffile_path + "\" \
in conffiles file " + conffiles_file_label + " must be a regular file")
                        return False
                except KeyError:
                    logger.error("The conffile " + str(i + 1) + " file \"" + conffile_path + "\" \
in conffiles file " + conffiles_file_label + " was not added to data.tar and must exist in it")
                    return False

        logger.debug("Validation successful")
        return True
    except Exception as err:
        logger.error("Opening data.tar file \"" + (data_tar_file_path or "") + "\" failed with err:\n" + str(err))
        return False





def validate_ar_entry(label, file_path):
    "Returns true if file at file_path is a valid ar entry." # noqa

    label = "" if not label else " " + str(label)

    # ar container has a hard limit on each member size of max 10 digits
    # or 9,999,999,999 bytes or 9536.74 MiB, since that is the max
    # number of digits allocated in the header.
    # https://wiki.debian.org/Teams/Dpkg/TimeTravelFixes
    # https://manpages.debian.org/testing/dpkg-dev/deb.5.en.html
    # https://sourceware.org/git/?p=binutils-gdb.git;a=blob;f=bfd/archive.c;h=9d63849a483d5cd5c5ad40eb6b811bae2c9ae813;hb=7e46a74aa3713c563940960e361e08defda019c2#l189

    try:
        file_size = str(os.path.getsize(file_path))
        if len(file_size) <= 10:
            return True
        else:
            logger.error("The" + label + " file at \"" + str(file_path or "") + "\" is not a valid ar entry since \
its size of " + "{:,}".format(int(file_size)) + " bytes is greater than the max allowed ar entry size of 9,999,999,999 bytes.")
            return False
    except Exception as err:
        logger.error("Reading size of " + label + " file \"" + str(file_path or "") + "\" failed with err:\n" + str(err))
        return False


def run_shell_command(command_array):
    "Run a shell command and get stdout, stderr and exit code." # noqa

    # If command_array is not set or of type list
    if not command_array or not isinstance(command_array, list):
        logger.error("The command_array passed to run_shell_command function must be set and of type list")
        return (1, None, None)

    try:
        p = subprocess.Popen(
            command_array, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
        )
        stdout, stderr = p.communicate()
        return_value = p.returncode
        stdout = stdout.rstrip("\n")
        stderr = stderr.rstrip("\n")
        return (return_value, stdout, stderr)
    except Exception as err:
        logger.error("Running " + str(command_array or [""]) + " shell command failed with err:\n" + str(err))
        return (1, None, None)


def create_tarinfo_obj_with_content(file_path, file_content):
    "Create a TarInfo file with the file_name and file_content." # noqa

    file_content = "" if not file_content else str(file_content)

    # If file_path is not set or of type str
    if not file_path or not isinstance(file_path, str):
        logger.error("The file_path passed to create_tarinfo_obj_with_content function must be set and of type str")
        return (1, None, None)

    try:
        # Convert file_content to a bytes file and find its size
        file = io.BytesIO(file_content.encode("utf-8"))
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)

        # Define a TarInfo object for file and set its size
        tarinfo = tarfile.TarInfo(name=file_path)
        tarinfo.size = file_size

        return (0, file, tarinfo)
    except Exception as err:
        logger.error("Creating the \"" + str(file_path or "") + "\" TarInfo file failed with err:\n" + str(err))
        return (1, None, None)





def is_valid_debian_user_name(user_name):
    "Returns true if user_name string is a valid user name as per debian policy." # noqa

    if not user_name or not isinstance(user_name, str): return False # noqa

    # https://manpages.debian.org/testing/passwd/useradd.8.en.html
    # https://github.com/shadow-maint/shadow/blob/4.8.1/src/useradd.c#L1448
    # https://github.com/shadow-maint/shadow/blob/4.8.1/libmisc/chkname.c
    # https://github.com/systemd/systemd/blob/v247/docs/USER_NAMES.md
    # https://pubs.opengroup.org/onlinepubs/9699919799/basedefs/V1_chap03.html#tag_03_437

    # Usernames may only be up to 32 characters long.
    if len(user_name) > 32:
        return False

    # It is usually recommended to only use usernames that begin with a lower case letter or an underscore,
    # followed by lower case letters, digits, underscores, or hyphens.
    # They can end with a dollar sign.
    return re.match('^[a-z_][a-z0-9_-]*[$]?$', user_name) or CONFIG.allow_bad_user_names_and_ids


def validate_debian_user_name(label, user_name, allowUnset=False, log_error=True):
    "Returns true if user_name is valid as per debian policy." # noqa

    if (user_name is None and allowUnset):
        return True

    label = "The user name" if not label else str(label)

    if user_name is None or not is_valid_debian_user_name(user_name):
        if log_error:
            logger.error(label + " \"" + str(user_name or "") + "\" is not a valid debian user name. It must begin with a lower \
case letter or an underscore, followed by lower case letters, digits, underscores, or hyphens. It can end with a \
dollar sign. In regular expression terms: '[a-z_][a-z0-9_-]*[$]?'. It may also be only up to 32 characters long.")
        return False
    else:
        return True


def is_valid_debian_user_id(user_id):
    "Returns true if user_id string is a valid uid as per debian policy." # noqa

    if not user_id or not isinstance(user_id, str) or not user_id.isdigit(): return False # noqa

    # https://www.debian.org/doc/debian-policy/ch-opersys.html#users-and-groups
    # https://manpages.debian.org/testing/passwd/useradd.8.en.html
    # https://github.com/systemd/systemd/blob/v247/docs/UIDS-GIDS.md
    # https://github.com/shadow-maint/shadow/blob/4.8.1/libmisc/find_new_uid.c

    # Only globally/statically allocated uids should be allowed.
    # As per debian policy, these are 0-99, 60000-64999 and 65534.
    # Other uids should be dynamically allocated for user names using
    # useradd through maintainer scripts.
    user_id = int(user_id)
    ranges = [(0, 99), (60000, 64999), (65534, 65534)]
    return any(lower <= user_id <= upper for (lower, upper) in ranges) or CONFIG.allow_bad_user_names_and_ids


def validate_debian_user_id(label, user_id, allowUnset=False, log_error=True):
    "Returns true if user_id is valid as per debian policy." # noqa

    if (user_id is None and allowUnset):
        return True

    label = "The user id" if not label else str(label)

    if user_id is None or not is_valid_debian_user_id(user_id):
        if log_error:
            logger.error(label + " \"" + str(user_id or "") + "\" is not a valid debian user id. It must be within the 0-99, \
60000-64999 and 65534 ranges.")
        return False
    else:
        return True


def validate_debian_ownership_tuple(pre_label, post_label, ownership_tuple, allowUnset=False, log_error=True):
    "Returns true if file ownership (uid, uname, gid, gname) tuple is valid as per debian policy." # noqa

    pre_label = "The ownership tuple" if not pre_label else str(pre_label)
    post_label = "" if not post_label else " " + str(post_label)

    (owner_uid, owner_uname, owner_gid, owner_gname) = ownership_tuple

    if not validate_debian_user_id(pre_label + " \"owner_uid\" field value" + post_label, owner_uid, allowUnset, log_error):
        return False

    if not validate_debian_user_name(pre_label + " \"owner_uname\" field value" + post_label, owner_uname, allowUnset, log_error):
        return False

    if not validate_debian_user_id(pre_label + " \"owner_gid\" field value" + post_label, owner_gid, allowUnset, log_error):
        return False

    if not validate_debian_user_name(pre_label + " \"owner_gname\" field value" + post_label, owner_gname, allowUnset, log_error):
        return False

    return True



def is_valid_linux_user_name(user_name):
    "Returns true if user_name string is a valid user name as per linux." # noqa

    if not user_name or not isinstance(user_name, str): return False # noqa

    # On POSIX the set of valid user names is defined as lower and upper
    # case ASCII letters, digits, period, underscore, and hyphen, with
    # the restriction that hyphen is not allowed as first character of
    # the user name. Interestingly no size limit is declared, i.e. in
    # neither direction, meaning that strictly speaking according to
    # POSIX both the empty string is a valid user name as well as a
    # string of gigabytes in length.
    return re.match('^[a-zA-Z0-9._-]+$', user_name) and not re.match('^[-]', user_name)


def validate_linux_user_name(label, user_name, allowUnset=False, log_error=True):
    "Returns true if user_name is valid as per linux." # noqa

    if (user_name is None and allowUnset):
        return True

    label = "The user name" if not label else str(label)

    if user_name is None or not is_valid_linux_user_name(user_name):
        if log_error:
            logger.error(label + " \"" + str(user_name or "") + "\" is not a valid linux user name. \
It must only contain lower and upper case letters, digits, periods, underscores, or hyphens but must \
not start with a hyphen.")
        return False
    else:
        return True


def is_valid_linux_user_id(user_id):
    "Returns true if user_id string is a valid uid as per linux." # noqa

    if not user_id or not isinstance(user_id, str) or not user_id.isdigit(): return False # noqa

    # In theory, the range of the C type uid_t is 32bit wide on Linux, i.e. 0-4294967295
    user_id = int(user_id)
    return 0 <= user_id <= 4294967295


def validate_linux_user_id(label, user_id, allowUnset=False, log_error=True):
    "Returns true if user_id is valid as per linux." # noqa

    if (user_id is None and allowUnset):
        return True

    label = "The user id" if not label else str(label)

    if user_id is None or not is_valid_linux_user_id(user_id):
        if log_error:
            logger.error(label + " \"" + str(user_id or "") + "\" is not a valid linux user id. It must be within the 0-4294967295.")
        return False
    else:
        return True


def validate_linux_ownership_tuple(pre_label, post_label, ownership_tuple, allowUnset=False, log_error=True):
    "Returns true if file ownership (uid, uname, gid, gname) tuple is valid as per linux." # noqa

    pre_label = "The ownership tuple" if not pre_label else str(pre_label)
    post_label = "" if not post_label else " " + str(post_label)

    (owner_uid, owner_uname, owner_gid, owner_gname) = ownership_tuple

    if not validate_linux_user_id(pre_label + " \"owner_uid\" field value" + post_label, owner_uid, allowUnset, log_error):
        return False

    if not validate_linux_user_name(pre_label + " \"owner_uname\" field value" + post_label, owner_uname, allowUnset, log_error):
        return False

    if not validate_linux_user_id(pre_label + " \"owner_gid\" field value" + post_label, owner_gid, allowUnset, log_error):
        return False

    if not validate_linux_user_name(pre_label + " \"owner_gname\" field value" + post_label, owner_gname, allowUnset, log_error):
        return False

    return True


def get_file_ownership_tuple(label, file_path):
    "Get the file ownership (uid, uname, gid, gname) tuple of file at file_path." # noqa

    label = "" if not label else " " + str(label)

    try:
        # Use lstat so that symlinks are not followed, specially broken
        # ones on host system.
        # Not using this since it returns 'getgrgid(): gid not found: <uid>'
        # on android.
        # stat_info = os.lstat(file_path)
        # uid = stat_info.st_uid
        # uname = pwd.getpwuid(uid)[0]
        # gid = stat_info.st_gid
        # gname = grp.getgrgid(gid)[0]


        # Call stat to get ownership
        # The "-L" option is not passed so that symlinks are not followed,
        # specially broken ones on host system.
        stat_command_array = [
            "stat", "-c", "%u:%U:%g:%G", file_path
        ]

        (return_value, stdout, stderr) = run_shell_command(stat_command_array)
        if stdout and not stdout.isspace():
            if str(return_value) != "0":
                logger.error(str(stdout))
        if stderr and not stderr.isspace():
            if str(return_value) != "0":
                logger.error(str(stderr))
        if str(return_value) != "0":
            logger.error("stat command to get file ownership of" + label + " file \
\"" + str(file_path or "") + "\" failed")
            logger.error(get_list_string(stat_command_array))

        ownership_string = re.sub(r"[\n\t\s]*", "", stdout)
        ownership = re.split('[:]', ownership_string)
        uid = ownership[0]
        uname = ownership[1]
        gid = ownership[2]
        gname = ownership[3]

        # If ownership variables are invalid
        if not validate_linux_ownership_tuple(label, None, (uid, uname, gid, gname), False):
            logger.error("Invalid ownership detected while getting file \
ownership of" + label + " file \"" + str(file_path or "") + "\"")
            return (1, None, None, None, None)

        return (0, str(uid), str(uname), str(gid), str(gname))
    except Exception as err:
        logger.error("Getting file ownership of" + label + " file \
\"" + str(file_path or "") + "\" failed with err:\n" + str(err))
        return (1, None, None, None, None)


def get_ownership_tupple_from_dict(ownership_dict):
    "Get the ownership (uid, uname, gid, gname) tuple from the ownership_dict." # noqa

    ownership_list = []
    for field in ["owner_uid", "owner_uname", "owner_gid", "owner_gname"]:
        if field in ownership_dict:
            ownership_list.append(ownership_dict[field])
        else:
            ownership_list.append(None)

    ownership_tuple = tuple(ownership_list)
    return ownership_tuple


def get_ownership_string_from_tupple(ownership_tuple, unset_if_root_uid_and_gid=False, prefix=""):
    "Get the ownership string from tuple (uid, uname, gid, gname)." # noqa

    (owner_uid, owner_uname, owner_gid, owner_gname) = ownership_tuple

    ownership_string = str(owner_uid or "0") + "(" + str(owner_uname or "root") + "):" + str(owner_gid or "0") + "(" + str(owner_gname or "root") + ")"

    if unset_if_root_uid_and_gid and ownership_string == "0(root):0(root)":
        ownership_string = ""
    else:
        ownership_string = prefix + ownership_string

    return ownership_string


def validate_file_permission(label, perm_string):
    "Returns true if perm_string matches a 3 or 4 digit permission octal." # noqa

    label = "The perm" if not label else str(label)

    if not perm_string or not isinstance(perm_string, str) or \
            not re.match('^[0-7]?[0-7][0-7][0-7]$', perm_string):
        logger.error(label + " \"" + str(perm_string or "") + "\" is not a valid 3 or 4 digit permission octal matching '[0-7]?[0-7][0-7][0-7]'")
        return False
    else:
        return True


def get_permission_string_from_octal(perm_octal, prefix=""):
    "Get the 3 or 4 digit file permission string from permission octal." # noqa

    # Keep only last 4 digits
    perm_string = str(perm_octal)[-4:]
    # Remove "0" or "o" from start if perm_string is a 4 digit string
    # This would be in case sticky, setuid and setgid bits are not set
    # or string was a octal representation starting with "0o"
    if len(perm_string) == 4 and (perm_string[0] == "0" or perm_string[0] == "o"):
        perm_string = perm_string[1:]
    return prefix + perm_string





def should_fix_perm(file_info):
    "Returns true if fixing permissions should be done for a file." # noqa

    # global file
    # true true fix
    # true false no_fix
    # false true fix
    # false false no_fix

    if CONFIG.fix_perms:
        # Default to true
        return "fix_perm" not in file_info or file_info["fix_perm"]
    else:
        # Default to false
        return "fix_perm" in file_info and file_info["fix_perm"]


def dh_and_android_fixperms(label, file_path, file_type, perm_string):
    "Fix permissions as per dh_fixperms debian and android policy." # noqa

    label = "" if not label else " " + str(label)

    try:
        # If perm_string is invalid
        if not validate_file_permission(label, perm_string):
            return (1, None)

        if file_type == FileType.SYMLINK:
            return (0, perm_string)

        (return_value, perm_string) = dh_fixperms(label, file_path, file_type, perm_string)
        if str(return_value) != "0":
            return (return_value, perm_string)

        # If android rules apply to file_path, then remove all group
        # and other permissions since only app user should have access.
        if android_rules_apply_to_path(file_path):
            perm_int = int(str(perm_string), 8)
            perm_int = get_effective_mode(perm_int, "go-rwx")
            return (0, get_permission_string_from_octal(oct(perm_int)))
        else:
            return (0, perm_string)

    except Exception as err:
        logger.error("Fixing perms of" + label + " file \
\"" + str(file_path or "") + "\" failed with err:\n" + str(err))
        return (1, None)


def dh_fixperms(label, file_path, file_type, perm_string):
    "Fix permissions string as per dh_fixperms debian policy. \
    Ownership is set to 'root' by set_package_data_file_metadata." # noqa

    # https://manpages.debian.org/testing/debhelper/dh_fixperms.1.en.html
    # https://github.com/Debian/debhelper/blob/debian/13.1/dh_fixperms
    # https://www.debian.org/doc/debian-policy/ch-files.html#permissions-and-owners
    # https://manpages.debian.org/testing/coreutils/chmod.1.en.html
    # https://docs.python.org/3/library/stat.html

    label = "" if not label else " " + str(label)

    try:
        # If perm_string is invalid
        if not validate_file_permission(label, perm_string):
            return (1, None)

        # find_and_reset_perm($tmp, 'go=rX,u+rw,a-s', '! -type l');
        if file_type == FileType.SYMLINK:
            return (0, perm_string)

        perm_int = int(str(perm_string), 8)
        logger.debug("dh_fixperms: perm_orig_str: " + perm_string + ", perm_orig_int: " + str(perm_int))

        perm_int = get_effective_mode(perm_int, "go=rX,u+rw,a-s", file_type)
        logger.debug("perm_mod_str: " + get_permission_string_from_octal(oct(perm_int)) + ", perm_mod_int: " + str(perm_int))

        # Fix up permissions in usr/share/doc, setting everything to not
        # executable by default, but leave examples directories alone.
        if re.match('^' + CONFIG.installation_prefix_escaped + '/share/doc/.+', file_path):
            # find_and_reset_perm("${tmp}/usr/share/doc", '0644', '-type f', "! -regex '$tmp/usr/share/doc/[^/]*/examples/.*'");
            if file_type == FileType.REGULAR and \
                    not re.match(CONFIG.installation_prefix_escaped + '/share/doc/[^/]*/examples/.*', file_path):
                return (0, "644")
            # find_and_reset_perm("${tmp}/usr/share/doc", '0755', '-type d');
            elif file_type == FileType.DIRECTORY:
                return (0, "755")



        # Manpages, include file, desktop files, etc., shouldn't be executable
        # find_and_reset_perm([
        #             "${tmp}/usr/share/man",
        #             "${tmp}/usr/include",
        #             "${tmp}/usr/share/applications",
        #             "${tmp}/usr/share/lintian/overrides",
        #         ], '0644', '-type f');
        non_executable_files_dirs = ["share/man", "include", "share/applications", "share/lintian/overrides"]
        if file_type == FileType.REGULAR and \
                re.match('^' + CONFIG.installation_prefix_escaped + '/' + get_regex_or_pattern(non_executable_files_dirs) + '/.+', file_path):
            return (0, "644")



        # Nor should perl modules.
        # find_and_reset_perm(["${tmp}/${vendorarch}", "${tmp}/${vendorlib}"],
        #                    'a-X', "-type f -perm -5 -name '*.pm'");
        # The '-perm -5' means at least bits of read and execute for
        # others permission are set.
        # https://www.debian.org/doc/packaging-manuals/perl-policy/ch-perl.html
        # $Config{vendorarch} (currently /usr/lib/arch-triplet/perl5/shortversion)
        # $Config{vendorlib}  (currently /usr/share/perl5)
        # Where shortversion indicates the current Perl major version (for example 5.22).
        # These locations, particularly $Config{vendorarch}, may change if necessary[4].
        # Packages should use $Config{vendorlib} and $Config{vendorarch},
        # not hardcode the current locations.
        # $ perl -e 'use Config; print $Config{vendorarch}'
        # /usr/lib/x86_64-linux-gnu/perl5/5.30
        # $ perl -e 'use Config; print $Config{vendorlib}'
        # /usr/share/perl5
        # Android(Termux) does not have architecture in its path.
        if is_android_path(file_path):
            architecture_string = ''
        else:
            architecture_string = '/' + CONFIG.package_architecture_escaped

        if file_type == FileType.REGULAR and \
                re.match('^' + CONFIG.installation_prefix_escaped + '/((lib' + architecture_string + '/perl[0-9]+/[0-9]+\\.[0-9]+(\\.[0-9]+)?)|(share/perl[0-9]+))/.+', file_path) and \
                path_matches_unix_wildcard(file_path, ['*.pm']) and \
                bool(perm_int & stat.S_IROTH) and \
                bool(perm_int & stat.S_IXOTH):
            return (0, get_permission_string_from_octal(oct(get_effective_mode(perm_int, "a-X", file_type))))



        # find_and_reset_perm($tmp, '0644', '-type f ' . patterns2find_expr(@mode_0644_patterns)) if @mode_0644_patterns;
        mode_0644_patterns = [
            # Libraries and related files
            '*.so.*', '*.so', '*.la', '*.a',
            # Web application related files
            '*.js', '*.css', '*.scss', '*.sass',
            # Images
            '*.jpeg', '*.jpg', '*.png', '*.gif',
            # OCaml native-code shared objects
            '*.cmxs',
            # Node bindings
            '*.node'
        ]

        node_file_patterns = ['*/cli.js', '*/bin.js']

        if file_type == FileType.REGULAR and \
                path_matches_unix_wildcard(file_path, mode_0644_patterns) and \
                not path_matches_unix_wildcard(file_path, node_file_patterns):
            return (0, "644")



        # find_and_reset_perm($tmp, '0755', '-type f ' . patterns2find_expr(@mode_0755_patterns)) if @mode_0755_patterns;
        # mode_0755_patterns = [
        #   # None for Debian
        # ]



        # Programs in the bin and init.d dirs should be executable..
        # find_and_reset_perm([map { "${tmp}/$_"} @executable_files_dirs], 'a+x', '-type f');
        # @executable_files_dirs = (usr/bin bin usr/sbin sbin usr/games etc/init.d)
        executable_files_dirs = [
            CONFIG.installation_prefix + "/bin",
            "/bin",
            CONFIG.installation_prefix + "/sbin",
            "/sbin",
            CONFIG.installation_prefix + "/games",
            "/etc/init.d"]
        if file_type == FileType.REGULAR and \
                re.match('^' + get_regex_or_pattern(executable_files_dirs) + '/.+', file_path):
            return (0, get_permission_string_from_octal(oct(get_effective_mode(perm_int, "a+x"))))



        # ADA ali files should be mode 444 to avoid recompilation
        # find_and_reset_perm("${tmp}/usr/lib", 'uga-w', "-type f -name '*.ali'");
        if file_type == FileType.REGULAR and \
                re.match('^' + CONFIG.installation_prefix_escaped + '/lib/.+', file_path) and \
                path_matches_unix_wildcard(file_path, ['*.ali']):
            return (0, get_permission_string_from_octal(oct(get_effective_mode(perm_int, "uga-w"))))



        # if ( -d "$tmp/usr/lib/nodejs/") {
        #     my @nodejs_exec_patterns = qw(*/cli.js */bin.js);
        #     my @exec_files = grep {
        #         not excludefile($_) and -f $_;
        #     } glob_expand(["$tmp/usr/lib/nodejs"], \&glob_expand_error_handler_silently_ignore, @nodejs_exec_patterns);
        #     reset_perm_and_owner(0755, @exec_files)
        # }
        # reset_perm_and_owner()
        # https://github.com/Debian/debhelper/blob/debian/13.1/lib/Debian/Debhelper/Dh_Lib.pm#L695
        # excludefile() (dh_fixperms --exclude)
        # https://github.com/Debian/debhelper/blob/debian/13.1/lib/Debian/Debhelper/Dh_Lib.pm#L1614
        if file_type == FileType.REGULAR and \
                re.match('^' + CONFIG.installation_prefix_escaped + '/lib/nodejs/.+', file_path) and \
                path_matches_unix_wildcard(file_path, node_file_patterns):
            return (0, "755")



        # if ( -d "$tmp/usr/share/bug/$package") {
        #     complex_doit("find $tmp/usr/share/bug/$package -type f",
        #                  "! -name 'script' ${find_exclude_options} -print0",
        #                  "2>/dev/null | xargs -0r chmod 644");
        #     if ( -f "$tmp/usr/share/bug/$package/script" ) {
        #         reset_perm_and_owner(0755, "$tmp/usr/share/bug/$package/script");
        #     }
        # } elsif ( -f "$tmp/usr/share/bug/$package" ) {
        #     reset_perm_and_owner(0755, "$tmp/usr/share/bug/$package");
        # }
        if file_type == FileType.REGULAR:
            if file_path in (
                    CONFIG.installation_prefix + "/share/bug/" + CONFIG.package_name,
                    CONFIG.installation_prefix + "/share/bug/" + CONFIG.package_name + "/script"):
                return (0, "755")
            elif re.match('^' + CONFIG.installation_prefix_escaped + '/share/bug/' + CONFIG.package_name_escaped + '/.+', file_path):
                return (0, "644")



        # Files in $tmp/etc/sudoers.d/ must be mode 0440.
        # find_and_reset_perm("${tmp}/etc/sudoers.d", '0440', "-type f ! -perm 440");
        if file_type == FileType.REGULAR and \
                re.match('^/etc/sudoers.d/.+', file_path):
            return (0, "440")

        return (0, get_permission_string_from_octal(oct(perm_int)))

    except Exception as err:
        logger.error("Fixing perms of" + label + " file \
\"" + str(file_path or "") + "\" failed with err:\n" + str(err))
        return (1, None)


def path_matches_unix_wildcard(file_path, patterns):
    "Test whether file_path matches Unix shell-style wildcards." # noqa
    # https://docs.python.org/3/library/fnmatch.html

    if not file_path or not patterns or not isinstance(patterns, list) or not patterns: return False # noqa

    for p in patterns:
        if fnmatch.fnmatch(file_path, p):
            return True
    return False


def get_file_permission_octal(label, file_path):
    "Get the 3 or 4 digit file permission octal of file at file_path." # noqa

    label = "" if not label else " " + str(label)

    try:
        # Use lstat so that symlinks are not followed, specially broken ones on host system
        return (0, get_permission_string_from_octal(oct(os.lstat(file_path).st_mode)))
    except Exception as err:
        logger.error("Getting file permission octal of" + label + " file \
\"" + str(file_path or "") + "\" failed with err:\n" + str(err))
        return (1, None)





def get_effective_mode(current_mode, symbolic, file_type=None):
    "Get octal mode, given current mode and symbolic mode modifier." # noqa

    # https://github.com/YakDriver/oschmod/blob/0.3.12/oschmod/__init__.py#L231
    # https://faun.pub/securing-files-on-windows-macos-and-linux-7b2b9899992
    # https://github.com/YakDriver/oschmod/blob/0.3.12/LICENSE
    # Apache License Version 2.0, Copyright 2020 Maintainers of plus3it/oschmod
    # License applies to get_effective_mode, _get_effective_mode_multiple
    # and _get_basic_symbol_to_mode
    # The original function only supported "rwx" permissions and has
    # been modified to support "Xst" as well.

    if not isinstance(symbolic, str):
        raise AttributeError("symbolic must be a string: " + "\"" + str(symbolic or "") + "\"")

    if "," in symbolic:
        return _get_effective_mode_multiple(current_mode, symbolic, file_type)

    result = re.search(r'^\s*([ugoa]*)([-+=])([rwxXst]*)\s*$', symbolic)
    if result is None:
        raise AttributeError("bad format of symbolic representation modifier: " + "\"" + str(symbolic or "") + "\"")

    clazz = result.group(1) or "ugo"
    operation = result.group(2)
    perm = result.group(3)


    if "X" in perm:
        if not file_type:
            raise AttributeError("The 'X' permission cannot be passed if file_type is not passed: " + "\"" + str(symbolic or "") + "\"")
        perm = perm.replace("x", "").replace("X", "")

        # "X" applies execute permissions to directories regardless of
        # their current permissions and applies execute permissions to
        # a file which already has at least one execute permission bit
        # already set (either user, group or others).
        if file_type == FileType.DIRECTORY or \
                (current_mode & stat.S_IXUSR) or \
                (current_mode & stat.S_IXGRP) or \
                (current_mode & stat.S_IXOTH):
            perm = perm + "x"


    if "a" in clazz:
        clazz = "ugo"

    # Bitwise magic
    bit_perm = _get_basic_symbol_to_mode(perm)
    mask_mode = \
        ("u" in clazz and bit_perm << 6) | \
        ("g" in clazz and bit_perm << 3) | \
        ("o" in clazz and bit_perm << 0)

    if operation == "=":
        # We preserve a class's current_mode by ORing it with the
        # new mask_mode passed.
        # S_IRWXU(448) user mask, S_IRWXG(56) group mask, S_IRWXO(7)
        # others mask are preserved if their respective class is not passed.
        # S_ISUID(2048) setuid and S_ISGID(1024) setgid are always preserved.
        # S_ISVTX(512) stick bit is only preserved if others class is not passed.
        original = \
            ("u" not in clazz and current_mode & stat.S_IRWXU) | \
            ("g" not in clazz and current_mode & stat.S_IRWXG) | \
            ("o" not in clazz and current_mode & stat.S_IRWXO & stat.S_ISVTX) | \
            (current_mode & stat.S_ISUID & stat.S_ISGID)

        new_mode = mask_mode | original

    elif operation == "+":
        new_mode = current_mode | mask_mode

    else:
        new_mode = current_mode & ~mask_mode


    # The setuid, setgid and stick bit are only set/unset if their
    # respective class is passed.
    if operation in ("=", "+"):
        new_mode = new_mode | \
            ("u" in clazz and "s" in perm and stat.S_ISUID) | \
            ("g" in clazz and "s" in perm and stat.S_ISGID) | \
            ("o" in clazz and "t" in perm and stat.S_ISVTX)
    else:
        new_mode = new_mode & \
            ~("u" in clazz and "s" in perm and stat.S_ISUID) & \
            ~("g" in clazz and "s" in perm and stat.S_ISGID) & \
            ~("o" in clazz and "t" in perm and stat.S_ISVTX)

    return new_mode


def _get_effective_mode_multiple(current_mode, modes, file_type=None):
    "Get octal mode, given current mode and symbolic mode modifiers." # noqa

    new_mode = current_mode
    for mode in modes.split(","):
        new_mode = get_effective_mode(new_mode, mode, file_type)
    return new_mode


def _get_basic_symbol_to_mode(symbol):
    "Calculate numeric value of set of 'rwx'." # noqa

    return ("r" in symbol and 1 << 2) | \
        ("w" in symbol and 1 << 1) | \
        ("x" in symbol and 1 << 0)


def unset_setuid_setgid(perm_int):
    "Unset setuid and setgid bits by doing a not(~) followed by and(&) operations." # noqa
    return perm_int & ~stat.S_ISUID & ~stat.S_ISGID





def android_rules_apply_to_path(path):
    "Returns true if path starts with '/data/data/<app_package>/files/' \
    and ignore_android_specific_rules is not enabled." # noqa

    return is_android_path(path) and not CONFIG.ignore_android_specific_rules


def is_android_path(path):
    "Returns true if path starts with '/data/data/<app_package>/files/'" # noqa
    return re.match('^/data/data/[^/]+/files/', path)


def is_hardlink(path):
    "Returns the file at path is a hardlink." # noqa

    # Hardlinks are checked with st_nlink to verify that there is only
    # one link to the file inode since tar.add() apparently does not
    # properly work for hardlinks and hence a copy must be made of the
    # file before they are added to the tar
    # FYI:
    # Make sure to empty trash can after deleting a hardlink
    # Find all hardlinks in current directory: `find . -type f -links +1`
    # File all references to a file inode under "/": `find / -xdev -samefile /path/to/file 2>/dev/null`
    return path and not os.path.islink(path) and os.path.isfile(path) and os.stat(path).st_nlink > 1


class FileType:
    "The types of files" # noqa

    SYMLINK = "symlink"
    REGULAR = "regular"
    DIRECTORY = "directory"


def validate_and_get_file_type(label, path):
    "Returns the file_type of file at path if its a symlink, regular file or directory, otherwise returns null." # noqa

    label = "" if not label else " " + str(label)

    # Validate if file at path exists and is a symlink, regular file
    # or directory.
    # The islink() check is done before isfile() since isfile()
    # follows symlinks which would result in wrong source_file_type,
    # i.e "regular" for a symlink if its not broken.
    # Invalid file types will be silently skipped if "source_recurse" is true.
    try:
        if os.path.islink(path):
            file_type = FileType.SYMLINK
        elif os.path.isfile(path):
            file_type = FileType.REGULAR
        elif os.path.isdir(path):
            file_type = FileType.DIRECTORY
        else:
            file_type = None
        return (0, file_type)
    except Exception as err:
        logger.error("Validating file type of" + label + " file \
\"" + str(path or "") + "\" failed with err:\n" + str(err))
        return (1, None)


def get_file_md5hash(label, file_path):
    "Get md5hash of file at file_path. The md5hash of file is calculated in chunks of 4096 bytes." # noqa

    label = "" if not label else " " + str(label)

    try:
        md5hash = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                md5hash.update(chunk)
        return (0, md5hash.hexdigest())
    except Exception as err:
        logger.error("Getting md5hash of" + label + " file \"" + str(file_path or "") + "\" \
failed with err:\n" + str(err))
        return (1, None)





def set_package_data_file_metadata(tarinfo):
    "Set metadata for package data file." # noqa

    if CONFIG.package_data_file_mtime:
        tarinfo.mtime = CONFIG.package_data_file_mtime

    if CONFIG.package_data_file_perm:
        tarinfo.mode = int(str(CONFIG.package_data_file_perm), 8)

    if CONFIG.package_data_file_uid:
        tarinfo.uid = int(CONFIG.package_data_file_uid)
    else:
        tarinfo.uid = 0

    if CONFIG.package_data_file_uname:
        tarinfo.uname = str(CONFIG.package_data_file_uname)
    else:
        tarinfo.uname = "root"

    if CONFIG.package_data_file_gid:
        tarinfo.gid = int(CONFIG.package_data_file_gid)
    else:
        tarinfo.gid = 0

    if CONFIG.package_data_file_gname:
        tarinfo.gname = str(CONFIG.package_data_file_gname)
    else:
        tarinfo.gname = "root"

    return tarinfo


def set_control_info_file_metadata(tarinfo):
    "Set metadata for control info file." # noqa

    if CONFIG.package_control_info_file_mtime:
        tarinfo.mtime = CONFIG.package_control_info_file_mtime

    tarinfo.mode = 0o644
    tarinfo.uid = tarinfo.gid = 0
    tarinfo.uname = tarinfo.gname = "root"
    return tarinfo


def set_maintainer_script_file_metadata(tarinfo):
    "Set metadata for maintainer script file." # noqa

    tarinfo.mode = 0o755
    tarinfo.uid = tarinfo.gid = 0
    tarinfo.uname = tarinfo.gname = "root"
    return tarinfo


def check_and_get_android_specific_directory_perm(path):
    "Get directory perm octal depending on if path is under android app data directory." # noqa

    # If android rules apply, then return permission "700" since group
    # and others octals must be unset so that only the user has access
    if android_rules_apply_to_path(path):
        return "700"
    # Else return default permission
    else:
        return "755"


def set_filesystem_encoding():
    "Set the global variable FILESYSTEM_ENCODING." # noqa

    global FILESYSTEM_ENCODING

    # Get filesystem encoding
    # It is the locale encoding on UNIX systems, will return None for python < 3.2
    FILESYSTEM_ENCODING = sys.getfilesystemencoding()

    # If FILESYSTEM_ENCODING is not set, then set it to "ascii" (LANG=C)
    # Python defaults to the same if not set for >= 3.2
    if not FILESYSTEM_ENCODING:
        logger.warning("Force setting filesystem encoding to 'ascii' since its not set")
        FILESYSTEM_ENCODING = "ascii"

    # If FILESYSTEM_ENCODING does not equal "utf-8"
    if FILESYSTEM_ENCODING != "utf-8":
        logger.warning("Filesystem encoding is set to \"" + FILESYSTEM_ENCODING + "\" instead of 'utf-8' \
which may cause termux-create-package to fail. \
Check your LANG and LC_CTYPE environment variables")


def validate_control_file_field_name(label, field):
    "Returns true if field is a valid control file field name." # noqa

    label = "The package control file field" if not label else str(label)

    if field is None or not isinstance(field, str): return False # noqa

    # The field name is composed of US-ASCII characters excluding
    # control characters, space, and colon (i.e., characters in the
    # ranges U+0021 (!) through U+0039 (9), and U+003B (;) through
    # U+007E (~), inclusive). Field names must not begin with the
    # comment character (U+0023 #), nor with the hyphen character (U+002D -).
    # https://www.debian.org/doc/debian-policy/ch-controlfields.html#syntax-of-control-files

    # If field is within the range 32/U+0021 through 126/U+007E and
    # does not contain a space ' ' or colon ':' and
    # does not start with a hyphen '-' or comment character '#'
    if is_restricted_ascii_encodable(field) and re.match('.*[ :]+.*', field) is None and not re.match('^[-#]', field):
        return True
    else:
        logger.error(label + " \"" + field + "\" is not a valid field name as per debian policy. \
It must be composed of US-ASCII characters within the range 32/U+0021 through 126/U+007E \
excluding space ' ' and colon ':' characters. It must not begin with a hyphen '-' or comment '#' characters.")
        return False


def is_ascii_encodable(var):
    "Returns true if var is 'ascii' encodable." # noqa

    if var is None or not isinstance(var, str): return False # noqa

    try:
        var.encode("ascii", 'strict')
        return True
    except UnicodeEncodeError:
        return False


def is_restricted_ascii_encodable(var):
    "Returns true if var is 'ascii' encodable and is within the range 32/U+0021 (space ' ') through 126/U+007E (tilda '~'), inclusive" # noqa

    if var is None or not isinstance(var, str): return False # noqa

    return all(32 <= ord(char) <= 126 for char in var)


def is_utf8_encodable(var):
    "Returns true if var is 'utf-8' encodable." # noqa

    if var is None or not isinstance(var, str): return False # noqa

    try:
        var.encode("utf-8", 'strict')
        return True
    except UnicodeEncodeError:
        return False


def validate_data_tar_path(label, path):
    "Returns true if path string is a valid data.tar path as per debian policy." # noqa

    label = "" if not label else " " + str(label)

    # If path is not set or of type str
    if not path or not isinstance(path, str):
        logger.error("The path passed to validate_data_tar_path function must be set and of type str")
        return False

    path = re.sub("[/]+", "/", path)  # replace multiple "/" with single

    # If path is under "/bin/", "/sbin/", "/usr/bin/", "/usr/sbin/",
    # "/usr/games/" or "<installation_prefix>/bin/"
    # there is no end anchor "$" in the  following regex since
    # restrictions should ideally apply to any files under the
    # respective directories, even if they are under sub directories.
    # https://www.debian.org/doc/debian-policy/ch-files.html#file-names
    if re.match('^(((/usr)?/[s]?bin/)|(/usr/games/)|(' + CONFIG.installation_prefix_escaped + '/bin/))[^/]+', path):
        # If path is not "ascii" encodable
        if not is_ascii_encodable(path):
            logger.error("The" + label + " path \"" + path + "\" must be an 'ascii' encodable path as per debian policy")
            return False
    else:
        # If path is not "utf-8" encodable
        if not is_utf8_encodable(path):
            logger.error("The" + label + " path \"" + path + "\" must be a 'utf-8' encodable path as per debian policy")
            return False

    # https://www.debian.org/doc/debian-policy/ch-opersys.html#file-system-hierarchy
    # https://refspecs.linuxfoundation.org/FHS_3.0/fhs/index.html

    # If path is under "/usr/local/" or "<installation_prefix>/local/"
    if re.match('^((/usr/local/)|(' + CONFIG.installation_prefix_escaped + '/local/))[^/]+', path):
        logger.error("The" + label + " path \"" + path + "\" is an invalid path as per debian policy since its under '*/usr/local'")
        return False

    return True


def get_sub_file_paths_list_under_directory(label, directory_path, ignore_non_utf8_paths):
    "Return sub file paths list under directory at directory_path." # noqa

    label = "The" if not label else str(label)

    try:
        # If directory_path is not set or of type str
        if not directory_path or not isinstance(directory_path, str) or not os.path.isdir(directory_path):
            logger.error("The directory_path passed to get_sub_file_paths_list_under_directory function \
must be set and of type str and must be a path to a directory")
            return (1, None)

        sub_file_paths_list = []

        # Recursively add all sub files under directory_path to
        # sub_file_paths_list directory_path is converted from a
        # unicode string to bytes before passing it to os.walk so that
        # it passes bytes to os.scandir which in turn also returns paths
        # as bytes.
        # This is done to ensure that all paths are "utf-8" encodable
        # as per debian policy for cases where LANG or LC_CTYPE are set
        # to something other than "utf-8" for a different filesystem
        # encoding or filenames cannot be decoded to "utf-8".
        # All paths set through manifest are already "utf-8" encodable,
        # but the paths added dynamically may not be.
        # Bytes paths were deprecated in python 3.3 on windows
        # (but were undeprecated in 3.6) so use string paths for it.
        # https://docs.python.org/3/howto/unicode.html#unicode-filenames
        if not sys.platform.startswith("win"):
            path_separator_bytes = "/".encode(FILESYSTEM_ENCODING)
            for dirpath_bytes, directories_bytes, filenames_bytes in os.walk(directory_path.encode(FILESYSTEM_ENCODING)):

                for j in range(len(directories_bytes)):  # pylint: disable=consider-using-enumerate
                    # Decode dirpath + "/" + directory bytes to a "utf-8" string
                    (return_value, directory_utf8) = decode_and_validate_data_tar_path_bytes(
                        label + " \"" + directory_path + "\" sub directory " + str(j),
                        dirpath_bytes + path_separator_bytes + directories_bytes[j])
                    if str(return_value) != "0":
                        if str(return_value) == "1" and ignore_non_utf8_paths:
                            continue
                        else:
                            return (return_value, None)

                    # Add directory path to sub_file_paths_list
                    sub_file_paths_list.append(directory_utf8)

                for j in range(len(filenames_bytes)):  # pylint: disable=consider-using-enumerate
                    # Decode dirpath + "/" + filename bytes to a "utf-8" string
                    (return_value, filename_utf8) = decode_and_validate_data_tar_path_bytes(
                        label + " \"" + directory_path + "\" sub file " + str(j),
                        dirpath_bytes + path_separator_bytes + filenames_bytes[j])
                    if str(return_value) != "0":
                        if str(return_value) == "1" and ignore_non_utf8_paths:
                            continue
                        else:
                            return (return_value, None)

                    # Add file path to sub_file_paths_list
                    sub_file_paths_list.append(filename_utf8)
        else:
            for dirpath_string, directories_string, filenames_string in os.walk(directory_path):
                for directory_string in directories_string:
                    sub_file_paths_list.append(dirpath_string + "/" + directory_string)
                for filename_string in filenames_string:
                    sub_file_paths_list.append(dirpath_string + "/" + filename_string)

        return (0, sub_file_paths_list)
    except Exception as err:
        logger.error("Getting sub file paths list under the directory \"" + str(directory_path or "") + "\" failed with err:\n" + str(err))
        return (1, None)


def decode_and_validate_data_tar_path_bytes(label, path_bytes):
    "Decodes and validate a path passed as bytes is 'utf-8' encodable as per debian policy." # noqa

    label = "The path" if not label else str(label)

    # If path_bytes is not set or is not of type bytes
    if not path_bytes or not isinstance(path_bytes, bytes):
        logger.error(label + " path_bytes passed to decode_and_validate_data_tar_path_bytes function must be set and of type bytes")
        return (1, None)

    # https://www.debian.org/doc/debian-policy/ch-files.html#file-names

    # Exception will be raised even if filesystem encoding is "utf-8"
    # but path_bytes cannot be decoded to "utf-8".
    # https://stackoverflow.com/a/26978444/14686958
    # touch "$(echo -e "\x8b\x8bThis is a bad filename")"

    try:
        # Decode bytes to a "utf-8" string
        path_utf8 = path_bytes.decode("utf-8")
        return (0, path_utf8)
    except UnicodeDecodeError as err:
        logger.error(label + " must be a 'utf-8' encodable path as per debian policy")
        try:
            # If FILESYSTEM_ENCODING equals "utf-8"
            if FILESYSTEM_ENCODING == "utf-8":
                logger.error("path 'utf-8' encoded and truncated: \"" + path_bytes.decode("utf-8", "ignore") + "\"")
            else:
                logger.error("path '" + FILESYSTEM_ENCODING + "' encoded: \"" + path_bytes.decode(FILESYSTEM_ENCODING) + "\"")
        except Exception:
            pass
        logger.error("err:\n" + str(err))
        return (1, None)


def is_valid_utf8_encoded_file(label, file_path):
    "Returns true if file at path is valid 'utf-8' encoded file." # noqa

    label = "" if not label else " " + str(label)

    try:
        # File at file_path must not contain non "utf-8" characters, otherwise an exception will be raised
        with open(file_path, "r", encoding="utf-8", errors="strict") as file:
            file.readlines()
            return True
    except UnicodeDecodeError as err:
        logger.error("The" + label + " file must be a valid 'utf-8' encoded file")
        logger.error("err:\n" + str(err))
        return False
    except Exception as err:
        logger.error("Opening" + label + " file failed with err:\n" + str(err))
        return False


def is_parent_path_reference_containing_path(path):
    "Returns true if path equals '..', starts with '../', contains '/../' or ends with '/..'." # noqa

    return re.match(r'(?:^\.\.$)|(?:^\.\./)|(?:/\.\./)|(?:/\.\.$)', str(path))


def validate_subpaths_do_not_exist_under_file_path(err, file_path, all_file_paths_list):
    "Returns true if file_path is not a parent of any path in all_file_paths_list" # noqa

    err = "The file_path contains the following sub paths" if not err else str(err)

    # If file_path is not set or of type str
    if not file_path or not isinstance(file_path, str):
        logger.error("The file_path passed to validate_subpaths_do_not_exist_under_file_path function must be set and of type str")
        return False

    # If all_file_paths_list is null or not of type list
    if all_file_paths_list is None or not isinstance(all_file_paths_list, list):
        logger.error("The all_file_paths_list passed to validate_subpaths_do_not_exist_under_file_path function must not be null and of type list")
        return False

    subpaths_list = [all_file_path for all_file_path in all_file_paths_list if all_file_path.startswith(file_path + "/")]

    if subpaths_list:
        logger.error(err)
        logger.error("file_path: " + " \"" + file_path + "\"")
        logger.error("subpaths_list: " + " \"" + str(subpaths_list) + "\"")
        return False
    else:
        return True





def update_manifest_format(manifest):
    "Update manifest to make it compatible with version '>= 0.12.0' while maintaining backward compatibility." # noqa

    global CONFIG

    # If "version" field exists in the manifest and is an int, then convert it to a string
    if "version" in manifest and manifest["version"] and \
            isinstance(manifest["version"], int):
        manifest["version"] = str(manifest["version"])



    # Define a list of fields to rename in the manifest
    manifest_fields_to_rename_dict = {
        "name": "Package",
        "arch": "Architecture",
        "version": "Version",
        "maintainer": "Maintainer",
        "depends": "Depends",
        "provides": "Provides",
        "suggests": "Suggests",
        "recommends": "Recommends",
        "conflicts": "Conflicts",
        "homepage": "Homepage",
        "description": "Description"
    }

    if "control" not in manifest or not manifest["control"]:
        manifest["control"] = collections.OrderedDict()
    # If any field in the manifest_fields_to_rename_dict exists in the manifest
    for old_field, new_field in manifest_fields_to_rename_dict.items():
        if old_field in manifest:
            # Rename old_field to new_field
            # If new_field already exists, it will be overwritten
            value = manifest[old_field]
            del manifest[old_field]
            manifest["control"][new_field] = value



    # If "files" field exists in the manifest and is a dict
    if "files" in manifest and manifest["files"] and \
            isinstance(manifest["files"], dict):
        # Enable old_manifest_format
        logger.debug("Old manifest format detected")
        CONFIG.old_manifest_format = True

        # Preserve backward compatibility with version '>= 0.8'

        # Automatically set "fix_perms" to False to preserve permissions
        CONFIG.fix_perms = False

        # Update manifest to new "data_files" format
        # Convert
        # '"files": {"source_file_path": "dest_file_path"}'
        # To
        # '"data_files": {"dest_file_path": { "source": "source_file_path"... }}'
        # Automatically set "source_recurse" to True to enable
        # recursion of source directories.
        # Automatically set "source_ownership" to True to preserve
        # ownership of source files. If ownership id or name are not
        # valid as per debian policy, then ownership of those files
        # will be ignored by create_data_tar() and "root:root"
        # ownership will be used. Check is_valid_debian_user_id() for more info.
        new_package_data_files_dict = collections.OrderedDict()
        old_package_data_files_dict = manifest["files"]
        for source_file_path in old_package_data_files_dict:
            dest_file_path = old_package_data_files_dict[source_file_path]
            new_package_data_files_dict[dest_file_path] = \
                {"source": source_file_path, "source_recurse": True, "source_ownership": True}
        del manifest["files"]
        manifest["data_files"] = new_package_data_files_dict
    else:
        CONFIG.old_manifest_format = False



    # If "Description" field exists in the manifest control and is not
    # a list,  then convert manifest["control"]["Description"] to a
    # list after splitting it on line boundaries, like newlines.
    control = manifest["control"]
    if control and isinstance(control, dict) and \
            "Description" in control and control["Description"] and \
            not isinstance(control["Description"], list):
        manifest["control"]["Description"] = str(manifest["control"]["Description"]).splitlines()


    return 0


def validate_manifest(manifest):
    "Validate the package manifest." # noqa
    # pylint: disable=broad-except

    valid_package_name_regex = '^[a-z0-9][a-z0-9.+-]+$'
    valid_package_version_regex = '^([0-9]+:)?[0-9][a-zA-Z0-9.+~]*(-[a-zA-Z0-9.+~]+)?$'
    valid_package_architecture_wildcard_regex = '^[a-z0-9][a-z0-9.+_-]+( [a-z0-9][a-z0-9.+_-]+)*$'

    logger.debug("Validating Manifest")

    control = manifest["control"]

    # Check if control contains duplicate fields
    # Control file field names are not case-sensitive,
    # hence convert to lowercase for detection of duplicates that are
    # of a different case since control is of type dict, it will not
    # allow duplicates of different case.
    control_fields_list = [x.lower() for x in list(control.keys())]
    control_fields_duplicate_list = \
        set([x for x in control_fields_list if control_fields_list.count(x) > 1])  # pylint: disable=consider-using-set-comprehension

    if control_fields_duplicate_list:
        logger.error("The manifest \"control\" dict contains duplicate fields: " + str(control_fields_duplicate_list))
        return 1

    mandatory_string_fields_list = []
    mandatory_string_fields_list.extend(PACKAGE_CONTROL_FILE_MANDATORY_STRING_FIELDS_LIST)
    mandatory_string_fields_list.extend(["Description"])
    # If a mandatory field is missing
    for field in mandatory_string_fields_list:
        if field not in control or not control[field]:
            logger.error("Missing mandatory \"" + field + "\" package control file field in manifest \"control\" dict")
            return 1

    # If "data_files" field is missing
    if "data_files" not in manifest or not manifest["data_files"]:
        logger.error("Missing mandatory \"data_files\" package create info field in the manifest")
        return 1

    # For all fields, values in control
    for field, value in control.items():
        # If field is not a valid control file field
        if not validate_control_file_field_name("The package control file field in the manifest \"control\" dict", field):
            return 1

        # If field is in PACKAGE_CONTROL_FILE_MANDATORY_STRING_FIELDS_LIST
        if field in PACKAGE_CONTROL_FILE_MANDATORY_STRING_FIELDS_LIST:
            # If value is not null or a string
            if value is not None and not isinstance(value, str):
                logger.error("The \"" + field + "\" package control file field value in the manifest \"control\" dict must be of type str")
                return 1
        # Else if value is not null or a string or a list
        elif value is not None and not isinstance(value, str) and not isinstance(value, list):
            logger.error("The \"" + field + "\" package control file field value in the manifest \"control\" dict must be of type str or list")
            return 1

        # If value is not null
        if value is not None:
            # Handle case where newline characters '\n' were added
            # to any item of the list or string. Also handle case
            # where a user tries to sneak past control file fields
            # through the value of another field in the manifest control.

            # If value is a list, like the "Description" field
            if isinstance(value, list):
                # If field exists in PACKAGE_CONTROL_FILE_RELATIONSHIP_FIELDS_LIST,
                # then join value with ", " and split it again on
                # a newline fields in PACKAGE_CONTROL_FILE_RELATIONSHIP_FIELDS_LIST
                # can also be defined on multiple lines by ending
                # an entry line on a comma, and adding next entry
                # on a newline after a space character.
                if field in PACKAGE_CONTROL_FILE_RELATIONSHIP_FIELDS_LIST:
                    list_value = ", ".join(map(str, value)).split("\n")
                # Else join value on newline and split it again on a newline
                else:
                    list_value = "\n".join(map(str, value)).split("\n")
            # Is a string
            else:
                list_value = value.split("\n")

            i = 1
            # Check if value is valid
            for value1 in list_value:

                # If first line
                if i == 1:
                    # If line is empty, only contains whitespaces or " ."
                    if not value1 or value1.isspace() or value1 == " .":
                        logger.error("The \"" + field + "\" field value line " + str(i) + ": \"" + value1 + "\" \
in the manifest \"control\" dict is empty and must contain some non-whitespace characters")
                        return 1

                else:
                    # If line is empty or only contains whitespaces
                    if not value1 or value1.isspace():
                        logger.error("The \"" + field + "\" field value line " + str(i) + ": \"" + value1 + "\" \
in the manifest \"control\" dict is empty and must at least contain a space followed by a dot for empty lines: \" .\"")
                        return 1

                    # If line does not start with a space " " or tab "\t"
                    if not value1.startswith(" ") and not value1.startswith("\t"):
                        logger.error("The \"" + field + "\" field value line " + str(i) + ": \"" + value1 + "\" \
in the manifest \"control\" dict does not start with a space or tab character, which is invalid")
                        return 1

                i += 1


    # For all fields, values in manifest
    for field, value in manifest.items():
        # If field is not in PACKAGE_CREATE_INFO_FIELDS_LIST
        if field not in PACKAGE_CREATE_INFO_FIELDS_LIST:
            logger.error("The \"" + field + "\" field in the manifest is not a supported package create info field")
            return 1

        # If field is in the list
        if field in ["fix_perms", "ignore_android_specific_rules", "allow_bad_user_names_and_ids"]:
            # If value is not null or a bool
            if value is not None and not isinstance(value, bool):
                logger.error("The \"" + field + "\" package create info field value in the manifest must be of type bool")
                return 1
        # Else if field is in the list
        elif field in ["control", "data_files"]:
            # If value is not null or a dict
            if value is not None and not isinstance(value, dict):
                logger.error("The \"" + field + "\" package create info field value in the manifest must be of type dict")
                return 1
        # Else if value is not null or a string
        elif value is not None and not isinstance(value, str):
            logger.error("The \"" + field + "\" package create info field value in the manifest must be of type str")
            return 1



    # If a package_name is not valid according to debian policy
    # https://www.debian.org/doc/debian-policy/ch-controlfields.html#package
    if not re.match(valid_package_name_regex, CONFIG.package_name):
        logger.error("Package \"" + CONFIG.package_name + "\" field value is invalid in the manifest \"control\" dict. \
It must consist only of lower case letters (a-z), \
digits (0-9), plus (+) and hyphen (-) signs, and periods (.). It must be at least \
two characters long and must start with an alphanumeric character.")
        return 1



    # If a package_version is not valid according to debian policy
    # Https://www.debian.org/doc/debian-policy/ch-controlfields.html#version
    if not re.match(valid_package_version_regex, CONFIG.package_version):
        logger.error("Version \"" + CONFIG.package_version + "\" field value is invalid in the manifest \"control\" dict. \
It must be in the format '[epoch:]upstream_version[-debian_revision]'. \
'epoch' can only be an integer. \
'upstream_version' and 'debian_revision' must consist only of upper or lower case \
letters (a-zA-Z), digits (0-9), plus (+) and tilde (~) signs, and periods (.). \
The 'upstream_version' must start with a digit. \
The hyphen (-) is only allowed if 'debian_revision' is set.")
        return 1


    # If a package_architecture is not valid according to debian policy
    # If android rules apply to installation_prefix
    if android_rules_apply_to_path(CONFIG.installation_prefix):
        # if package_architecture is not in the list of valid architectures
        # Checking for ["all", "arm", "i686", "aarch64", "x86_64"] only
        # applies for android and not for other distributions.
        if CONFIG.package_architecture not in ["all", "arm", "i686", "aarch64", "x86_64"]:
            logger.error("Architecture \"" + CONFIG.package_architecture + "\" field value is invalid in the manifest \"control\" dict. \
It must be one of 'all', 'arm', 'i686', 'aarch64' or 'x86_64' if installation prefix is under '/data/data/<app_package>/files/' to target android.")
            return 1

    # If package_architecture is not a space separated list of architectures or architecture wildcards
    # https://www.debian.org/doc/debian-policy/ch-controlfields.html#architecture
    if not re.match(valid_package_architecture_wildcard_regex, CONFIG.package_architecture):
        logger.error("Architecture \"" + CONFIG.package_architecture + "\" field value is invalid in the manifest \"control\" dict. \
It must contain a space separated list of architectures or architecture wildcards \
that consist only of lower case letters (a-z), digits (0-9), plus (+) and hyphen (-) \
signs, periods (.), underscores (_) and spaces ( ). It must be at least two characters \
long and must start with an alphanumeric character.")
        return 1

# If "Source" field exists in the control
    if "Source" in control:
        source_name = control["Source"]
        # If "Source" field is invalid
        # https://www.debian.org/doc/debian-policy/ch-controlfields.html#s-f-source
        if not re.match(valid_package_name_regex, source_name):
            logger.error("Source \"" + source_name + "\" field value is invalid in the manifest \"control\" dict. \
It must consist only of lower case letters (a-z), \
digits (0-9), plus (+) and hyphen (-) signs, and periods (.). It must be at least \
two characters long and must start with an alphanumeric character.")
            return 1



    # If "tar_compression" field is invalid
    if "tar_compression" in manifest and manifest["tar_compression"] and \
            manifest["tar_compression"] not in ["none", "gz", "xz"]:
        logger.error("tar_compression \"" + manifest["tar_compression"] + "\" field value is invalid in the manifest. It must be one of 'none', 'gz' or 'xz'")
        return 1

    # If "tar_format" field is invalid
    if "tar_format" in manifest and manifest["tar_format"] and \
            manifest["tar_format"] not in ["gnutar", "ustar", "pax"]:
        logger.error("tar_format \"" + manifest["tar_format"] + "\" field value is invalid in the manifest. It must be one of 'none', 'gz' or 'xz'")
        return 1



    # Check if "data_files" field is valid
    CONFIG.package_data_files_dict = manifest["data_files"]  # pylint: disable=redefined-outer-name

    i = 1
    # For all dest_file_path, dest_file_info in the "data_files" dict set to package_data_files_dict
    for dest_file_path, dest_file_info in CONFIG.package_data_files_dict.items():

        # If dest_file_path is null or is not a string
        if dest_file_path is None or not isinstance(dest_file_path, str):
            logger.error("data_files: destination file " + str(i) + " value in the manifest must be set and of type str")
            return 1



        # If dest_file_info is null or is not a dict
        if dest_file_info is None or not isinstance(dest_file_info, dict):
            logger.error("data_files: destination file " + str(i) + " \"" + dest_file_path + "\" \
info value in the manifest must be set and of type dict")
            return 1

        # For all fields, values in dest_file_info
        for field, value in dest_file_info.items():
            # If field is not in PACKAGE_DATA_FILES_ATTRIBUTES_AND_ACTIONS_LIST
            if field not in PACKAGE_DATA_FILES_ATTRIBUTES_AND_ACTIONS_LIST:
                logger.error("data_files: destination file " + str(i) + " \"" + dest_file_path + "\" \
info \"" + field + "\" field in the manifest is not a supported attribute or action field")
                return 1

            # If field is in the list
            if field in [
                    "is_conffile", "ignore", "ignore_if_no_exist",
                    "source_readlink", "source_recurse", "source_ownership",
                    "fix_perm", "set_parent_perm"]:
                # If value is not null or a bool
                if value is not None and not isinstance(value, bool):
                    logger.error("data_files: destination file " + str(i) + " \"" + dest_file_path + "\" \
info \"" + field + "\" field value in the manifest must be of type bool")
                    return 1
            # Else if field is in the list
            elif field in ["symlink_destinations"]:
                # If value is not null or a list
                if value is not None and not isinstance(value, list):
                    logger.error("data_files: destination file " + str(i) + " \"" + dest_file_path + "\" \
info \"" + field + "\" field value in the manifest must be of type list")
                    return 1
            # Else if value is not null or a string
            elif value is not None and not isinstance(value, str):
                logger.error("data_files: destination file " + str(i) + " \"" + dest_file_path + "\" \
info \"" + field + "\" field value in the manifest must be of type str")
                return 1



        # If "perm" field exists in dest_file_info
        if "perm" in dest_file_info and dest_file_info["perm"] is not None:
            # If "perm" field is invalid
            if not validate_file_permission("data_files: destination file " + str(i) + " \"" + dest_file_path + "\" \
info \"perm\" field value in the manifest", dest_file_info["perm"]):
                return 1

        if not validate_debian_ownership_tuple("data_files: destination file " + str(i) + " \"" + dest_file_path + "\" \
info", "in the manifest", get_ownership_tupple_from_dict(dest_file_info), True):
            return 1

        i += 1


    logger.debug("Validation successful\n\n")

    return 0


def create_debian_binary_file(debian_binary_file_path):
    "Create a deb debian-binary file with the package format version number." # noqa

    logger.info("Creating debian-binary")

    # Write "2.0\n" to debian-binary file
    with open(debian_binary_file_path, "w") as debian_binary_file:
        debian_binary_file.write("2.0\n")
    logger.debug("Writing to debian-binary complete")

    # Validate if debian-binary file is a valid ar entry file that
    # can be added to the deb file.
    if not validate_ar_entry("debian-binary", debian_binary_file_path):
        return 1

    return 0


def create_data_tar(manifest, files_dir, data_tar_file_path, tar_compression, tar_format):
    "Create a deb data.tar file from the specified manifest." # noqa

    global CONFIG

    log_debug_no_format(logger, "\n\n")
    logger.info("Creating data.tar")
    log_debug_no_format(logger, "")

    CONFIG.package_data_files_dict = manifest["data_files"]

    dest_file_paths_list = []
    dest_directory_paths_list = []
    normalized_package_data_files_dict = collections.OrderedDict()
    absolute_package_data_files_dict = collections.OrderedDict()

    # The procedure of creating data.tar requires preprocessing.
    # We generate a new absolute_package_data_files_dict from
    # package_data_files_dict that has absolute paths set for all path
    # values.
    # The new dict will also remove unneeded keys. It will also be
    # sorted so that shorter paths are added first to data.tar. Paths
    # cannot be added/updated again with different permissions if they
    # already exist in a tar. Duplicate values will also be detected
    # after paths are normalized including if they exist both as an
    # absolute path and also without the installation prefix.
    #
    # The absolute_package_data_files_dict is created according the following:
    # 1. Loop on the dest_file_path keys in the original package_data_files_dict:
    #   1. Find  absolute paths for the dest_file_path key values of package_data_files_dict
    #      while creating absolute_package_data_files_dict.
    #   2. Set absolute paths for the source field values of package_data_files_dict
    #      while creating absolute_package_data_files_dict if the
    #      "source" field exists. Resolve symlinks if "source_readlink"
    #      field also exists.
    #   3. If the "source" field exists, add the dest_file_absolute_path
    #      to dest_file_paths_list, otherwise add it to dest_directory_paths_list.
    #
    # 2. Loop on the dest_file_absolute_path copy of the absolute_package_data_files_dict:
    #   1. If "source" and "set_parent_perm" fields both exist, then
    #      add an entry for the parent path for the dest_file_absolute_path
    #      to the absolute_package_data_files_dict and dest_directory_paths_list.
    #      This is not required if the "source" field does not exist
    #      since the dest_file_absolute_path would have already been
    #      added to dest_directory_paths_list and its parent would
    #      automatically be added/created later.
    #   2. If "source" and "source_recurse" fields both exist and source
    #      is a directory, then recursively find every sub file under
    #      the source path and add an entry for it to the
    #      absolute_package_data_files_dict where key is the sub path
    #      of the sub file append to dest_file_absolute_path. Symlinks
    #      are not transversed. This is similar to how "dpkg-deb --build"
    #      works where dest_file_absolute_path acts as the prefix.
    #      The dest key values are not added to dest_file_paths_list
    #      since the parent directory structure for each file under
    #      the dest_file_absolute_path would already be intact when
    #      creating the data.tar.
    #   3. If "symlink_destinations" fields exist, then find the
    #      absolute path for every value in the list set and create
    #      temp symlink file for each
    #      symlink_destination_absolute_file_path -> dest_file_absolute_path
    #      as per deb policy and add an entry to the absolute_package_data_files_dict
    #      where the temp symlink file path is the "source" field and
    #      symlink_destination_absolute_file_path is the key and also add
    #      it to dest_file_paths_list.

    i = 1
    # For all dest_file_path, dest_file_info in package_data_files_dict
    for dest_file_path, dest_file_info in CONFIG.package_data_files_dict.items():

        # If dest_file_path is null or "ignore" field exists in dest_file_info and is true, then ignore
        if dest_file_path is None or \
                ("ignore" in dest_file_info and dest_file_info["ignore"]):
            logger.debug("Ignoring destination file " + str(i) + " \"" + dest_file_path + "\"\n")
            i += 1
            continue
        # Else if is set and not empty, then normalize it
        elif dest_file_path:
            dest_file_normalized_path = normalize_path(dest_file_path)
        # Else if empty, set it to installation_prefix
        else:
            dest_file_normalized_path = CONFIG.installation_prefix

        if not dest_file_normalized_path.startswith("/"):
            dest_file_absolute_path = CONFIG.installation_prefix + "/" + dest_file_normalized_path
        else:
            dest_file_absolute_path = dest_file_normalized_path

        logger.debug("Processing destination file " + str(i) + " \"" + dest_file_path + "\"")

        # If dest_file_path contains parent path references "../"
        if is_parent_path_reference_containing_path(dest_file_path):
            logger.error("data_files: destination file " + str(i) + " \"" + dest_file_path + "\" cannot contain parent path references '../'")
            return 1

        # If dest_file_path normalized form also exists in the package_data_files_dict
        if dest_file_normalized_path != dest_file_path and \
                dest_file_normalized_path in CONFIG.package_data_files_dict:
            logger.error("data_files: destination file " + str(i) + " \"" + dest_file_path + "\" \
has duplicate values in normalized form \"" + dest_file_normalized_path + "\" in the manifest")
            return 1


        logger.debug("dest_file_absolute_path: \"" + dest_file_absolute_path + "\"")



        # For all fields, values in dest_file_info
        for field, value in dest_file_info.copy().items():
            # If field is not in PACKAGE_DATA_FILES_ATTRIBUTES_AND_ACTIONS_LIST or
            # (if field in list and empty) or
            # if value is null
            if field not in PACKAGE_DATA_FILES_ATTRIBUTES_AND_ACTIONS_LIST or \
                (field in ["perm", "owner_uid", "owner_uname", "owner_gid", "owner_gname", "set_shebang"] and not value) or \
                    value is None:
                del dest_file_info[field]

        # If "source" field does not exist in dest_file_info
        if "source" not in dest_file_info:
            # If field is only to be used if "source" field exists
            for field in [
                    "is_conffile", "source_readlink", "source_recurse",
                    "source_ownership", "fix_perm", "set_shebang"]:
                if field in dest_file_info:
                    del dest_file_info[field]

        # If "source" field exists in dest_file_info
        if "source" in dest_file_info:
            source_file_path = dest_file_info["source"]

            # If source_file_path is set
            if source_file_path:
                # If files_dir is set and source_file_path is not an absolute path, then
                # prefix source_file_path with files_dir
                if files_dir and not source_file_path.startswith("/"):
                    source_file_path = files_dir + "/" + source_file_path

                # Find the abspath of source_file_path and normalize it
                # without following symlinks symlinks are not followed
                # automatically so that symlink files are added to data.tar
                # instead of their target file, unless "source_readlink"
                # is passed this would also resolve parent path references "../"
                source_file_path = normalize_path(source_file_path)
            # Else if empty
            else:
                # Set source_file_path to files_dir if its set,
                # otherwise set it to current working directory
                source_file_path = files_dir or os.getcwd()


            logger.debug("source_file_path: \"" + source_file_path + "\"")

            # If "source_readlink" field exists in dest_file_info and
            # is true and source_file_path is a symlink
            if "source_readlink" in dest_file_info and \
                    dest_file_info["source_readlink"] and \
                    os.path.islink(source_file_path):

                # If source_file_path does not exist
                # os.path.exists returns false for broken symlinks
                if not os.path.exists(source_file_path):
                    if "ignore_if_no_exist" in dest_file_info and dest_file_info["ignore_if_no_exist"]:
                        logger.debug("Ignoring destination file " + str(i) + " \"" + dest_file_path + "\" \
since source file \"" + source_file_path + "\" symlink is broken\n")
                        i += 1
                        continue
                    else:
                        logger.error("data_files: destination file " + str(i) + " \"" + dest_file_path + "\" \
source file \"" + source_file_path + "\" symlink is broken")
                        return 1

                # Find realpath of source_file
                source_file_path = os.path.realpath(source_file_path)
                logger.debug("source_file_realpath: \"" + source_file_path + "\"")
            else:
                if "source_readlink" in dest_file_info:
                    del dest_file_info["source_readlink"]

            # Validate if source_file_path exists and is a symlink, regular file or directory
            (return_value, source_file_type) = \
                validate_and_get_file_type("source", source_file_path)
            if str(return_value) != "0":
                return return_value

            # If source_file_path is not a symlink, regular file or directory
            if not source_file_type:
                if "ignore_if_no_exist" in dest_file_info and dest_file_info["ignore_if_no_exist"]:
                    logger.debug("Ignoring destination file " + str(i) + " \"" + dest_file_path + "\" \
since source file \"" + source_file_path + "\" does not exist and/or must be a symlink, regular file or directory\n")
                    i += 1
                    continue
                else:
                    logger.error("data_files: destination file " + str(i) + " \"" + dest_file_path + "\" \
source file \"" + source_file_path + "\" does not exist and/or must be a symlink, regular file or directory")
                    return 1

            # If source_file is not a directory
            if source_file_type != FileType.DIRECTORY:
                # Only directories can be recursed
                for field in ["source_recurse"]:
                    if field in dest_file_info:
                        del dest_file_info[field]

            # If source_file is not a regular file
            if source_file_type != FileType.REGULAR:
                # Only regular files can be conffiles and have their shebang set
                for field in ["is_conffile", "set_shebang"]:
                    if field in dest_file_info:
                        del dest_file_info[field]

            # Update dest_file_info "source" field
            dest_file_info["source"] = source_file_path

            # If "source_ownership" field exists in dest_file_info and is true
            source_ownership_dict = {}
            ownership_string = ""
            if "source_ownership" in dest_file_info and dest_file_info["source_ownership"]:
                # Use the ownership of the source file on the host system
                (return_value, owner_uid, owner_uname, owner_gid, owner_gname) = \
                    get_file_ownership_tuple("source", source_file_path)
                if str(return_value) != "0":
                    return return_value

                ownership_string = get_ownership_string_from_tupple(
                    (owner_uid, owner_uname, owner_gid, owner_gname), True, " ")

                # If old manifest format and ownership variables are invalid
                if CONFIG.old_manifest_format and not validate_debian_ownership_tuple(
                        "destination file " + str(i) + " \"" + dest_file_path + "\" \
source file \"" + source_file_path + "\"", None,
                        (owner_uid, owner_uname, owner_gid, owner_gname), True, False):
                    logger.debug("Ignoring \"source_ownership\" \"" + ownership_string + "\" since its not compliant with debian policy.")
                else:
                    dest_file_info["owner_uid"] = owner_uid
                    dest_file_info["owner_uname"] = owner_uname
                    dest_file_info["owner_gid"] = owner_gid
                    dest_file_info["owner_gname"] = owner_gname

            # Add dest_file_absolute_path entry to dest_file_paths_list
            # so that its missing parent branches can be added later
            dest_file_paths_list.append(dest_file_absolute_path)
        else:
            # Add dest_file_absolute_path entry to dest_directory_paths_list
            # so that its missing parent branches can be added later
            dest_directory_paths_list.append(dest_file_absolute_path)


        # Add dest_file_info "dest_normalized" field
        dest_file_info["dest_normalized"] = dest_file_normalized_path

        # Add a dummy entry to normalized_package_data_files_dict for
        # the dest_file_normalized_path
        normalized_package_data_files_dict[dest_file_normalized_path] = {}

        # Add an entry to absolute_package_data_files_dict for the dest_file_absolute_path
        absolute_package_data_files_dict[dest_file_absolute_path] = dest_file_info

        log_debug_no_format(logger, "")

        i += 1


    i = 1
    # For all dest_file_absolute_path, dest_file_info in absolute_package_data_files_dict
    # we use absolute_package_data_files_dicts so that we can get
    # absolute paths for dest_file_path we use a copy since we only
    # need to loop on entries of the previous loop and moreover, we
    # cannot modify a dict inside its own for loop.
    for dest_file_absolute_path, dest_file_info in absolute_package_data_files_dict.copy().items():

        dest_file_normalized_path = dest_file_info["dest_normalized"]

        # If "source" field exists in dest_file_info and is set
        if "source" in dest_file_info and dest_file_info["source"]:

            source_file_path = dest_file_info["source"]

            # If "set_parent_perm" field exists in dest_file_info and
            # is true and source_file_path is a directory we do not do
            # the following if source_file_path is not a directory
            # since directory and regular file permissions must not be
            # mixed together and a regular file/symlink permission must
            # not be set to the dest_file_absolute_parent_path directory,
            # whether from the "perm" field or from the host system.
            if "set_parent_perm" in dest_file_info and \
                    dest_file_info["set_parent_perm"] and \
                    os.path.isdir(source_file_path):
                dest_file_normalized_parent_path = os.path.dirname(dest_file_normalized_path)
                dest_file_absolute_parent_path = os.path.dirname(dest_file_absolute_path)

                # If dest_file_absolute_parent_path does not already
                # exist in the absolute_package_data_files_dict and
                # dest_file_absolute_path does not equal "/"
                if dest_file_absolute_parent_path not in absolute_package_data_files_dict \
                        and dest_file_absolute_path != "/":
                    logger.debug("Processing destination file " + str(i) + " \"" + dest_file_absolute_path + "\" \
source file destination parent directory")

                    # If "perm" field exists in dest_file_info
                    if "perm" in dest_file_info and dest_file_info["perm"]:
                        # Use the "perm" field value
                        perm = dest_file_info["perm"]
                        perm_log = perm
                    else:
                        # Use the permission of the source file on the host system
                        (return_value, perm) = get_file_permission_octal("source", source_file_path)
                        if str(return_value) != "0":
                            return return_value
                        orig_perm = perm

                        # If fixing perm is enabled globally and for file
                        if should_fix_perm(dest_file_info):
                            (return_value, perm) = dh_and_android_fixperms(
                                "source file destination parent directory",
                                dest_file_absolute_parent_path, FileType.DIRECTORY, perm)
                            if str(return_value) != "0":
                                return return_value

                        if orig_perm != perm:
                            perm_log = orig_perm + " -> " + perm
                        else:
                            perm_log = perm

                    logger.debug("Adding \"data_files\" dict entry: \"" + dest_file_absolute_parent_path + "\" (" + str(perm_log) + ")")

                    # Add dest_file_absolute_parent_path entry to dest_directory_paths_list
                    # so that its missing parent branches can be added later
                    dest_directory_paths_list.append(dest_file_absolute_parent_path)

                    # Add a dummy entry to normalized_package_data_files_dict
                    # for the dest_file_normalized_parent_path
                    normalized_package_data_files_dict[dest_file_normalized_parent_path] = {}

                    # Add an entry to absolute_package_data_files_dict
                    # for the dest_file_absolute_parent_path with the
                    # the "perm" and "set_parent_perm" fields
                    absolute_package_data_files_dict[dest_file_absolute_parent_path] = {"perm": perm, "set_parent_perm": True}

                    log_debug_no_format(logger, "")



            # If "source_recurse" field exists in dest_file_info and
            # is true and source_file_path is a directory
            if "source_recurse" in dest_file_info and \
                    dest_file_info["source_recurse"] and \
                    os.path.isdir(source_file_path):
                source_sub_file_paths_list = []

                # Recursively get all sub files under source_file_path into source_sub_file_paths_list
                (return_value, source_sub_file_paths_list) = \
                    get_sub_file_paths_list_under_directory(
                        "data_files: destination file " + str(i) + " \"" + dest_file_absolute_path + "\" \
source file", source_file_path, False)
                if str(return_value) != "0":
                    return return_value

                # Sort the source_sub_file_paths_list so that package_data_files_dict fields are created in order
                source_sub_file_paths_list.sort()

                logger.debug("Recursing destination file " + str(i) + " \"" + dest_file_absolute_path + "\" \
source file sub files")

                # logger.debug("source_sub_file_paths_list =\n\"\n" + str(source_sub_file_paths_list) + "\n\"")

                # For all j, source_sub_file_path in source_sub_file_paths_list
                for j, source_sub_file_path in enumerate(source_sub_file_paths_list):

                    # If source_sub_file_path is null or empty, then ignore
                    if not source_sub_file_path:
                        continue

                    # Remove source_file_path prefix from source_sub_file_path if it exists
                    source_sub_file_path_without_prefix = normalize_path(source_sub_file_path)
                    if source_sub_file_path_without_prefix.startswith(source_file_path + "/"):
                        source_sub_file_path_without_prefix = source_sub_file_path_without_prefix.replace(source_file_path + "/", "", 1)

                    # Prefix source_sub_file_path_without_prefix with
                    # dest_file_absolute_path since that is the full
                    # destination path on the target system
                    dest_sub_file_normalized_path = normalize_path(
                        dest_file_normalized_path + "/" + source_sub_file_path_without_prefix)
                    dest_sub_file_absolute_path = normalize_path(
                        dest_file_absolute_path + "/" + source_sub_file_path_without_prefix)

                    logger.debug("Processing source sub file " + str(j + 1) + " \"" + source_sub_file_path + "\"")

                    # Validate if source_sub_file_path exists and is a
                    # symlink, regular file or directory
                    (return_value, source_sub_file_type) = validate_and_get_file_type("source sub", source_sub_file_path)
                    if str(return_value) != "0":
                        return return_value

                    # If source_sub_file_type is not a symlink,
                    # regular file or directory, then skip it.
                    if not source_sub_file_type:
                        logger.debug("Skipping since its not a symlink, regular file or directory")
                        continue

                    # If dest_sub_file_absolute_path already exists in
                    # the absolute_package_data_files_dict.
                    if dest_sub_file_absolute_path in absolute_package_data_files_dict:
                        dest_sub_file_info = absolute_package_data_files_dict[dest_sub_file_absolute_path]

                        # If "source" field exists in dest_sub_file_info
                        # and is equal to the current source_sub_file_path
                        # this is done in case "source_recurse" is set
                        # but user wants to set specific attributes to
                        # a sub file manually.
                        if "source" in dest_sub_file_info and dest_sub_file_info["source"] == source_sub_file_path:
                            logger.debug("Skipping since its destination \"" + dest_sub_file_absolute_path + "\" already exists as a destination \
file in the manifest for the same source file")
                            continue
                        else:
                            logger.error("data_files: destination file " + str(i) + " \"" + dest_file_absolute_path + "\" recursive source file \
" + str(j + 1) + " \"" + source_sub_file_path + "\" destination \"" + dest_sub_file_absolute_path + "\" already exists as a destination file \
in the manifest")
                            return 1

                    # Use the permission of the source sub file on the host system
                    (return_value, perm) = get_file_permission_octal("source sub", source_sub_file_path)
                    if str(return_value) != "0":
                        return return_value
                    orig_perm = perm

                    # If fixing perm is enabled globally and for file
                    if should_fix_perm(dest_file_info):
                        (return_value, perm) = dh_and_android_fixperms(
                            "source sub", dest_sub_file_absolute_path,
                            source_sub_file_type, perm)
                        if str(return_value) != "0":
                            return return_value

                    if orig_perm != perm:
                        perm_log = orig_perm + " -> " + perm
                    else:
                        perm_log = perm

                    # If "source_ownership" field exists in dest_file_info and is true
                    source_ownership_dict = {}
                    ownership_string = ""
                    if "source_ownership" in dest_file_info and dest_file_info["source_ownership"]:
                        # Use the ownership of the source sub file on the host system
                        (return_value, owner_uid, owner_uname, owner_gid, owner_gname) = \
                            get_file_ownership_tuple("source sub", source_sub_file_path)
                        if str(return_value) != "0":
                            return return_value

                        ownership_string = get_ownership_string_from_tupple(
                            (owner_uid, owner_uname, owner_gid, owner_gname), True, " ")

                        # If ownership variables are invalid
                        if not validate_debian_ownership_tuple(
                                "destination file " + str(i) + " \"" + dest_file_absolute_path + "\" recursive source file \
" + str(j + 1) + " \"" + source_sub_file_path + "\"", None,
                                (owner_uid, owner_uname, owner_gid, owner_gname), True, False):
                            logger.debug("Ignoring \"source_ownership\" \"" + ownership_string + "\" since its not compliant with debian policy.")
                            ownership_string = ""
                        else:
                            source_ownership_dict["owner_uid"] = owner_uid
                            source_ownership_dict["owner_uname"] = owner_uname
                            source_ownership_dict["owner_gid"] = owner_gid
                            source_ownership_dict["owner_gname"] = owner_gname

                    logger.debug("Adding \"data_files\" dict entry: \"" + dest_sub_file_absolute_path + "\" (" + str(perm_log) + ")" + ownership_string)

                    # Add a dummy entry to normalized_package_data_files_dict
                    # for the dest_sub_file_normalized_path
                    normalized_package_data_files_dict[dest_sub_file_normalized_path] = {}

                    # Add an entry to absolute_package_data_files_dict
                    # for the dest_sub_file_absolute_path with the
                    # "source" field set to sub file of source file
                    # at source_sub_file_path and the "perm" field
                    absolute_package_data_files_dict[dest_sub_file_absolute_path] = \
                        {"source": source_sub_file_path, "perm": perm}

                    if source_ownership_dict:
                        absolute_package_data_files_dict[dest_sub_file_absolute_path].update(source_ownership_dict)

                    # If "fix_perm" field exists in dest_file_info
                    if "fix_perm" in dest_file_info:
                        absolute_package_data_files_dict[dest_sub_file_absolute_path]["fix_perm"] = \
                            dest_file_info["fix_perm"]

                    log_debug_no_format(logger, "")



        # If "symlink_destinations" field exists in dest_file_info and is set
        if "symlink_destinations" in dest_file_info and dest_file_info["symlink_destinations"]:

            logger.debug("Processing destination file " + str(i) + " \"" + dest_file_absolute_path + "\" \
symlink destinations")

            symlink_destination_file_paths_list = dest_file_info["symlink_destinations"]
            # For all j, symlink_destination_file_path in symlink_destination_file_paths_list
            for j, symlink_destination_file_path in enumerate(symlink_destination_file_paths_list):

                # If symlink_destination_file_path is null, then ignore
                if symlink_destination_file_path is None:
                    continue
                # Else if is set and not empty, then normalize it
                elif symlink_destination_file_path:
                    symlink_destination_normalized_file_path = normalize_path(symlink_destination_file_path)
                # Else if empty, set it to installation_prefix
                else:
                    symlink_destination_normalized_file_path = CONFIG.installation_prefix

                if not symlink_destination_normalized_file_path.startswith("/"):
                    symlink_destination_absolute_file_path = CONFIG.installation_prefix + "/" + symlink_destination_normalized_file_path
                else:
                    symlink_destination_absolute_file_path = symlink_destination_normalized_file_path

                # If symlink_destination_file_path contains parent path references "../"
                if is_parent_path_reference_containing_path(symlink_destination_file_path):
                    logger.error("data_files: destination file " + str(i) + " \"" + dest_file_absolute_path + "\" \
symlink destination " + str(j + 1) + " \"" + symlink_destination_file_path + "\" cannot contain parent path references '../'")
                    return 1

                # If symlink_destination_absolute_file_path already
                # exists in the absolute_package_data_files_dict
                if symlink_destination_absolute_file_path in absolute_package_data_files_dict:
                    logger.error("data_files: destination file " + str(i) + " \"" + dest_file_absolute_path + "\" \
symlink destination " + str(j + 1) + " \"" + symlink_destination_absolute_file_path + "\" already exists as a destination file in the manifest")
                    return 1

                # Update dest_file_info "symlink_destinations" field
                # of absolute_package_data_files_dict
                absolute_package_data_files_dict[dest_file_absolute_path]["symlink_destinations"][j] = symlink_destination_absolute_file_path

                # Create temp symlink from
                # symlink_destination_absolute_file_path -> dest_file_absolute_path
                # at get its path in source_file_path
                (return_value, source_file_path) = make_symlink(
                    symlink_destination_absolute_file_path, dest_file_absolute_path)
                if str(return_value) != "0":
                    return return_value

                # Symlinks normally have "777" permission
                perm = "777"
                logger.debug("Adding \"data_files\" dict entry: \"" + symlink_destination_absolute_file_path + "\" (" + str(perm) + ")")

                # Add symlink_destination_absolute_file_path entry to
                # dest_file_paths_list so that its missing parent
                # branches can be added later.
                dest_file_paths_list.append(symlink_destination_absolute_file_path)

                # Add a dummy entry to normalized_package_data_files_dict
                # for the symlink_destination_normalized_file_path
                normalized_package_data_files_dict[symlink_destination_normalized_file_path] = {}

                # Add an entry to absolute_package_data_files_dict for
                # the symlink_destination_absolute_file_path with the
                # "source" field set to the temp symlink file generated
                # at source_file_path and the "perm" field.
                absolute_package_data_files_dict[symlink_destination_absolute_file_path] = {"source": source_file_path, "perm": perm}


                log_debug_no_format(logger, "")

        i += 1



    i = 1
    # For all dest_file_normalized_path, dest_file_info in
    # normalized_package_data_files_dict check if same path exists as
    # an absolute path and also without the installation prefix
    for dest_file_normalized_path, dest_file_info in normalized_package_data_files_dict.items():
        if not dest_file_normalized_path.startswith("/"):
            dest_file_absolute_path = CONFIG.installation_prefix + "/" + dest_file_normalized_path
            if dest_file_absolute_path in normalized_package_data_files_dict:
                logger.error("data_files: destination file " + str(i) + " \"" + dest_file_absolute_path + "\" \
exists both as an absolute path and also without the installation prefix \"" + CONFIG.installation_prefix + "\" in the manifest")
                return 1

        i += 1



    # Set the new absolute_package_data_files_dict back to package_data_files_dict
    CONFIG.package_data_files_dict = absolute_package_data_files_dict



    # If dest_directory_paths_list is set
    if dest_directory_paths_list:
        logger.debug("Processing dest_directory_paths_list =\n\"\n" + str(dest_directory_paths_list) + "\n\"")

        # Add all dest_directory_path_branches in each dest_directory_paths_list item
        # to package_data_files_dict that were not already in it
        for dest_directory_path in dest_directory_paths_list:

            dest_file_info = CONFIG.package_data_files_dict[dest_directory_path]

            # logger.debug("dest_directory_path: \"" + dest_directory_path + "\"")
            dest_directory_path_branches = get_branches_of_path(dest_directory_path)
            # logger.debug("dest_directory_path_branches =\n\"\n" + str(dest_directory_path_branches) + "\n\"")

            for dest_directory_path_branch in dest_directory_path_branches:
                # If dest_directory_path_branch not already in package_data_files_dict
                if dest_directory_path_branch not in CONFIG.package_data_files_dict:

                    # If "perm" and "set_parent_perm" fields exists
                    # in dest_file_info and set_parent_perm is true
                    if ("perm" in dest_file_info and dest_file_info["perm"]) and \
                            ("set_parent_perm" in dest_file_info and dest_file_info["set_parent_perm"]):
                        # Use the "perm" field value
                        perm = dest_file_info["perm"]
                    else:
                        # Use android specific or default permission
                        perm = check_and_get_android_specific_directory_perm(dest_directory_path_branch)

                    logger.debug("Adding \"data_files\" dict entry: \"" + dest_directory_path_branch + "\" (" + str(perm) + ")")

                    # Add an entry to package_data_files_dict for the
                    # dest_directory_path_branch with the "perm" field
                    CONFIG.package_data_files_dict[dest_directory_path_branch] = {"perm": perm}

        log_debug_no_format(logger, "")



    # Find all unique parent paths of data_files to be added to data.tar
    # that do not have any parents and create entries for them in
    # package_data_files_dict so that correct metadata is set as per debian policy
    parent_paths_list = get_unique_parent_paths_list(dest_file_paths_list)

    # If parent_paths_list is set
    if parent_paths_list:

        # Remove duplicates and paths already in dest_directory_paths_list
        parent_paths_list = list(set(parent_paths_list) - set(dest_directory_paths_list))
        logger.debug("Processing parent_paths_list =\n\"\n" + str(parent_paths_list) + "\n\"")

        # Add all parent_path_branches in each parent_paths_list item
        # to package_data_files_dict that were not already in it
        for parent_path in parent_paths_list:

            # logger.debug("parent_path: \"" + parent_path + "\"")
            parent_path_branches = get_branches_of_path(parent_path)
            # logger.debug("parent_path_branches =\n\"\n" + str(parent_path_branches) + "\n\"")

            for parent_path_branch in parent_path_branches:
                # If parent_path_branch not already in package_data_files_dict
                if parent_path_branch not in CONFIG.package_data_files_dict:
                    # Use android specific or default permission
                    perm = check_and_get_android_specific_directory_perm(parent_path_branch)

                    logger.debug("Adding \"data_files\" dict entry: \"" + parent_path_branch + "\" (" + str(perm) + ")")

                    # Add an entry to package_data_files_dict for the parent_path_branch with the "perm" field
                    CONFIG.package_data_files_dict[parent_path_branch] = {"perm": perm}

        log_debug_no_format(logger, "")



    # Sort package_data_files_dict so that shorter paths are added first
    CONFIG.package_data_files_dict = collections.OrderedDict(sorted(CONFIG.package_data_files_dict.items()))
    logger.debug("package_data_files_dict =\n\"\n" + json.dumps(CONFIG.package_data_files_dict, indent=4) + "\n\"")



    # Open a data_tar_file at data_tar_file_path with write mode and
    # tar_compression and tar_format
    with tarfile.open(data_tar_file_path, mode="w:" + tar_compression, format=tar_format) as data_tar_file:

        already_added_paths = []
        i = 1
        # For all dest_file_path, dest_file_info in package_data_files_dict
        for dest_file_path, dest_file_info in CONFIG.package_data_files_dict.items():

            logger.debug("Processing destination file " + str(i))

            # Validate if dest_file_path is a valid path as per debian policy
            if not validate_data_tar_path("destination file " + str(i), dest_file_path):
                return 1

            # If dest_file_path has already been added to the data.tar
            if dest_file_path in already_added_paths:
                logger.error("destination file " + str(i) + " \"" + dest_file_path + "\" has already been added \
data.tar and cannot be added again.")
                return 1

            # If "source" field exists in dest_file_info and is set
            if "source" in dest_file_info and dest_file_info["source"]:
                source_file_path = dest_file_info["source"]

                logger.debug("source_file_path: \"" + source_file_path + "\"")

                # Validate if source_file_path exists and is a symlink, regular file or directory
                (return_value, source_file_type) = validate_and_get_file_type("source", source_file_path)
                if str(return_value) != "0":
                    return return_value

                # If source_file_path is not a symlink, regular file or directory
                if not source_file_type:
                    logger.error("source file \"" + source_file_path + "\" for destination file " + str(i) + " \
\"" + dest_file_path + "\" does not exist and/or must be a symlink, regular file or directory")
                    return 1

                # If dest_file_path will be a regular file or symlink, then any paths must not exist under it
                # tar.add does allow duplicate file and directory entries with the same basename
                if source_file_type in (FileType.SYMLINK, FileType.REGULAR):
                    if not validate_subpaths_do_not_exist_under_file_path("destination file " + str(i) + " is a \
" + source_file_type + " but destination file paths exist under it", dest_file_path, list(CONFIG.package_data_files_dict.keys())):
                        return 1

                # If source_file is a regular file, then find its size
                # and md5hash and perform any actions required
                # directories and symlinks are not to be added to
                # md5sums file and do not contribute to "Installed-Size"
                # field and any actions are not performed on them.
                if source_file_type == FileType.REGULAR:
                    # Get file size and md5hash
                    file_size_in_bytes = os.path.getsize(source_file_path)

                    (return_value, file_md5hash) = get_file_md5hash("source", source_file_path)
                    if str(return_value) != "0":
                        return return_value

                    logger.debug("source_file_size_in_bytes: \"" + str(file_size_in_bytes) + "\"")
                    logger.debug("source_file_md5hash: \"" + file_md5hash + "\"")

                    create_source_file_copy = False

                    # If dest_file_info contains any field in the list and is set
                    for file_action_field in ["set_shebang"]:
                        if file_action_field in dest_file_info and dest_file_info[file_action_field]:
                            create_source_file_copy = True
                            break

                    # If file at source_file_path is a hardlink
                    if is_hardlink(source_file_path):
                        create_source_file_copy = True

                    # If create_source_file_copy is true
                    if create_source_file_copy:
                        # Create a temp copy of file at source_file_path
                        (return_value, source_file_path) = create_temp_copy_of_file("source", source_file_path)
                        if str(return_value) != "0":
                            return return_value
                        logger.debug("updated_source_file_path: \"" + source_file_path + "\"")

                        # If "set_shebang" field exists in dest_file_info
                        if "set_shebang" in dest_file_info and dest_file_info["set_shebang"]:
                            # Replace shebang of source file if it exists with the "set_shebang" field value
                            return_value = replace_shebang_in_file("source", dest_file_info["set_shebang"], source_file_path)
                            if str(return_value) != "0":
                                return return_value

                        # Get updated file size and md5hash
                        file_size_in_bytes = os.path.getsize(source_file_path)

                        (return_value, file_md5hash) = get_file_md5hash("source", source_file_path)
                        if str(return_value) != "0":
                            return return_value

                        logger.debug("updated_source_file_size_in_bytes: \"" + str(file_size_in_bytes) + "\"")
                        logger.debug("updated_source_file_md5hash: \"" + file_md5hash + "\"")

                    # Add size of current source_file to installed_size so
                    # that the final cumulative size can be added to the
                    # "control" file "Installed-Size" field.
                    file_size_in_kilobytes = math.ceil(file_size_in_bytes / 1024)
                    CONFIG.installed_size += file_size_in_kilobytes

                    # Add entry of dest_file_path to md5sums_file_content
                    # in the format "md5sum  path\n" to be added later to
                    # the "md5sums" file.
                    dest_file_path_for_md5sums_file = dest_file_path
                    if dest_file_path_for_md5sums_file.startswith("/"):
                        dest_file_path_for_md5sums_file = dest_file_path_for_md5sums_file[1:]
                    CONFIG.md5sums_file_content += file_md5hash + "  " + dest_file_path_for_md5sums_file + "\n"

                    # If "is_conffile" field exists in dest_file_info, then
                    # add entry of dest_file_path to conffiles_file_content
                    # in the format "path\n" to be added later to
                    # the "conffiles" file.
                    # The conffile must be a regular file and not a symlink since that is not officially supported
                    # and can result in unpredictable behaviour, directories are not supported either.
                    if "is_conffile" in dest_file_info and dest_file_info["is_conffile"]:
                        # If dest_file_path contains a newline "\n"
                        if "\n" in dest_file_path:
                            logger.error("destination file " + str(i) + " \"" + dest_file_path + "\" contains a newline \
which is not allowed for a conffile path")
                            return 1

                        # Validate if conffile_path is a valid path as per debian policy
                        if not validate_conffile_path("destination file " + str(i), dest_file_path):
                            return False

                        CONFIG.conffiles_file_content += dest_file_path + "\n"

                # Add file at source_file_path at dest_file_path in data.tar file
                # Call set_package_data_file_metadata function via a filter so that it
                # sets proper metadata.

                # Set package_data_file_* global variables
                # to be used by the set_package_data_file_metadata function.

                # Use the mtime of the source file on the host system.
                CONFIG.package_data_file_mtime = None

                # Set package_data_file_perm
                # If "perm" field exists in dest_file_info
                if "perm" in dest_file_info and dest_file_info["perm"]:
                    # Use the "perm" field value
                    perm = dest_file_info["perm"]
                    perm_log = perm
                else:
                    # Use the permission of the source file on the host system
                    (return_value, perm) = get_file_permission_octal("source", source_file_path)
                    if str(return_value) != "0":
                        return return_value
                    orig_perm = perm

                    # If fixing perm is enabled globally and for file
                    if should_fix_perm(dest_file_info):
                        (return_value, perm) = dh_and_android_fixperms(
                            "source", dest_file_path, source_file_type, perm)
                        if str(return_value) != "0":
                            return return_value

                    if orig_perm != perm:
                        perm_log = orig_perm + " -> " + perm
                    else:
                        perm_log = perm

                CONFIG.package_data_file_perm = perm

                # If package_data_file_perm is invalid
                if not validate_file_permission("destination file " + str(i) + " \"" + dest_file_path + "\" \"perm\"", CONFIG.package_data_file_perm):
                    return 1

                # Set package_data_file_* ownership variables
                (  # pylint: disable=unbalanced-tuple-unpacking
                    CONFIG.package_data_file_uid, CONFIG.package_data_file_uname,
                    CONFIG.package_data_file_gid, CONFIG.package_data_file_gname
                ) = get_ownership_tupple_from_dict(dest_file_info)

                # If package_data_file_* ownership variables are invalid
                if not validate_debian_ownership_tuple(
                        "destination file " + str(i) + " \"" + dest_file_path + "\"", None,
                        (CONFIG.package_data_file_uid, CONFIG.package_data_file_uname,
                         CONFIG.package_data_file_gid, CONFIG.package_data_file_gname), True):
                    return 1

                ownership_string = get_ownership_string_from_tupple(
                    (CONFIG.package_data_file_uid, CONFIG.package_data_file_uname,
                     CONFIG.package_data_file_gid, CONFIG.package_data_file_gname), True, " ")

                logger.info("Adding " + source_file_type + ": \"" + dest_file_path + "\"" + " (" + perm_log + ")" + ownership_string)
                data_tar_file.add(source_file_path, arcname="." + dest_file_path, recursive=False, filter=set_package_data_file_metadata)



            # Else if "source" field does not exist in dest_file_info
            # and only an empty directory needs to be added.
            # dest_directory_path_branches and parent_path_branches
            # loops would also have added entries if they were not
            # already in the manifest.
            else:

                # Add a directory at dest_file_path in data.tar file
                # Call set_package_data_file_metadata function directly
                # so that it sets proper metadata to tarfile.TarInfo object.
                dest_directory_path_file_info = tarfile.TarInfo(name="." + dest_file_path)
                dest_directory_path_file_info.type = tarfile.DIRTYPE

                # Set package_data_file_* global variables
                # to be used by the set_package_data_file_metadata function

                # Use the current time as mtime
                CONFIG.package_data_file_mtime = time.time()

                # Set package_data_file_perm
                # If "perm" field exists in dest_file_info
                if "perm" in dest_file_info and dest_file_info["perm"]:
                    # Use the "perm" field value
                    perm = dest_file_info["perm"]
                else:
                    # Use android specific or default permission
                    perm = check_and_get_android_specific_directory_perm(dest_file_path)

                CONFIG.package_data_file_perm = perm

                # If package_data_file_perm is invalid
                if not validate_file_permission("destination file " + str(i) + " \"" + dest_file_path + "\" \"perm\"", CONFIG.package_data_file_perm):
                    return 1

                # Set package_data_file_* ownership variables
                (  # pylint: disable=unbalanced-tuple-unpacking
                    CONFIG.package_data_file_uid, CONFIG.package_data_file_uname,
                    CONFIG.package_data_file_gid, CONFIG.package_data_file_gname
                ) = get_ownership_tupple_from_dict(dest_file_info)

                # If package_data_file_* ownership variables are invalid
                if not validate_debian_ownership_tuple(
                        "destination file " + str(i) + " \"" + dest_file_path + "\"", None,
                        (CONFIG.package_data_file_uid, CONFIG.package_data_file_uname,
                         CONFIG.package_data_file_gid, CONFIG.package_data_file_gname), True):
                    return 1

                ownership_string = get_ownership_string_from_tupple(
                    (CONFIG.package_data_file_uid, CONFIG.package_data_file_uname,
                     CONFIG.package_data_file_gid, CONFIG.package_data_file_gname), True, " ")

                logger.info("Adding directory: \"" + dest_file_path + "\" (" + CONFIG.package_data_file_perm + ")" + ownership_string)
                set_package_data_file_metadata(dest_directory_path_file_info)
                data_tar_file.addfile(tarinfo=dest_directory_path_file_info)

            already_added_paths.append(dest_file_path)
            log_debug_no_format(logger, "\n")

            i += 1

        logger.debug("Adding data files complete\n\n")


        logger.debug("Writing to data.tar complete")



    # Validate if data.tar file is a valid ar entry file that can be
    # added to the deb file.
    if not validate_ar_entry("data.tar", data_tar_file_path):
        return 1

    return 0


def create_control_tar(manifest, files_dir, control_files_dir, data_tar_file_path, control_tar_file_path, tar_compression, tar_format):
    "Create a deb control.tar file from the specified manifest." # noqa

    global CONFIG

    log_debug_no_format(logger, "\n\n")
    logger.info("Creating control.tar")
    log_debug_no_format(logger, "")

    control = manifest["control"]

    # If "Installed-Size" field exists in the control but is not a
    # valid integer, then remove it.
    if "Installed-Size" in control and not str(control["Installed-Size"]).isdigit():
        logger.warning("Removing invalid \"Installed-Size\" field from manifest \"control\" dict")
        del manifest["control"]["Installed-Size"]

    # If "Installed-Size" is not already in the control and was set
    # by the create_data_tar function and is a valid integer.
    if "Installed-Size" not in control and isinstance(CONFIG.installed_size, int) \
            and str(CONFIG.installed_size).isdigit():
        # Add installed_size to manifest control
        manifest["control"]["Installed-Size"] = str(CONFIG.installed_size)



    # Add fields in the manifest control that are not in
    # PACKAGE_CONTROL_FILE_BUILD_AND_INSTALL_FIELDS_LIST,
    # PACKAGE_CONTROL_FILE_RELATIONSHIP_FIELDS_LIST and
    # PACKAGE_CONTROL_FILE_HOME_AND_DESCRIPTION_FIELDS_LIST and
    # that do not start with "-" or "#" to package_control_file_optional_fields_list
    package_control_file_optional_fields_list = []
    for field, value in control.items():
        if field not in PACKAGE_CONTROL_FILE_BUILD_AND_INSTALL_FIELDS_LIST and \
                field not in PACKAGE_CONTROL_FILE_RELATIONSHIP_FIELDS_LIST and \
                field not in PACKAGE_CONTROL_FILE_HOME_AND_DESCRIPTION_FIELDS_LIST and \
                not re.match('^[-#]', field):
            package_control_file_optional_fields_list.append(field)

    # Define the final list of fields that will be added to the control
    # file in order if they exist.
    control_file_fields_list = []
    control_file_fields_list.extend(PACKAGE_CONTROL_FILE_BUILD_AND_INSTALL_FIELDS_LIST)
    control_file_fields_list.extend(PACKAGE_CONTROL_FILE_RELATIONSHIP_FIELDS_LIST)
    control_file_fields_list.extend(package_control_file_optional_fields_list)
    control_file_fields_list.extend(PACKAGE_CONTROL_FILE_HOME_AND_DESCRIPTION_FIELDS_LIST)
    # logger.debug("control_file_fields_list =\n\"\n" + str(control_file_fields_list) + "\n\"")



    # Add fields in control_file_fields_list to the control file if
    # they exist and are not null.
    control_file_content = ""
    for field in control_file_fields_list:
        if field in control and control[field]:
            value = control[field]
            # If field value is a list
            if isinstance(value, list):
                # If field exists in PACKAGE_CONTROL_FILE_RELATIONSHIP_FIELDS_LIST,
                # then join value with ", " and append it to control_file_content
                # this is done to maintain backward compatibility with
                # version '< 0.12.0' as well
                if field in PACKAGE_CONTROL_FILE_RELATIONSHIP_FIELDS_LIST:
                    control_file_content += field + ": " + ", ".join(map(str, value)) + "\n"
                # Else join value with newlines and append it to control_file_content
                else:
                    control_file_content += field + ": " + "\n".join(map(str, value)) + "\n"
            # Else convert value to string and append it to control_file_content
            else:
                control_file_content += field + ": " + str(value) + "\n"

    # If control_file_content is empty
    if not control_file_content:
        logger.error("The control file content cannot be empty")
        return 1



    # Open a control_tar_file at control_tar_file_path with write mode
    # and tar_compression and tar_format.
    with tarfile.open(control_tar_file_path, mode="w:" + tar_compression, format=tar_format) as control_tar_file:
        # Add control file to control_tar_file
        logger.info("Adding control file")
        logger.debug("control file =\n\"\n" + str(control_file_content) + "\n\"\n")

        (return_value, control_file, control_file_info) = create_tarinfo_obj_with_content("./control", control_file_content)
        if str(return_value) != "0":
            return return_value

        # Use the current time as mtime
        CONFIG.package_control_info_file_mtime = time.time()
        set_control_info_file_metadata(control_file_info)

        control_tar_file.addfile(fileobj=control_file, tarinfo=control_file_info)

        # Validate the control file
        # This shouldn't ideally be needed unless someone disabled/modified
        # validation or sanitizing of json manifest.
        # read the data written to control_file
        control_file.seek(0)
        control_file_content = control_file.read().decode("utf-8")
        # logger.debug("control file updated =\n\"\n" + str(control_file_content) + "\n\"\n")

        control_file_fields_list = []
        field_line_match_regex = re.compile("^([^:]+): .+")
        # For all lines in control_file_content
        i = 1
        for line in control_file_content.splitlines():
            # If line does not start with a space " " or tab "\t"
            if not line.startswith(" ") and not line.startswith("\t"):
                field_line_match_result = field_line_match_regex.match(line)
                # If the line does not start with one or more characters, followed by a colon ":",
                # followed by a space and followed by one or more characters
                if field_line_match_result is None:
                    logger.error("The control file line " + str(i) + ": \"" + line + "\" is not a valid field line \
and must be in the format \"name: value\"")
                    logger.error("control file =\n\"\n" + str(control_file_content) + "\n\"\n")
                    return 1

                # Find the field name characters before the first colon ":"
                field = field_line_match_result.group(1)

                # If field is not a valid control file field
                if not validate_control_file_field_name("The package control file field in the control file", field):
                    return 1
                # Add field to control_file_fields_list
                control_file_fields_list.append(field)
            # If line is empty or only contains whitespaces
            elif not line or line.isspace():
                logger.error("The control file line " + str(i) + ": \"" + line + "\" is not a valid multi-line value \
line and must at least contain a space followed by a dot for empty lines: \" .\"")
                logger.error("control file =\n\"\n" + str(control_file_content) + "\n\"\n")
                return 1

            i += 1

        # Check if control file contains duplicate fields
        # Control file field names are not case-sensitive
        # hence also convert to lowercase for detection of duplicates
        # that are of a different case.
        control_file_fields_list = [x.lower() for x in control_file_fields_list]
        control_file_fields_duplicate_list = set([x for x in control_file_fields_list if control_file_fields_list.count(x) > 1])  # pylint: disable=consider-using-set-comprehension
        if control_file_fields_duplicate_list:
            logger.error("The control file contains duplicate fields: " + str(control_file_fields_duplicate_list))
            logger.error("control file =\n\"\n" + str(control_file_content) + "\n\"\n")
            return 1

        log_debug_no_format(logger, "")



        # If md5sums_file_content is not empty and was set by the create_data_tar function
        if CONFIG.md5sums_file_content:
            # Add md5sums file to control_tar_file
            logger.info("Adding md5sums file")
            logger.debug("md5sums file =\n\"\n" + str(CONFIG.md5sums_file_content) + "\n\"")

            (return_value, md5sums_file, md5sums_file_info) = create_tarinfo_obj_with_content("./md5sums", CONFIG.md5sums_file_content)
            if str(return_value) != "0":
                return return_value

            # Use the current time as mtime
            CONFIG.package_control_info_file_mtime = time.time()
            set_control_info_file_metadata(md5sums_file_info)

            control_tar_file.addfile(fileobj=md5sums_file, tarinfo=md5sums_file_info)

            log_debug_no_format(logger, "\n")



        # If "maintainer_scripts_shebang" field exists in the manifest
        if "maintainer_scripts_shebang" in manifest and manifest["maintainer_scripts_shebang"]:
            maintainer_scripts_shebang = manifest["maintainer_scripts_shebang"]
        else:
            maintainer_scripts_shebang = None

        # For all maintainer_scripts in PACKAGE_MAINTAINER_SCRIPTS_LIST
        # https://www.debian.org/doc/debian-policy/ch-files.html#scripts
        for maintainer_script in PACKAGE_MAINTAINER_SCRIPTS_LIST:
            # If control_files_dir is defined, then prepend it to
            # path set in maintainer_script
            if control_files_dir:
                maintainer_script_path = control_files_dir + "/" + maintainer_script
            # If files_dir is defined, then prepend it to path set in maintainer_script
            elif files_dir:
                maintainer_script_path = files_dir + "/" + maintainer_script
            else:
                maintainer_script_path = maintainer_script

            # If script file exists at path set in maintainer_script_path
            if os.path.isfile(maintainer_script_path):
                logger.debug("Processing \"" + maintainer_script + "\"")
                logger.debug(maintainer_script + "_maintainer_script_path: \"" + maintainer_script_path + "\"")

                # If maintainer_scripts_shebang is set or file at
                # maintainer_script_path is a hardlink.
                if maintainer_scripts_shebang or is_hardlink(maintainer_script_path):
                    # Create a temp copy of maintainer_script file
                    (return_value, maintainer_script_path) = create_temp_copy_of_file(maintainer_script + "maintainer script", maintainer_script_path)
                    if str(return_value) != "0":
                        return return_value
                    logger.debug("updated_" + maintainer_script + "_maintainer_script_path: \"" + maintainer_script_path + "\"")

                    # If maintainer_scripts_shebang is set
                    if maintainer_scripts_shebang:
                        # Replace shebang of maintainer_script file if
                        # it exists with the maintainer_scripts_shebang value.
                        return_value = replace_shebang_in_file(maintainer_script + "maintainer script", maintainer_scripts_shebang, maintainer_script_path)
                        if str(return_value) != "0":
                            return return_value

                # Add maintainer_script file to control_tar_file, and
                # add set_maintainer_script_file_metadata function as
                # filter to set its metadata.
                logger.info("Adding " + maintainer_script + " file")
                control_tar_file.add(maintainer_script_path, arcname="./" + maintainer_script, recursive=False, filter=set_maintainer_script_file_metadata)

                log_debug_no_format(logger, "\n")



        # Create a copy of PACKAGE_OTHER_CONTROL_FILES_LIST
        package_other_control_files_list_copy = PACKAGE_OTHER_CONTROL_FILES_LIST[:]

        # If conffiles_file_content is not empty and was set by the create_data_tar function
        if CONFIG.conffiles_file_content:
            # Add conffiles file to control_tar_file
            logger.info("Adding conffiles file (manifest)")
            logger.debug("conffiles file =\n\"\n" + str(CONFIG.conffiles_file_content) + "\n\"")

            (return_value, conffiles_file, conffiles_file_info) = create_tarinfo_obj_with_content("./conffiles", CONFIG.conffiles_file_content)
            if str(return_value) != "0":
                return return_value

            # Use the current time as mtime
            CONFIG.package_control_info_file_mtime = time.time()
            set_control_info_file_metadata(conffiles_file_info)

            control_tar_file.addfile(fileobj=conffiles_file, tarinfo=conffiles_file_info)


            # Read the data written to conffiles_file
            conffiles_file.seek(0)
            CONFIG.conffiles_file_content = conffiles_file.read().decode("utf-8")
            # logger.debug("conffiles file updated =\n\"\n" + str(CONFIG.conffiles_file_content) + "\n\"\n")

            # Check if conffiles is valid and all entries in conffiles exist in data.tar
            if not validate_conffiles_file(CONFIG.conffiles_file_content, False, data_tar_file_path, tar_compression, tar_format):
                return 1

            # Remove "conffiles" from package_other_control_files_list_copy so that it is not added again
            package_other_control_files_list_copy.remove("conffiles")

            log_debug_no_format(logger, "\n")



        # For all other_control_files in package_other_control_files_list_copy
        for other_control_file in package_other_control_files_list_copy:
            # If control_files_dir is defined, then prepend it to
            # path set in other_control_file
            if control_files_dir:
                other_control_file_path = control_files_dir + "/" + other_control_file
            # If files_dir is defined, then prepend it to path set in other_control_file_path
            elif files_dir:
                other_control_file_path = files_dir + "/" + other_control_file
            else:
                other_control_file_path = other_control_file

            # If control file exists at path set in other_control_file_path
            if os.path.isfile(other_control_file_path):
                logger.debug("Processing \"" + other_control_file + "\"")
                logger.debug(other_control_file + "_control_file_path: \"" + other_control_file_path + "\"")

                create_other_control_file_copy = False

                # If current other_control_file is "conffiles" and "conffiles_prefix_to_replace" field exists in the manifest and is set
                if other_control_file == "conffiles" and "conffiles_prefix_to_replace" in manifest and manifest["conffiles_prefix_to_replace"]:
                    create_other_control_file_copy = True
                    conffiles_prefix_to_replace = manifest["conffiles_prefix_to_replace"]
                else:
                    conffiles_prefix_to_replace = None

                # If file at other_control_file_path is a hardlink
                if is_hardlink(other_control_file_path):
                    create_other_control_file_copy = True

                # If create_other_control_file_copy is true
                if create_other_control_file_copy:
                    # Create a temp copy of conffiles file
                    (return_value, other_control_file_path) = create_temp_copy_of_file("conffiles", other_control_file_path)
                    if str(return_value) != "0":
                        return return_value
                    logger.debug("updated_" + other_control_file + "_control_file_path: \"" + other_control_file_path + "\"")


                    # If conffiles_prefix_to_replace is set
                    if conffiles_prefix_to_replace:
                        # Replace conffiles_prefix_to_replace prefix with installation_prefix in all entries of conffiles at other_control_file_path
                        logger.error("Replacing prefix \"" + conffiles_prefix_to_replace + "\" with \"" + CONFIG.installation_prefix + "\" in conffiles file")
                        return_value = replace_prefix_in_conffiles(conffiles_prefix_to_replace, CONFIG.installation_prefix, other_control_file_path)
                        if str(return_value) != "0":
                            return return_value


                # If other control file is not a valid "utf-8" encoded file
                if not is_valid_utf8_encoded_file(other_control_file, other_control_file_path):
                    return 1

                # Check if conffiles is valid and all entries in conffiles exist in data.tar
                if other_control_file == "conffiles" and not validate_conffiles_file(other_control_file_path, True, data_tar_file_path, tar_compression, tar_format):
                    return 1

                # Use the mtime of the other control file on the host system
                CONFIG.package_control_info_file_mtime = None

                # Add other control file to control_tar_file, and
                # add set_control_info_file_metadata function as
                # filter to set its metadata
                logger.info("Adding " + other_control_file + " file")
                control_tar_file.add(other_control_file_path, arcname="./" + other_control_file, recursive=False, filter=set_control_info_file_metadata)
                log_debug_no_format(logger, "\n")



        logger.debug("Writing to control.tar complete")


    # Validate if control.tar file is a valid ar entry file that can
    # be added to the deb file.
    if not validate_ar_entry("control.tar", control_tar_file_path):
        return 1

    return 0


def create_deb_package():
    "Create a deb package file from the specified manifest." # noqa

    global CONFIG

    file_fd_regex = '^/dev/fd/[0-9]+$'

    # If manifest file does not exist at manifest_file_path and is not
    # path to a file descriptor, like passed via process substitution.
    if not os.path.isfile(CONFIG.manifest_file_path) and \
            not re.match(file_fd_regex, CONFIG.manifest_file_path):
        logger.error("Failed to find manifest file at \"" + CONFIG.manifest_file_path + "\"")
        return 1

    try:
        if re.match(file_fd_regex, CONFIG.manifest_file_path):
            # Check if data can be read from the file descriptor.
            # https://docs.python.org/3/library/select.html#select.select
            manifest_file_fd = os.open(CONFIG.manifest_file_path, os.O_RDONLY | os.O_NONBLOCK)
            rlist, _, _ = select.select([manifest_file_fd], [], [], 0)
            if not rlist:
                logger.error("The manifest file fd at \"" + CONFIG.manifest_file_path + "\" is not readable.")
                return 1

        # Open manifest file at manifest_file_path
        # Manifest must not contain non "utf-8" characters, otherwise
        # an exception will be raised.
        with open(CONFIG.manifest_file_path, "r", encoding="utf-8", errors="strict") as manifest_file:
            try:
                if CONFIG.yaml_manifest_format or \
                        CONFIG.manifest_file_path.endswith(".yml") or \
                        CONFIG.manifest_file_path.endswith(".yaml"):
                    if not yaml_supported:
                        logger.error("Loading yaml files requires ruamel.yaml. \
Install it with \"pip install ruamel.yaml\" in android/termux or \
\"sudo apt install python3-pip; sudo pip3 install ruamel.yaml\" \
in debian/ubuntu or check https://yaml.readthedocs.io/en/latest/install.html.")
                        return 1

                    yaml = ruamel.yaml.YAML(typ='safe', pure=True)
                    data = yaml.load(manifest_file)
                    manifest = collections.OrderedDict(data)
                else:
                    # Load json data from manifest file as a python dict
                    manifest = json.load(manifest_file, object_pairs_hook=collections.OrderedDict)

                # Sanitize illegal characters in manifest
                manifest = sanitize_dict(manifest)
                # logger.info("manifest =\n\"\n" + json.dumps(manifest, indent=4) + "\n\"")
            except ValueError as err:
                logger.error("Loading json from manifest file at \"" + str(CONFIG.manifest_file_path or "") + "\" \
failed with err:\n" + str(err))
                return 1
    except Exception as err:
        logger.error("Opening manifest file at \"" + str(CONFIG.manifest_file_path or "") + "\" failed with err:\n" + str(err))
        return 1

    # Update manifest
    return_value = update_manifest_format(manifest)
    if str(return_value) != "0":
        logger.error("update_manifest_format failed")
        return return_value

    logger.debug("manifest:\n" + json.dumps(manifest, sort_keys=False, indent=4, default=str))

    # If "control" field is missing
    if "control" not in manifest or not manifest["control"] or not isinstance(manifest["control"], dict):
        logger.error("Missing mandatory \"control\" dict field in the manifest")
        return 1


    control = manifest["control"]

    if "Package" in control:
        CONFIG.set_package_name(control["Package"])



    # If package_version not passed as parameter or is empty
    if not CONFIG.package_version and "Version" in control:
        CONFIG.set_package_version(control["Version"])
    else:
        # Update manifest so that create_control_tar can use parameter value
        control["Version"] = CONFIG.package_version


    # If package_architecture not passed as parameter or is empty
    if not CONFIG.package_architecture and "Architecture" in control:
        CONFIG.set_package_architecture(control["Architecture"])
    else:
        # Update manifest so that create_control_tar can use parameter value
        control["Architecture"] = CONFIG.package_architecture


    # If installation_prefix not passed as parameter or is empty
    if not CONFIG.installation_prefix:
        # If "installation_prefix" field exists in the manifest, then set
        # that as installation_prefix
        if "installation_prefix" in manifest and manifest["installation_prefix"]:
            CONFIG.set_installation_prefix(manifest["installation_prefix"])
        # Else set it to the default installation_prefix
        else:
            CONFIG.set_installation_prefix(DEFAULT_INSTALLATION_PREFIX)

    # If installation_prefix is set, then normalize it
    if CONFIG.installation_prefix:
        # If installation_prefix contains parent path references "../"
        if is_parent_path_reference_containing_path(CONFIG.installation_prefix):
            logger.error("installation_prefix \"" + CONFIG.installation_prefix + "\" cannot contain parent path references '../'")
            return 1

        CONFIG.set_installation_prefix(normalize_path(CONFIG.installation_prefix))


    # If installation_prefix is not an absolute path that starts with
    # "/" or does not end with "/usr" or contains a character other
    # than "a-zA-Z0-9_./".
    # Android package names can only be characters in the range "a-zA-Z0-9_."
    # This also ensures installation_prefix is ascii encodable and
    # does not contain control characters, shell metacharacters or
    # spaces ' ' which would obviously make things high-maintenance.
    if not CONFIG.installation_prefix or \
            not CONFIG.installation_prefix.startswith("/") or \
            not CONFIG.installation_prefix.endswith("/usr") or \
            not re.match('^[a-zA-Z0-9_./]+$', CONFIG.installation_prefix):
        logger.error("installation_prefix \"" + CONFIG.installation_prefix + "\" must be an absolute path that start with a '/', \
must end with '/usr' and must only contain characters in the range 'a-zA-Z0-9_./'")
        return 1



    # If "fix_perms" field exists in the manifest
    if "fix_perms" in manifest and isinstance(manifest["fix_perms"], bool):
        CONFIG.fix_perms = manifest["fix_perms"]


    # If "ignore_android_specific_rules" field exists in the manifest
    if "ignore_android_specific_rules" in manifest and isinstance(manifest["ignore_android_specific_rules"], bool):
        CONFIG.ignore_android_specific_rules = manifest["ignore_android_specific_rules"]


    # If "allow_bad_user_names_and_ids" field exists in the manifest
    if "allow_bad_user_names_and_ids" in manifest and isinstance(manifest["allow_bad_user_names_and_ids"], bool):
        CONFIG.allow_bad_user_names_and_ids = manifest["allow_bad_user_names_and_ids"]



    # If files_dir not passed as parameter or is empty
    if not CONFIG.files_dir:
        # If "files_dir" field exists in the manifest, then use that as files_dir
        if "files_dir" in manifest and manifest["files_dir"]:
            files_dir = manifest["files_dir"]
        else:
            files_dir = ""

    # If files_dir is set, then find its realpath
    if files_dir:
        files_dir = os.path.realpath(files_dir)

        # If files_dir does not exist
        if not os.path.isdir(files_dir):
            logger.error("Failed to find files_dir at \"" + files_dir + "\"")
            return 1



    # If control_files_dir not passed as parameter or is empty
    if not CONFIG.control_files_dir:
        # If "control_files_dir" field exists in the manifest, then
        # use that as control_files_dir
        if "control_files_dir" in manifest and manifest["control_files_dir"]:
            control_files_dir = manifest["control_files_dir"]
        else:
            control_files_dir = ""

    # If control_files_dir is set, then find its realpath
    if control_files_dir:
        control_files_dir = os.path.realpath(control_files_dir)



    # If deb_dir not passed as parameter or is empty
    if not CONFIG.deb_dir:
        # If "deb_dir" field exists in the manifest, then use that as deb_dir
        if "deb_dir" in manifest and manifest["deb_dir"]:
            deb_dir = manifest["deb_dir"]
        else:
            deb_dir = ""

    # If deb_dir is set, then find its realpath
    if deb_dir:
        deb_dir = os.path.realpath(deb_dir)



    # Validate manifest
    return_value = validate_manifest(manifest)
    if str(return_value) != "0":
        logger.error("validate_manifest failed")
        return return_value



    # If deb_name not passed as parameter or is empty
    if not CONFIG.deb_name:
        # If "deb_name" field exists in the manifest, then use that as deb_name
        if "deb_name" in manifest and manifest["deb_name"]:
            deb_name = manifest["deb_name"]
        # Else set default deb_name
        else:
            # If "deb_architecture_tag" field exists in the manifest, then use that in deb_name
            if "deb_architecture_tag" in manifest and manifest["deb_architecture_tag"]:
                deb_name = CONFIG.package_name + "_" + CONFIG.package_version + "_" + manifest["deb_architecture_tag"] + ".deb"
            else:
                deb_name = CONFIG.package_name + "_" + CONFIG.package_version + "_" + CONFIG.package_architecture + ".deb"

    # If deb_name empty or contains a "/"
    if not deb_name or "/" in deb_name:
        logger.error("Invalid deb_name \"" + deb_name + "\"")
        return 1



    logger.debug("Building deb package \"" + deb_name + "\"")

    logger.debug("architecture: \"" + str(CONFIG.package_architecture) + "\"")
    logger.debug("installation_prefix: \"" + str(CONFIG.installation_prefix) + "\"")
    logger.debug("files_dir: \"" + str(files_dir) + "\"")
    logger.debug("control_files_dir: \"" + str(control_files_dir) + "\"")



    # xz tar compression is used by default since that is the default
    # for current versions of dpkg
    # If dpkg gives errors like the following, try using
    # "tar_compression": "none" and "tar_format": "gnutar":
    # dpkg-deb: error: archive <name> has premature member '{control,data}.tar.xz' before 'control.tar', giving up
    # https://manpages.debian.org/testing/dpkg-dev/deb.5.en.html

    # If "tar_compression" field exists in the manifest, then set that as tar_compression_string
    if "tar_compression" in manifest and manifest["tar_compression"]:
        tar_compression_string = manifest["tar_compression"]
    # Else set it to default tar compression
    else:
        tar_compression_string = "xz"

    # Set tar_compression and tar_extension depending on tar_compression_string
    if tar_compression_string == "none":
        tar_compression = ""
        tar_extension = ".tar"
    elif tar_compression_string == "xz":
        tar_compression = "xz"
        tar_extension = ".tar.xz"
    elif tar_compression_string == "gz":
        tar_compression = "gz"
        tar_extension = ".tar.gz"
    else:
        logger.error("Invalid tar_compression_string \"" + tar_compression_string + "\"")
        return 1

    logger.debug("tar_compression: \"" + str(tar_compression_string) + "\"")
    logger.debug("tar_extension: \"" + str(tar_extension) + "\"")



    # GNU tar format is used by default since that is officially
    # supported by dpkg
    # pax is not supported and if its used, then dpkg may consider the
    # tar corrupted and give errors like:
    # corrupted filesystem tarfile in package in package archive:
    # unsupported PAX tar header type 'x'
    # https://manpages.debian.org/testing/dpkg-dev/deb.5.en.html

    # If "tar_format" field exists in the manifest, then set that as tar_format_string
    if "tar_format" in manifest and manifest["tar_format"]:
        tar_format_string = manifest["tar_format"]
    # Else set it to default tar format
    else:
        tar_format_string = "gnutar"

    # Set tar_format depending on tar_format_string
    if tar_format_string == "gnutar":
        tar_format = tarfile.GNU_FORMAT
    elif tar_format_string == "ustar":
        tar_format = tarfile.USTAR_FORMAT
    elif tar_format_string == "pax":
        tar_format = tarfile.PAX_FORMAT
    else:
        logger.error("Invalid tar_format_string \"" + tar_format_string + "\"")
        return 1

    logger.debug("tar_format: \"" + str(tar_format_string) + "\"\n")



    # Create a temp directory for package and set paths to debian_binary_file,
    # data_tar_file and control_tar_file inside it
    package_main_temp_directory_path = tempfile.mkdtemp(prefix=os.path.basename(CONFIG.manifest_file_path) + "-")
    CONFIG.package_temp_directory_paths_list.append(package_main_temp_directory_path)
    debian_binary_file_path = package_main_temp_directory_path + "/debian-binary"
    data_tar_file_path = package_main_temp_directory_path + "/data" + tar_extension
    control_tar_file_path = package_main_temp_directory_path + "/control" + tar_extension

    try:
        # Call create_debian_binary_file to create debian-binary
        return_value = create_debian_binary_file(debian_binary_file_path)
        if str(return_value) != "0":
            logger.error("create_debian_binary_file failed")
            return return_value
    except Exception as err:
        logger.error("Creating debian-binary file failed with err:\n" + str(traceback.format_exc()))
        return 1

    try:
        # Call create_data_tar to create data.tar
        return_value = create_data_tar(manifest, files_dir, data_tar_file_path, tar_compression, tar_format)
        if str(return_value) != "0":
            logger.error("create_data_tar failed")
            return return_value
    except Exception as err:
        logger.error("Creating data.tar failed with err:\n" + str(traceback.format_exc()))
        return 1

    try:
        # Call create_control_tar to create control.tar
        return_value = create_control_tar(manifest, files_dir, control_files_dir, data_tar_file_path, control_tar_file_path, tar_compression, tar_format)
        if str(return_value) != "0":
            logger.error("create_control_tar failed")
            return return_value
    except Exception as err:
        logger.error("Creating control.tar file failed with err:\n" + str(traceback.format_exc()))
        return 1



    log_debug_no_format(logger, "\n\n")
    logger.debug("Validating deb package")

    # If deb_dir is set
    if deb_dir:
        # If any file exists at deb_dir
        if os.path.exists(deb_dir):
            # If file is not a directory
            if not os.path.isdir(deb_dir):
                logger.error("A non-directory file already exists at deb_dir \"" + deb_dir + "\"")
                return 1
        # Else create a directory at deb_dir
        else:
            os.makedirs(deb_dir)
            # If failed to create deb_dir
            if not os.path.isdir(deb_dir):
                logger.error("Failed to create deb_dir at \"" + deb_dir + "\"")
                return 1

        # Set deb_path to deb_path/deb_name
        deb_path = deb_dir + "/" + deb_name
    else:
        # Set deb_path to deb_name
        deb_path = deb_name

    # If any file exists at deb_path
    if os.path.exists(deb_path):
        # If file is not a regular file
        if not os.path.isfile(deb_path):
            logger.error("A non-regular file already exists at \"" + deb_path + "\"")
            return 1
        # Else remove it
        else:
            os.remove(deb_path)

    # If debian-binary does not exist at debian_binary_file_path as expected
    if not os.path.isfile(debian_binary_file_path):
        logger.error("Failed to find debian-binary at \"" + debian_binary_file_path + "\"")
        return 1

    # If control.tar does not exist at control_tar_file_path as expected
    if not os.path.isfile(control_tar_file_path):
        logger.error("Failed to find control.tar at \"" + control_tar_file_path + "\"")
        return 1

    # If data.tar does not exist at data_tar_file_path as expected
    if not os.path.isfile(data_tar_file_path):
        logger.error("Failed to find data.tar at \"" + data_tar_file_path + "\"")
        return 1


    logger.info("Creating deb archive at \"" + deb_path + "\"")

    # Call ar to create deb file at deb_path containing debian-binary,
    # control.tar and data.tar in that specific order as per debian policy
    ar_command_array = [
        "ar", "r", deb_path,
        debian_binary_file_path,
        control_tar_file_path,
        data_tar_file_path
    ]
    (return_value, stdout, stderr) = run_shell_command(ar_command_array)
    if stdout and not stdout.isspace():
        if str(return_value) == "0":
            logger.debug(str(stdout))
        else:
            logger.error(str(stdout))
    if stderr and not stderr.isspace():
        if str(return_value) == "0":
            logger.debug(str(stderr))
        else:
            logger.error(str(stderr))
    if str(return_value) != "0":
        logger.error("ar command to create deb file at \"" + deb_path + "\" failed")
        logger.error(get_list_string(ar_command_array))
        return return_value

    # If deb file does not exist at deb_path as expected
    if not os.path.isfile(deb_path):
        logger.error("Failed to find deb file at \"" + deb_path + "\"")
        return 1


    logger.info("Creating deb archive complete")

    return 0


def cleanup_deb_package():
    "Cleanup deb package temp files." # noqa

    # If package_temp_directory_paths_list is set
    if CONFIG.package_temp_directory_paths_list:
        for package_temp_directory_path in CONFIG.package_temp_directory_paths_list:
            # If package_temp_directory_path is set and is a directory
            if package_temp_directory_path and os.path.isdir(package_temp_directory_path):
                # logger.debug("Removing temp directory: \"" + package_temp_directory_path + "\"")
                shutil.rmtree(package_temp_directory_path)

    # If package_temp_file_paths_list is set
    if CONFIG.package_temp_file_paths_list:
        for package_temp_file_path in CONFIG.package_temp_file_paths_list:
            # If package_temp_file_path is set and is a file
            if package_temp_file_path and os.path.isfile(package_temp_file_path):
                # logger.debug("Removing temp file: \"" + package_temp_file_path + "\"")
                os.remove(package_temp_file_path)


DESCRIPTION = """
termux-create-package command is used to create binary deb packages.

Usage:
  termux-create-package [optional arguments] manifests...
""" # noqa

EPILOG = """
The paths to YAML or JSON manifest file(s) must be passed as "manifests".
""" # noqa

DESCRIPTION_EXTRA = """
Example YAML manifest:

```yaml
control:
    Package: hello-world
    Version: 0.1.0
    Architecture: all
    Maintainer: GithubNick <GithubNick@gmail.com>
    Depends: python (>= 3.0), libandroid-support
    Homepage: https://hello-world.com
    Description: |-
        This is the hello world package
         It is just an example for termux-create-package
         .
         It is just prints 'Hello world'

installation_prefix: /data/data/com.termux/files/usr

data_files:
    bin/hello-world:
        source: hello-world.py
        set_shebang: "#!/data/data/com.termux/files/usr/bin/env python3"

    share/man/man1/hello-world.1:
        source: hello-world.1
```


Example JSON manifest:
```json
{
    "control": {
        "Package": "hello-world",
        "Version": "0.1.0",
        "Architecture": "all",
        "Maintainer": "GithubNick <GithubNick@gmail.com>",
        "Depends": "python (>= 3.0), libandroid-support",
        "Homepage": "https://hello-world.com",
        "Description": [
            "This is the hello world package",
            " It is just an example for termux-create-package",
            " .",
            " It is just prints 'Hello, world'"
            ]
    },

    "installation_prefix": "/data/data/com.termux/files/usr",

    "data_files": {
        "bin/hello-world": { "source": "hello-world.py",
                                "set_shebang": "#!/data/data/com.termux/files/usr/bin/env python3" },
        "share/man/man1/hello-world.1": { "source": "hello-world.1" }
    }
}
```
""" # noqa


class ShowHelpExtraAction(argparse.Action):
    "Show termux-create-package extra help" # noqa

    def __call__(self, parser, namespace, values, option_string=None):
        parser.print_help()
        print("\n" + DESCRIPTION_EXTRA)
        sys.exit(0)


def main(argv):
    "termux-create-package main." # noqa

    global CONFIG

    parser = argparse.ArgumentParser(
        description=DESCRIPTION,
        epilog=EPILOG,
        usage=argparse.SUPPRESS,
        formatter_class=argparse.RawTextHelpFormatter)

    # Add supported arguments to parser
    parser.add_argument("--help-extra", help="show extra help message and exit", nargs=0, action=ShowHelpExtraAction)

    parser.add_argument("--version", action="version", version=VERSION)

    parser.add_argument("-v", help=""""set verbose level,
pass once for log level "INFO" and twice for "DEBUG""""", dest="log_level", action="append_const", const=1)

    parser.add_argument("--control-files-dir", help="""path to directory of maintainer scripts and other control files,
(default: current directory,
unless "control_files_dir" field is set or "--files-dir" is passed or "files_dir" manifest field is set)""")

    parser.add_argument("--deb-dir", help="""path to directory to create deb file in,
(default: current directory,
unless "deb_dir" manifest field is set)""")

    parser.add_argument("--deb-name", help="""name of deb file to create,
(default: "${Package}_${Version}_S{Architecture}.deb",
unless "deb_name" manifest field is set)""")

    parser.add_argument("--files-dir", help="""path to directory of package files,
(default: relative to current directory,
unless "files_dir" manifest field is set)""")

    parser.add_argument("--pkg-arch", help="""architecture the package was compiled for or will run on,
(default: "Architecture" manifest \"control\" dict field)""")

    parser.add_argument("--pkg-version", help="""version for the package,
(default: "Version" manifest \"control\" dict field)""")

    parser.add_argument("--prefix", help="""path under which to install the files on the target system
(default: """ + DEFAULT_INSTALLATION_PREFIX + """,
unless "installation_prefix" manifest field is set)""")

    parser.add_argument("--yaml", action="store_true", help="""force consider manifest to be in yaml format,
(default: false""")

    parser.add_argument("manifests", nargs="+", help="YAML or JSON manifest file(s) describing the package(s)")


    # If no args passed, then show help and exit
    if len(argv) == 0:
        parser.print_help()
        sys.exit(1)

    # Parse args
    args = parser.parse_args(argv)

    # Set args to local variables
    files_dir_param = str(args.files_dir) if args.files_dir else ""
    control_files_dir_param = str(args.control_files_dir) if args.control_files_dir else ""
    deb_dir_param = str(args.deb_dir) if args.deb_dir else ""
    deb_name_param = str(args.deb_name) if args.deb_name else ""
    package_architecture_param = str(args.pkg_arch) if args.pkg_arch else ""
    package_version_param = str(args.pkg_version) if args.pkg_version else ""
    installation_prefix_param = str(args.prefix) if args.prefix else ""
    yaml_manifest_format_param = args.yaml
    manifest_file_paths_list = args.manifests



    # Set logger and LOG_LEVEL
    log_level_index = LOG_LEVELS.index(DEFAULT_LOG_LEVEL)

    # For each "-v" flag, adjust the LOG_LEVEL between 0 and len(LOG_LEVELS) - 1
    for adjustment in args.log_level or ():
        log_level_index = min(len(LOG_LEVELS) - 1, max(log_level_index + adjustment, 0))
    set_root_logger_and_log_level(LOG_LEVELS[log_level_index])


    logger.debug("Starting termux-create-package")

    # Set the global variable FILESYSTEM_ENCODING
    set_filesystem_encoding()

    # For all manifests in manifest_file_paths_list
    return_value = "1"
    manifest_number = 1
    for manifest_file_path in manifest_file_paths_list:

        if len(manifest_file_paths_list) == 1:
            logger.info("Processing manifest \"" + manifest_file_path + "\"")
        else:
            if manifest_number > 1:
                log_debug_no_format(logger, "\n\n\n")
            logger.info("Processing manifest " + str(manifest_number) + " \"" + manifest_file_path + "\"")

        # Create deb package from manifest
        CONFIG = PackageConfig()
        CONFIG.manifest_file_path = manifest_file_path
        CONFIG.files_dir = files_dir_param
        CONFIG.control_files_dir = control_files_dir_param
        CONFIG.deb_dir = deb_dir_param
        CONFIG.deb_name = deb_name_param

        CONFIG.set_package_architecture(package_architecture_param)
        CONFIG.set_package_version(package_version_param)
        CONFIG.set_installation_prefix(installation_prefix_param)

        CONFIG.yaml_manifest_format = yaml_manifest_format_param

        return_value = create_deb_package()
        cleanup_deb_package()

        if str(return_value) != "0":
            logger.error("create_deb_package for the manifest \"" + CONFIG.manifest_file_path + "\" failed with exit code \"" + str(return_value) + "\"")
            if not str(return_value).isdigit():
                return_value = "1"
            break

        manifest_number += 1


    sys.exit(int(return_value))


if __name__ == "__main__":
    main(sys.argv[1:])
