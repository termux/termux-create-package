#!../usr/bin/python

import argparse, io, json, os, sys, subprocess, tarfile, tempfile

PREFIX = "/data/data/com.termux/files/usr/"

description = """Create a Termux package from a json manifest file. Example of manifest:
{
  "name": "mypackage",
  "version": "0.1",
  "arch": "all",
  "maintainer": "@MyGithubNick",
  "description": "This is a hello world package",
  "homepage": "https://example.com",
  "depends": ["python", "vim"],
  "provides": ["vi"],
  "conflicts": ["vim-python-git"],
  "files" : {
    "hello-world.py": "bin/hello-world",
    "hello-world.1": "usr/share/man/man1/hello-world.1"
  }
}
The "maintainer", "description", "homepage", "depends", "provides" and
"conflicts" properties are all optional.  The "arch" property defaults to "all"
(that is, a platform-independent package not containing native code).  Run
"uname -m" to find out arch name if creating native code inside Termux.  The
resulting .deb file can be installed by Termux users with:
  apt install ./package-file.deb'"""

parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("manifest")
parser.add_argument("--prefix", help="set prefix dir (default: " + PREFIX + ")")
args = parser.parse_args()
if args.prefix: PREFIX = str(args.prefix)

manifest_file_path = args.manifest
with open(manifest_file_path) as f: manifest = json.load(f)

for prop in 'name', 'version', 'files':
	if prop not in manifest: sys.exit('Missing mandatory "' + prop + '" property')

package_name = manifest['name']
package_version = manifest['version'];
package_files = manifest['files']

package_arch = 'all'
if 'arch' in manifest: package_arch = manifest['arch']
if package_arch not in ['all', 'arm', 'i686', 'aarch64', 'x86_64']:
	sys.exit('Invalid "arch" - must be one of all/arm/i686/aarch64/x86_64')

package_maintainer = 'None'
if 'maintainer' in manifest: package_maintainer = manifest['maintainer']

package_description = 'No description'
if 'description' in manifest: package_description = manifest['description']

package_homepage = 'No homepage'
if 'homepage' in manifest: package_homepage = manifest['homepage']

package_deps = []
if 'depends' in manifest: package_deps = manifest['depends']

package_provides = []
if 'provides' in manifest: package_provides = manifest['provides']

package_conflicts = []
if 'conflicts' in manifest: package_conflicts = manifest['conflicts']

output_debfile_name = package_name + '_' + package_version + '_' + package_arch + '.deb'
print('Building ' + output_debfile_name)

package_tmp_directory = tempfile.TemporaryDirectory()
with open(package_tmp_directory.name + '/debian-binary', 'w') as debian_binary: debian_binary.write("2.0\n")

with tarfile.open(package_tmp_directory.name + '/control.tar.xz', mode = 'w:xz') as control_tarfile:
	contents = 'Package: ' + package_name + "\n"
	contents += 'Version: ' + package_version + "\n"
	contents += 'Architecture: ' + package_arch + "\n"
	contents += 'Maintainer: ' + package_maintainer + "\n"
	contents += 'Description: ' + package_description + "\n"
	contents += 'Homepage: ' + package_homepage + "\n"

	if len(package_deps) > 0:
		contents += 'Depends: '
		delim = ''
		for d in package_deps:
			contents += delim + d
			delim = ','
		contents += '\n'

	if len(package_provides) > 0:
		contents += 'Provides: '
		delim = ''
		for d in package_provides:
			contents += delim + d
			delim = ','
		contents += '\n'

	if len(package_conflicts) > 0:
		contents += 'Conflicts: '
		delim = ''
		for d in package_conflicts:
			contents += delim + d
			delim = ','
		contents += '\n'

	control_file = io.BytesIO(contents.encode('utf8'))
	control_file.seek(0, os.SEEK_END)
	file_size = control_file.tell()
	control_file.seek(0)

	info = tarfile.TarInfo(name="control")
	info.size = file_size
	control_tarfile.addfile(tarinfo=info, fileobj=control_file)

with tarfile.open(package_tmp_directory.name + '/data.tar.xz', mode = 'w:xz') as data_tarfile:
	for input_file in package_files:
		file_stat = os.stat(input_file)

		# The tar file path should not start with slash:
		if PREFIX.startswith('/'): PREFIX = PREFIX[1:]
		if not PREFIX.endswith('/'): PREFIX += '/'

		output_file = PREFIX + package_files[input_file]
		info = tarfile.TarInfo(name=output_file)

		info.mode = file_stat.st_mode
		info.mtime = file_stat.st_mtime
		info.size = file_stat.st_size
		with open(input_file, 'rb') as f:
			data_tarfile.addfile(tarinfo=info, fileobj=f)

subprocess.check_call(['ar', 'r', output_debfile_name,
  package_tmp_directory.name + '/debian-binary',
  package_tmp_directory.name + '/control.tar.xz',
  package_tmp_directory.name + '/data.tar.xz'
])
