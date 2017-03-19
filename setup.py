from setuptools import setup

# https://packaging.python.org/distributing/#packaging-your-project
setup(
    name = 'termux-create-package',
    version = '0.4',
    license = 'MIT',
    description = 'Lightweight tool for creating deb packages',
    author = 'Fredrik Fornwall',
    author_email = 'fredrik@fornwall.net',
    url = 'https://github.com/termux/termux-create-package',
    scripts = ['termux-create-package'],
    classifiers = (
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Programming Language :: Python :: 3'
    )
)
