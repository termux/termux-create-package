# termux-create-package

A utility to create [binary deb packages](https://www.debian.org/doc/debian-policy/ch-binary.html).

By default it creates binary deb packages for installation in the [Termux](https://termux.com) Linux environment, but by passing the `--prefix /usr` argument or defining `installation_prefix: "/usr"` field in the `YAML` or `JSON`  manifest, a deb file can be created for linux distributions such as Debian or Ubuntu, etc.
##



### Contents
- [Compatibility](#Compatibility)
- [Downloads](#Downloads)
- [Installation](#Installation)
- [Current Features](#Current-Features)
- [Usage](#Usage)
- [Package Control File Fields](#Package-Control-File-Fields)
- [Package Create Info Fields](#Package-Create-Info-Fields)
- [Package Data Files Fields](#Package-Data-Files-Fields)
- [Other Control Files](#Other-Control-Files)
- [Examples](#Examples)
##



### Compatibility

- Android version `>= 7.0` using [Termux App].
- Linux distros.
- Windows using [cygwin](https://cygwin.com/index.html) or [WSL](https://docs.microsoft.com/en-us/windows/wsl). *(Untested)*
##



### Downloads

Latest version is `v0.12.0`.

- [GitHub releases](https://github.com/termux/termux-create-package/releases).
##



### Installation

Check [INSTALLATION.md](INSTALLATION.md) file for the **install instructions**.

Note that `termux-create-package` is no longer updated on the [`Python Package Index (PyPI)`](https://pypi.org/project/termux-create-package/) and should not be installed with `pip`. Latest version on `PyPi` is `0.7`.
##



### Current Features

- Define package build info in [`YAML` `1.2.0`](https://yaml.org/spec/1.2.0) or [`JSON`](https://docs.python.org/3.7/library/json.html) manifest files. 
- Create binary deb packages as per debian policy.
- Automatically create `control`, `md5sums`, `conffiles` file.
- Automatically set permissions and ownership to files.
- Run specific actions on package files like setting shebangs.
##



### Usage

```
termux-create-package command is used to create binary deb packages.

Usage:
  termux-create-package [optional arguments] manifests...

positional arguments:
  manifests             YAML or JSON manifest file(s) describing the package(s)

optional arguments:
  -h, --help            show this help message and exit
  --help-extra          show extra help message and exit
  --version             show program's version number and exit
  -v                    "set verbose level,
                        pass once for log level "INFO" and twice for "DEBUG
  --control-files-dir CONTROL_FILES_DIR
                        path to directory of maintainer scripts and other control files,
                        (default: current directory,
                        unless "control_files_dir" field is set or "--files-dir" is passed or "files_dir" manifest field is set)
  --deb-dir DEB_DIR     path to directory to create deb file in,
                        (default: current directory,
                        unless "deb_dir" manifest field is set)
  --deb-name DEB_NAME   name of deb file to create,
                        (default: "${Package}_${Version}_S{Architecture}.deb",
                        unless "deb_name" manifest field is set)
  --files-dir FILES_DIR
                        path to directory of package files,
                        (default: relative to current directory,
                        unless "files_dir" manifest field is set)
  --pkg-arch PKG_ARCH   architecture the package was compiled for or will run on,
                        (default: "Architecture" manifest "control" dict field)
  --pkg-version PKG_VERSION
                        version for the package,
                        (default: "Version" manifest "control" dict field)
  --prefix PREFIX       path under which to install the files on the target system
                        (default: /data/data/com.termux/files/usr,
                        unless "installation_prefix" manifest field is set)
  --yaml                force consider manifest to be in yaml format,
                        (default: false

The paths to YAML or JSON manifest file(s) must be passed as "manifests".
```

The `termux-create-package` script expects the package manifest files containing info on how to build the package to be defined in [`YAML` `1.2.0`](https://yaml.org/spec/1.2.0) or [`JSON`](https://docs.python.org/3.7/library/json.html) format. `YAMl` is the preferred format since its a better configuration language than `JSON`, specially due to support for comments and splitting strings on multiple lines.

The deb file created will be as per [Debian Policy Manual](https://www.debian.org/doc/debian-policy/index.html) and will contain the following files:
- `debian-binary` will contain the package format version number. Currently `2.0`.

- `control.tar*` will contain the [`control`](https://www.debian.org/doc/debian-policy/ch-controlfields.html) file containing package info, `md5sums` containing `md5` hashes of package files, maintainer scripts and other control files. More info on `control` file can be found at [dpkg-dev/deb-control](https://manpages.debian.org/testing/dpkg-dev/deb-control.5.en.html).

- `data.tar*` will contain the package data files.

**Note that any optional arguments passed will override their respective manifest fields in ALL manifests passed**, so use wisely, or use them only if passing only a single manifest.

Beware of trailing commas in `JSON` manifest for the last item of lists and dictionaries since otherwise an exception will be raised. 

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
##



### Package Control File Fields


The fields in the manifest file under the `control` dictionary will be added to the `control` file in `control.tar*` and should contain the package info.

The field name must be composed of `US-ASCII` characters within the range `32`/`U+0021` through `126`/`U+007E` excluding space ` ` and colon `:` characters and it must not begin with hyphen `-` or comment `#` characters. Field names are not case-sensitive, but it is usual to capitalize the first letter of words as per [`CamelCase`](https://simple.wikipedia.org/wiki/CamelCase) format. The fields must be defined in `CamelCase` for versions `>= 0.12.0` but old format is also supported to maintain backward compatibility. Some keys were named differently previously, which are also supported.

The common fields that are added to the control file in order if they exist in the manifest are `Package`, `Source`, `Version`, `Architecture`, `Maintainer`, `Installed-Size`, `Section`, `Priority`, `Essential`, `Depends`, `Pre-Depends`, `Recommends`, `Suggests`, `Breaks`, `Conflicts`, `Replaces`, `Enhances`, `Provides`, `Homepage`, `Description`. Any other field that exists in the manifest are added after the `Provides` field and before the `Homepage` field. The `Installed-Size` field will be automatically added by calculating data files sizes if its not already defined in the manifest.

The `Package`, `Version`, `Architecture`, `Maintainer` and `Description` fields are **mandatory** as per debian policy and their valid values must exist in the manifest. The `Architecture` value can optionally be passed as a command option if the manifest is to be shared between different architectures.

If the field is not of type `list`, then it is converted to a normal string and added to the control file. Fields that are `null` or empty are not added. Check [syntax of control files](https://www.debian.org/doc/debian-policy/ch-controlfields.html#syntax-of-control-files) section in debian policy for further details.

If the field is of type `list` and is not one of the package relationship fields, then each item of the list will be joined together by newlines and added to the control file. This is helpful to define multi-line fields like `Description`.

If the field is of type `list` and is one of the package relationship fields, i.e `Depends`, `Pre-Depends`, `Recommends`, `Suggests`, `Breaks`, `Conflicts`, `Replaces`, `Enhances` and `Provides`, then it will automatically be joined on a comma followed by space character `, `. If these fields are defined as a string, then a comma must be added between each package of the field in the manifest, otherwise `dpkg` will throw an error like `parsing file '/var/lib/dpkg/tmp.ci/control' near line 6 package 'hello-world': 'Depends' field, syntax error after reference to package 'python3'` during `deb` installation. These fields are currently not validated due to them being a bit complex to easily parse/validate. Check [declaring relationships between packages](https://www.debian.org/doc/debian-policy/ch-relationships.html) section in debian policy for further details.

All below fields are of type `string` unless otherwise specified.

#### `Package`

The name of the package. This field was named `name` in versions `< 0.12.0`. Check [here](https://www.debian.org/doc/debian-policy/ch-controlfields.html#package) for more details.

*Valid Values:* It must consist only of lower case letters `a-z`, digits `0-9`, plus `+` and hyphen `-` signs, and periods `.`. It must be at least two characters long and must start with an alphanumeric character. The same rules apply to the optional `Source` field.

#### `Version`

The version of the package. Check [here](https://www.debian.org/doc/debian-policy/ch-controlfields.html#version) for more details.

*Valid Values:* It must be in the format `[epoch:]upstream_version[-debian_revision]`. `epoch` can only be an integer. `upstream_version` and `debian_revision` must consist only of upper or lower case letters `a-zA-Z`, digits `0-9`, plus `+` and tilde `~` signs, and periods `.`. The `upstream_version` must start with a digit. The hyphen `-` is only allowed if `debian_revision` is set.

#### `Architecture`

The architecture the package was compiled for or will run on. This field was named `arch` in versions `< 0.12.0`. Check [here](https://www.debian.org/doc/debian-policy/ch-controlfields.html#architecture) for more details.

Set to `all` if the package only contains architecture-independent data. If installation prefix starts with `/data/data/<app_package>/files/`, then it must be one of `all`, `arm`, `i686`, `aarch64` or `x86_64` since android only supports those architectures, however, you can override this by adding `"ignore_android_specific_rules": true` entry to the manifest.

*Valid Values:* It must must contain a space separated list of architectures or architecture wildcards that consist only of lower case letters `a-z`, digits `0-9`, plus `+` and hyphen `-` signs, and periods `.`. It must be at least two characters long and must start with an alphanumeric character.

#### `Maintainer`

The name and contact of the maintainer. It should be in the format `name <email>`, example: `Foo Bar <foo.bar@baz.com>`. It is typically the person who created the package, as opposed to the author of the software that is to be packaged. Check [here](https://www.debian.org/doc/debian-policy/ch-controlfields.html#maintainer) for more details.

#### `Depends`

Comma-separated list of packages that this package depends on. Those packages will be installed automatically when this package is installed using `apt`.

#### `Homepage`

The project home page URL. Check [here](https://www.debian.org/doc/debian-policy/ch-controlfields.html#homepage) for more details.

#### `Description`

Contains the description of the binary package, consisting of two parts, the synopsis or the short description, and the long description. Check [here](https://www.debian.org/doc/debian-policy/ch-controlfields.html#description) for more details. It is a `multi-line` field with the following format:

```
Description: Single line short description
 extended description over several lines
 .
 some more description
 ```
&nbsp;&nbsp;


For `multi-line` fields in `control` file, each line after the first line must have a space character ` ` as the first character and must contain at least one non-whitespace character like a dot `.`, otherwise `dpkg` will throw an error like `parsing file '/var/lib/dpkg/tmp.ci/control' near line 8 package 'hello-world': field name 'It' must be followed by colon` during `deb` installation. To represent empty lines, set the line to a space character followed by a dot ` .`

To define a `multi-line` field in a `YAML` manifest, the field value could be set as a [literal block style `|`](https://yaml.org/spec/1.2.0/#id2594802) with [strip block chomping indication `-`](https://yaml.org/spec/1.2.0/#id2593651) (to strip trailing newlines), like `|-`. Each line will be joined together with a newline character `\n`. **Do not forget `-` after `|`**, otherwise validation will fail since last line due to trailing newline will be considered an empty line.

```
Description: |-
    Single line short description
     extended description over several lines
     .
     some more description
```

To define a multi-line field in a `JSON` manifest the field value could be set to a `list`. Each item of the `list` will be joined together with a newline character `\n`.

```
"Description": [
    "Single line short description",
    " extended description over several lines",
    " .",
    " some more description"
    ]
```
##



### Package Create Info Fields

The fields in the manifest file outside the [`control`] and [`data_files`] dictionaries are used for storing information on how to create the package and what files need to be added to the package. These fields are not added the `control` file.

The currently used package create info fields are the following. All fields are of type `string` unless otherwise specified.

#### `allow_bad_user_names_and_ids`

The `bool` field that decides whether is should be allowed to add package files to the deb that are considered invalid as per debian policy. Check [`owner_uid`](#owner_uid) and [`owner_uname`](#owner_uname) for details on what is considered valid.


#### `conffiles_prefix_to_replace`

The optional path prefix that should be replaced with the installation prefix in the files added in the locally defined `conffiles` file in [`control_files_dir`](#control_files_dir) or [`files_dir`](#files_dir). For example if this is set to `/usr`  and `conffiles` contains a file with the path `/usr/etc/hello-world/hello-world.config` and installation prefix is set to `/data/data/com.termux/files/usr`, then the final `conffiles` added to the deb file with have the path set to `/data/data/com.termux/files/usr/etc/hello-world/hello-world.config` instead. This does not apply to the `conffiles` file dynamically generated with [`data_files`] that have [`is_conffile`](#is_conffile) set to `true`.


#### `control_files_dir`

The path to directory containing maintainer scripts `preinst`, `postinst`, `prerm`, `postrm`, `config` and other control files `conffiles`, `templates`, `shlibs` to include in the deb package. The default is relative to current directory, unless `--control-files-dir` or `--files-dir` argument is passed to the script or [`files_dir`](#files_dir) field is set. This is useful if the same files/build directory is used for different distros or architectures but different maintainer scripts or `conffiles` for each.


#### `deb_architecture_tag`

The architecture tag to use for the file name of the deb file to be created. If [`deb_name`](#deb_name) is not set and `--deb-name` argument is not passed to the script, then deb file will be named `${Package}_${Version}_S{deb_architecture_tag}.deb` instead of `${Package}_${Version}_S{Architecture}.deb`. This is helpful if you want to use the same package and version tag defined in `Package` and `Version` fields respectively but a different architectures tag than the one defined in `Architecture` field.


#### `deb_dir`

The path of the directory to create the deb file in. The default is current directory, unless `--deb-dir` argument is passed to the script.


#### `deb_name`

The file name of the deb file to be created. If this is not set, then deb file will be named `${Package}_${Version}_S{Architecture}.deb` by default, unless `--deb-name` argument is passed to the script.


#### `files_dir`

The path to directory containing package files to include in the deb package. The default is relative to current directory, unless `--files-dir` argument is passed to the script.


#### `fix_perms`

The `bool` field that decides whether permissions of source files that are added as package [`data_files`] should be automatically fixed when adding them to the `deb` file as per [`dh_fixperms`](https://manpages.debian.org/testing/debhelper/dh_fixperms.1.en.html) ([impl](https://github.com/Debian/debhelper/blob/debian/13.1/dh_fixperms)) rules if needed.

The `fix_perms` value is the global value that can be set to `true` (default) or `false` to enable or disable fixing permissions respectively for **all** [`data_files`]. If it is `true`, then you can optionally disable fixing permissions for specific files only by setting their file level [`fix_perm`](#fix_perm) field value to `false`. If it is `false`, then you can optionally enable fixing permissions for specific files only by setting their file level [`fix_perm`](#fix_perm) field value to `true`. The permissions are not fixed if a data file has the [`perm`](#perm) field set.


#### `ignore_android_specific_rules`

The `bool` field that can be set to `true` to ignore the following android specific rules:
- Only allow android specific architectures if prefix is set under the `/data/data/<app_package>/files/` path.
- Remove group and others permissions while setting permissions for files to be added to `data.tar*` under the `/data/data/<app_package>/files/` path if [`perm`](#perm) field is not set and global [`fix_perms`](#fix_perms) and/or file level [`fix_perm`](#fix_perm) is `true`.
- Set permissions of parent directory paths for files to be added to `data.tar*` under the `/data/data/<app_package>/files/` path to `700` instead of `755` .


#### `installation_prefix`

The prefix under which to install the files on the target system. The termux prefix `/data/data/com.termux/files/usr` is used by default if the field is not defined, unless `--prefix` argument is passed to the script. It must be an absolute path that starts with forward slash `/`, ends with `/usr` and must only contain characters in the range `a-zA-Z0-9_./`. It cannot contain parent path references `../`.


#### `maintainer_scripts_shebang`

The shebang that should be set on the maintainer scripts if the first line starts with `#!`. Example: `#!/bin/bash` for linux distros and `#!/data/data/com.termux/files/usr/bin/bash` for termux.


#### `tar_compression`

The compression type of `control.tar*` and `data.tar*`. The `xz` tar compression is used by default if the field is not defined since that is the default for current versions of `dpkg`. If `none` is set, then compression will not be done. Check [dpkg-dev/deb](https://manpages.debian.org/testing/dpkg-dev/deb.5.en.html) for more details.

*Valid Values:* `none`, `gz` and `xz`.

#### `tar_format`

The tar format of `control.tar*` and `data.tar*`. The `GNU tar` format is used by default if the field is not defined since that is officially supported by `dpkg`. You may get package corrupted errors if other formats are used, specially `pax`. Check [dpkg-dev/deb](https://manpages.debian.org/testing/dpkg-dev/deb.5.en.html) for more details.

*Valid Values:* `gnutar`, `ustar` and `pax`.
##



### Package Data Files Fields

The [`data_files`] `dictionary` is a **mandatory** field containing a nested `dictionary` type where the parent key is the destination path for the data file inside the deb package or target system and the value is a `dictionary` containing the following keys/value pairs for version `>= 0.12.0`.

If destination path is an absolute path starting with a forward slash `/`, then that will be used. Otherwise it will be considered relative to the installation prefix. If the destination path is an empty string `""`, then it automatically expand to the installation prefix.

Fields that are `null` or empty are not used, other than `source` path.

Non `utf-8` characters are not allowed in any paths as per debian policy.

**Mandatory attribute key/value pairs:**

#### `source`

The source path for the data file from which to read the file that should be added to the package. If source path is an absolute path starting with a forward slash `/`, then that will be used, otherwise it will be considered relative to the current working directory, unless `--files-dir` argument is passed to the script or [`files_dir`](#files-dir) field is set. If the source path is an empty string `""`, then an empty directory will be added at the destination path.
##


**Optional attribute key/value pairs:**

#### `fix_perm`

The `bool` value that defines the `file` level setting for whether fixing permissions should be done for the source file when adding it to the deb. Check [`fix_perms`](#fix_perms) for more info.


#### `is_conffile`

The `bool` value that defines whether this data file is a `conffile` and should be added to the dynamically generated `conffiles` file.


#### `owner_uid`

The owner user id that should be set to the data file when adding it to the deb. It must be within the `0-99`, `60000-64999` and `65534` ranges. By default user id `0` is set, unless [`source_ownership`](#source_ownership) is set. The `source_ownership` takes precedence over `owner_uid`.

Check [`debian policy`](https://www.debian.org/doc/debian-policy/ch-opersys.html#users-and-groups), [`useradd manual`](https://manpages.debian.org/testing/passwd/useradd.8.en.html), [`systemd uid/gid docs`](https://github.com/systemd/systemd/blob/v247/docs/UIDS-GIDS.md) and [`shadow` `find_new_uid.c`](https://github.com/shadow-maint/shadow/blob/4.8.1/libmisc/find_new_uid.c) for more info.

**Note that when installing the `deb` file on android with the termux app, any custom ownership value will not be set and all files will be set to `termux` user ownership.**


#### `owner_uname`

The owner user name that should be set to the data file when adding it to the deb. It must begin with a lower case letter or an underscore, followed by lower case letters, digits, underscores, or hyphens. It can end with a dollar sign. In regular expression terms: `[a-z_][a-z0-9_-]*[$]?`. It may also be only up to `32` characters long. By default user name `root` is set, unless [`source_ownership`](#source_ownership) is set. The `source_ownership` takes precedence over `owner_uname`.

Check [`debian policy`](https://www.debian.org/doc/debian-policy/ch-opersys.html#users-and-groups), [`useradd manual`](https://manpages.debian.org/testing/passwd/useradd.8.en.html), [`shadow` `useradd.c`](https://github.com/shadow-maint/shadow/blob/4.8.1/src/useradd.c#L1448), [`systemd user name docs`](https://github.com/systemd/systemd/blob/v247/docs/USER_NAMES.md), [`shadow` `chkname.c`](https://github.com/shadow-maint/shadow/blob/4.8.1/libmisc/chkname.c) and [`posix docs`](https://pubs.opengroup.org/onlinepubs/9699919799/basedefs/V1_chap03.html#tag_03_437) for more info.


#### `group_uid`

The group user id that should be set to the data file when adding it to the deb. Same rules as [`owner_uid`](#owner_uid) apply.


#### `group_uname`

The group user name that should be set to the data file when adding it to the deb. Same rules as [`owner_uname`](#owner_uname) apply.


#### `perm`

The `3` or `4` digit permission octal that should be set to the data file when adding it to the deb. Example: `755` for `rwxr-xr-x` or `4755` for `rwsr-xr-x` where `setuid` bit is also set. If a custom value in `perm` field is not set, then the permissions will be automatically fixed. Check [`fix_perms`](#fix_perms) for more info.


#### `source_ownership`

The `bool` value for whether source ownership should be used when adding the data file to the deb. If source ownership is not compliant, as per debian policy, then it is ignored and `root:root` ownership is used. Check [`owner_uid`](#owner_uid) and [`owner_uname`](#owner_uname) for details on what is considered valid.
##


**Optional action key/value pairs:**


#### `ignore`

The `bool` value for whether this data file defined in the manifest should be ignored and not added to the deb. Source file existence check is not done.


#### `ignore_if_no_exist`

The `bool` value for whether this data file defined in the manifest should be ignored and not added to the deb if it not does not exist at [`source`](#source) path instead of command exiting with failure. 


#### `set_parent_perm`

The `bool` value for whether the permissions should be set to the parent directory paths for of the data file directory the same as the source permissions or the one defined by [`perm`](#perm). For example, if a destination entry is added for `opt/hello-world/cache`, then `opt` and `opt/hello-world` will also be set to the same permissions. This is useful to define a directory hierarchy with the same specific permissions.


#### `set_shebang`

The shebang that should be set on the data file if the first line starts with `#!`. Example: `#!/bin/bash` for linux distros and `#!/data/data/com.termux/files/usr/bin/bash` for termux.


#### `source_readlink`

The `bool` value for whether the [`source`](#source) path should be traversed if its a symlink. By default if `source` file is a `symlink`, then the `symlink` itself is added to the deb file instead of its target file.


#### `source_recurse`

The `bool` value for whether all files under the [`source`](#source) path should be recursively added to the deb if its a directory. By default **files under `source` directories are not automatically/recursively added to the deb. Each file that needs to be added to the deb must be added separately.** This is useful for cases where the files/build directory contains lots of files but you only want specific files to be added to the deb. You may optionally only add a directory entry and not add any file entries, which would ideally result in an empty directory at the target system if it didn't already exist there.


#### `symlink_destinations`

The `list` value that defines the symlinks that should automatically be created and added to the deb that target the destination data file path. For example adding the entry for the destination file `bin/hello-world.1` and adding `bin/hello-world` to `symlink_destinations` will create a file at `bin/hello-world` that points to `bin/hello-world.1`. This is helpful in defining one or more symlinks dynamically for a file, without having to create symlink files on source system.
##


If specific permission needs to be set to the parent directory of a file that needs to be installed at the target system, then add an empty `source` entry with the [`perm`](#perm) field set before the entry of the file, optionally with [`set_parent_perm`](#set_parent_perm) set to `true` as well. However, if the directory already exists at the target system, then the permission is unlikely to change, use maintainer scripts instead.

```
"data_files": {
    "bin": { "source": "", "perm": "755" },
    "bin/hello-world": { "source": "hello-world.py", "perm": "755" },
    "share/man/man1/hello-world.1": { "source": "hello-world.1", "perm": "644" }
}
```
##


**Old `files` format:**

This [`data_files`] field was named `files` in versions `< 0.12.0` and it had the `source` as the dictionary key instead of the destination. That had the design flaw that a single source file could only be added to one destination path in the deb. Moreover, since destination was the value instead of the key, multiple source files could be added for the same destination. The new design does not have such issues and paths are normalized to check for duplicates too. Old format is also fully supported to maintain backward compatibility. In version `>= 0.8`, with the `files` field, the files in source path directories were recursively added to the deb, but that will not happen in version `>= 0.12.0` with the new [`data_files`] field as mentioned in [`source_recurse`](#source_recurse). **Note that any files whose ownership is not compliant with debian policy, as detailed in [`owner_uid`](#owner_uid) and [`owner_uname`](#owner_uname), will have their ownership replaced with `root:root`. That is likely the only breaking change and users on old formats should shift to newer format and set [`allow_bad_user_names_and_ids`](#allow_bad_user_names_and_ids) to `true` if they want to go against debian policy.**

```
"files": {
    "hello-world.py": "bin/hello-world",
    "hello-world.1": "share/man/man1/hello-world.1"
}
```
##



### Other Control Files

The maintainer scripts `preinst`, `postinst`, `prerm`, `postrm`, `config` and other control files `conffiles`, `templates`, `shlibs` are automatically added to `control.tar*` if they exist in [`control_files_dir`](#control_files_dir) or [`files_dir`](#files_dir).

The ownership of all files added to the `control.tar*` is automatically set to `root:root` as per debian policy. The permission of maintainer scripts is automatically set to `755` and other control files to `644`.

The [`maintainer_scripts_shebang`](#maintainer_scripts_shebang) field is helpful if the same architecture independent scripts need to be added to different debs for linux distros and termux. Check [scripts](https://www.debian.org/doc/debian-policy/ch-files.html#scripts) section in debian policy for further details.

The `conffiles` can be added to the deb in two ways. Either a predefined file can be added to `control_files_dir` or `files_dir` that should be added or it can be dynamically generated by setting the [`is_conffile`](#is_conffile) field to `true` for the [`data_files`] that should be added to the `conffiles`. If even a single file has `is_conffile` set to `true`, then any predefined `conffiles` in [`control_files_dir`](#control_files_dir) or [`files_dir`](#files_dir) will not be added and `conffiles` generated dynamically will be added. All files in the `conffiles` added are validated for existence in the deb and an error will be raised if any file does not exist. If a predefined file is defined, the [`conffiles_prefix_to_replace`](#conffiles_prefix_to_replace) may be useful as well if debs are being built for linux distros and termux. The `conffiles` file content must be `utf-8` encodable as per debian policy and all files must be regular files and not symlinks since that is not officially supported and can result in unpredictable behaviour, directories are not supported either. Each line must contain an absolute file path. Empty lines are not allowed. Check [configuration files](https://www.debian.org/doc/debian-policy/ch-files.html#configuration-files) section in debian policy for further details.
##



### Examples

After creating a manifest for the project, run `termux-create-package </path/to/manifest>` command to create the deb file. Example manifests are provided for both `YAML` and `JSON` in the [`examples`](examples) directory.

- Create a deb package file with defaults: `termux-create-package manifest.yml`

- Create a deb package file with specific installation prefix, files directory, deb directory and deb name: `termux-create-package --prefix '/usr' --files-dir '/path/to/files_directory' --deb-dir '/path/to/deb_directory' --deb-name 'some-name.deb' manifest.json `

- Create example manifest deb from `termux-create-package` repo source: `cd examples/hello-world; ../../src/termux-create-package -vv manifest-ubuntu.yml`

The deb file can be installed by running `dpkg -i package.deb`. The `dpkg` install command will not install dependencies, you can install them by running `apt-get -f install` afterwards.

The deb file can also be added to a custom apt repository created with [`termux-apt-repo`](https://github.com/termux/termux-apt-repo) or any other available tool.
##



[Termux App]: https://github.com/termux/termux-app
[`control`]: #package-control-file-fields
[`data_files`]: #package-data-files-fields
