#!/usr/bin/env python3

try:
    import io
    import json
    import os
    import sys
    import subprocess
    import tarfile
    import tempfile
except Exception as error:
    print("An error occurred!")
    print("Error:")
    print(str(error))
class BuildDEB:
    def build(self, prefix, manifest):
        PREFIX = prefix
        #import argparse, io, json, os, sys, subprocess, tarfile, tempfile
        manifest_file_path = manifest
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

    def debian(self, manifest):
        prefix = "/usr/"
        self.build(prefix, manifest)
    def termux(self, manifest):
        prefix = "/data/data/com.termux/files/usr/"
        self.build(prefix,manifest)

class Main:
    def run(self):
        inst = BuildDEB()
        arglist = sys.argv
        if len(arglist) == 4 and arglist[1] == "build" and arglist[2] == "debian" and os.path.exists(arglist[3]) == True:
            try:
                inst.debian(arglist[3])
            except Exception as error:
                print(str(error))
        elif len(arglist) == 4 and arglist[1] == "build" and arglist[2] == "termux" and os.path.exists(arglist[3]) == True:
            try:
                inst.debian(arglist[3])
            except Exception as error:
                print(str(error))
        else:
            print("Invalid list of args supplied!")

def main():
    main = Main()
    main.run()

if __name__ == "__main__":
    main()
