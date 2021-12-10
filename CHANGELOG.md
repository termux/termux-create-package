# Changelog

All notable changes to this project will be documented in this file.

**Version Number Format:** `major.minor.patch`  
**Release Date Format:** `yyyy-mm-dd`  

**Types of Changes:**
- **Added** for new features.
- **Changed** for changes in existing functionality.
- **Deprecated** for soon-to-be removed features.
- **Removed** for now removed features.
- **Fixed** for any bug fixes.
- **Security** in case of vulnerabilities.
##


## [Unreleased]

### Added
- Add support for `YAML` format for manifests.
- Add support for custom permissions and ownership of data files.
- Add support to automatically set permissions and ownership to control tar files.
- Add support to automatically add `Installed-Size` field to `control` file.
- Add support to automatically generate `md5sums` file.
- Add support to automatically add other controls files `config`, `conffiles`, `templates`, `shlibs` to control tar.
- Add support to add custom `control` file fields.
- Add support for control and data tar compression type and format.
- Add support for `--control-files-dir`, `--deb-dir`, `--deb-name`, `--files-dir`, `--pkg-arch`, `--pkg-version` and `--yaml` comamnd line options.
- Add support of `installation_prefix`, `files_dir`, `tar_compression`, `tar_format`, `deb_dir`, `deb_name`, `deb_architecture_tag`, `control_files_dir`, `maintainer_scripts_shebang`, `conffiles_prefix_to_replace`, `fix_perms`, `allow_bad_user_names_and_ids`, `ignore_android_specific_rules` create info fields in manifest.
- Add support of `source`, `perm`, `fix_perm`, `source_ownership`, `owner_uid`, `owner_uname`, `owner_gid`, `owner_gname`, `is_conffile` attribute fields for `data_files` dictionary in manifest.
- Add support of `ignore`, `ignore_if_no_exist`, `source_readlink`, `source_recurse`, `set_parent_perm`, `symlink_destinations`, `set_shebang` action fields for `data_files` dictionary in manifest.
- Add support to automatically add `termux-create-package` script and `sha256sums.txt` to releases.

### Changed
- The manifest format has been completely changed, but backward compatibility still maintained. Check `README.md` for details. The `files` dictionary has been replaced with `data_files`. The `control` file fields are to be added to the `control` dictionary.
- Extended manifest validation so that debs comply with debian and `dpkg` rules.
- The manifest `Depends`, `Provides`, `Conflicts` and other package relationship fields should be of type `string` now instead of a `list`.
- The manifest `Description` and other multi-line field values should be of type `list` now instead of a `string`.
- The `--prefix` must now be an absolute path.


## [0.11] - 2021-01-28

### Fixed
- Fixed version in `setup.py`. ([`289ebc4f`](https://github.com/agnostic-apollo/termux-create-package/commit/289ebc4f))


## [0.10] - 2020-07-11

### Changed

- Minimized code structure and fixed minor issue


## [0.9] - 2020-07-08

### Added

- Added support for manifest `suggests` and `recommends` fields.


## [0.8] - 2020-07-07

### Added

- Added support to recursively add files to deb from source directories.

### Fixed

- Set default tar format to `tarfile.GNU_FORMAT` instead of `tarfile.PAX_FORMAT` to prevent corrupted package errors from `dpkg`.


## [0.7] - 2018-10-30

### Changed
- Correct release number in setup.py.


## [0.6] - 2018-10-30

### Added
- Allow for folders and symlinks in package ([`#15`](https://github.com/termux/termux-create-package/pull/15)).


## [0.5] - 2018-10-30

### Changed
- Create `./control` instead of control in tar ([`#14`](https://github.com/termux/termux-create-package/pull/14)).


## [0.4] - 2017-03-19

### Added
- Available for installation using pip.


## [0.3] - 2017-03-19

### Added
- Add support for the `--prefix` option.


## [0.2] - 2016-12-11

### Added

- Add support for `Conflicts`, `Homepage` and `Provides` fields.
##


[unreleased]: https://github.com/termux/termux-create-package/compare/v0.11.0...HEAD
[0.11]: https://github.com/termux/termux-create-package/compare/v0.10...v0.11
[0.10]: https://github.com/termux/termux-create-package/compare/v0.9...v0.10
[0.9]: https://github.com/termux/termux-create-package/compare/v0.8...v0.9
[0.8]: https://github.com/termux/termux-create-package/compare/v0.7...v0.8
[0.7]: https://github.com/termux/termux-create-package/releases/tag/v0.7
[0.6]: https://github.com/termux/termux-create-package/releases/tag/v0.6
[0.5]: https://github.com/termux/termux-create-package/releases/tag/v0.5
[0.4]: https://github.com/termux/termux-create-package/releases/tag/v0.4
[0.3]: https://github.com/termux/termux-create-package/releases/tag/v0.3
[0.2]: https://github.com/termux/termux-create-package/releases/tag/v0.2
