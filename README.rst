TERMUX-CREATE-PACKAGE
=====================

About
=====
A Python script to make Termux DEB packages.

Usage
=====
As the usage of this tool has been causing a lot of confusion, here is a simple tutorial on how to package a simple Python script called myscript.py into a DEB.

Prerequisites
-------------

- A Linux distro based off Debian
- The Termux app
- Common sense
- Any executables or scripts ( In this example a python script called myproject.py. )
- The full path to the script or executable.

Let's start:
To start the process just execute these commands from your terminal. 

Note: Replace "myproject.py" with your actual Python script and replace "myproject/myproject.py" with the full path to your Python script. Also replace "project" with the name of your project. Make sure that your Python script has a valid shebang line pointing to the right interpreter at the start of the script.

.. code-block:: bash

    $ apt update
    $ apt install wget git python3 coreutils
    $ git clone http://github.com/termux-termux-create-package.git
    $ mkdir project
    $ cd termux-create-package
    $ mv termux-create-package.py ../project
    $ cd ../project
    $ mkdir bin
    $ cp /myproject/myproject.py bin
    $ touch manifest.json
    
Next, put the following in your manifest.json file:

.. code-block:: bash

    { 
     "name": "myproject", 
     "version": "1.0", 
     "arch": "all", 
     "maintainer": "@mynick", 
     "description": "my description", 
     "homepage": "http://mysite.com", 
     "depends": ["dependency"], 
     "files" :{ 
      "bin/myproject.py": "bin/myproject" 
     } 
    }

After having done that, save the file and open up the terminal again! Then, execute this command:

.. code-block:: bash
    
    $ python3 termux-create-package.py manifest.json
    $ ls
    $ bin manifest.json myproject_1.0_all.deb


Congrats! You have just built your own Termux Debian package!
