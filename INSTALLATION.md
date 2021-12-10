# Installation

### Contents
- [Dependencies](#Dependencies)
- [Termux In Android Installation From Repository](#Termux-In-Android-Installation-From-Repository)
- [Termux In Android Installation From Source](#Termux-In-Android-Installation-From-Source)
- [Linux Distros System Installation From Repository](#Linux-Distros-System-Installation-From-Repository)
- [Linux Distros System Installation From Source](#Linux-Distros-System-Installation-From-Source)
##


### Dependencies

- Android users should install [Termux App](https://github.com/termux/termux-app).

- `python3` and optionally `pip3` should be installed in your system.
  - Termux (non-root shell): `pkg install python`.  Check https://wiki.termux.com/wiki/Python for details. `pip` will automatically be installed.
  - Linux distros: `sudo apt install python3 python3-pip`.

- The [`ruamel.yaml`](https://yaml.readthedocs.io) python module is used to load `YAML` manifest files. Check [Install](https://yaml.readthedocs.io/en/latest/install.html) instructions for more info.
  - Termux (non-root shell): `pip install ruamel.yaml`.
  - Linux distros: `sudo pip3 install ruamel.yaml`.
##



### Termux In Android Installation From Repository

```
pkg install termux-create-package
```
##



### Termux In Android Installation From Source

The `termux-create-package` file should be installed in termux `bin` directory `/data/data/com.termux/files/usr/bin`.  
It should have `termux` `uid:gid` ownership and have readable `600` permission before it can be sourced.  

#### Basic

```
pkg install curl && \
export install_path="/data/data/com.termux/files/usr/bin" && \
mkdir -p "$install_path" && \
curl -L 'https://github.com/termux/termux-create-package/releases/latest/download/termux-create-package' -o "$install_path/termux-create-package" && \
export owner="$(stat -c "%u" "$install_path")"; chown "$owner:$owner" "$install_path/termux-create-package" && chmod 600 "$install_path/termux-create-package";

```

#### Advance

1. Export install directory path and create it.  

```
export install_path="/data/data/com.termux/files/usr/bin"
mkdir -p "$install_path"
```

2. Download the `termux-create-package` file.  

    - Download to install directory directly from github using `curl` using a non-root termux shell.  
        Run `pkg install curl` to install `curl` first.  
        - Latest release:  

          `curl -L 'https://github.com/termux/termux-create-package/releases/latest/download/termux-create-package' -o "$install_path/termux-create-package"`  

        - Specific release:  

          `curl -L 'https://github.com/termux/termux-create-package/releases/download/v0.12.0/termux-create-package' -o "$install_path/termux-create-package"`  

        - Master Branch *may be unstable*:  

          `curl -L 'https://github.com/termux/termux-create-package/raw/master/termux-create-package' -o "$install_path/termux-create-package"`  

    - Download `termux-create-package` file manually from github to the android download directory and then copy it to install directory.  

      You can download the `termux-create-package` file from a github release from the `Assets` dropdown menu.  

      You can also download it from a specific github branch/tag by opening the [`termux-create-package`](./src/termux-create-package) file from the `Code` section.  
      Right-click or hold the `Raw` button at the top and select `Download/Save link`.  

      Then copy the file to install directory using `cat` command below or use a root file browser to manually place it.  

       `cat "/storage/emulated/0/Download/termux-create-package" > "$install_path/termux-create-package"`  

3. Set `termux` ownership and readable permissions.  

    - If you used a `curl` or `cat` to copy the file, then use a non-root termux shell to set ownership and permissions with `chown` and `chmod` commands respectively:  

      `export owner="$(stat -c "%u" "$install_path")"; chown "$owner:$owner" "$install_path/termux-create-package" && chmod 600 "$install_path/termux-create-package";`  

    - If you used a root file browser to copy the file, then use `su` to start a root shell to set ownership and permissions with `chown` and `chmod` commands respectively:  

      `export owner="$(stat -c "%u" "$install_path")"; su -c "chown \"$owner:$owner\" \"$install_path/termux-create-package\" && chmod 600 \"$install_path/termux-create-package\"";`  

    - Or manually set them with your root file browser. You can find `termux` `uid` and `gid` by running the command `id -u` in a non-root termux shell or by checking the properties of the termux `bin` directory from your root file browser.  
##





### Linux Distros System Installation From Repository

```
sudo pip3 install termux-create-package
```
##



### Linux Distros System Installation From Source

The `termux-create-package` file should be placed in the `/usr/local/bin` directory if you want to install it system-wide for all users as per [FHS 3.0](https://refspecs.linuxfoundation.org/FHS_3.0/fhs/ch04s09.html).  
It should have readable `600` permission before it can be sourced.  

The install command for `curl`  is for Ubuntu/Debian, it may be different for other distros.  

#### Basic

```
sudo apt install curl && \
export install_path="/usr/local/bin" && \
sudo mkdir -p "$install_path" && \
sudo curl -L 'https://github.com/termux/termux-create-package/releases/latest/download/termux-create-package' -o "$install_path/termux-create-package" && \
sudo chmod 600 "$install_path/termux-create-package";
```

#### Advance

1. Export install directory path and create it.  

```
export install_path="/usr/local/bin"
mkdir -p "$install_path"
```

2. Download the `termux-create-package` file.  

    - Download to install directory directly from github using `curl` using a root shell with `sudo`.  
        Run `sudo apt install curl` to install `curl` first.  

        - Latest release:  

          `sudo curl -L 'https://github.com/termux/termux-create-package/releases/latest/download/termux-create-package' -o "$install_path/termux-create-package"`  

        - Specific release:  

          `sudo curl -L 'https://github.com/termux/termux-create-package/releases/download/v0.12.0/termux-create-package' -o "$install_path/termux-create-package"`  

        - Master Branch *may be unstable*:  

          `sudo curl -L 'https://github.com/termux/termux-create-package/raw/master/termux-create-package' -o "$install_path/termux-create-package"`  

    - Download `termux-create-package` file manually from github to the install directory.  

      You can download the `termux-create-package` file from a github release from the `Assets` dropdown menu.  

      You can also download it from a specific github branch/tag by opening the [`termux-create-package`](./src/termux-create-package) file from the `Code` section.  
      Right-click or hold the `Raw` button at the top and select `Download/Save link`.  

      Then copy the file to install directory using `cat` command below or use a root file browser to manually place it (`sudo nautilus`).  

       `sudo cat "termux-create-package" > "$install_path/termux-create-package"`  

3. Set readable permissions.  

    - Set ownership and permissions with `chown` and `chmod` commands respectively:  

      `sudo chmod 600 "$install_path/termux-create-package"`  
##
