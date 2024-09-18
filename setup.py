# vim: set fileencoding=utf-8
"""
domika-ha-framework.

(c) DevPocket, 2024


Author(s): Artem Bezborodko
"""

from pathlib import Path

from setuptools import find_packages, setup

with Path("README.md").open("r", encoding="utf-8") as f:
    long_description = f.read()

with Path("requirements.txt").open("r", encoding="utf-8") as f:
    requirements = f.readlines()

_CONFIG = {
    "name": "domika_ha_framework",
    "version": "0.0.4",
    "author": "DevPocket LLC",
    "author_email": "",
    "description": "Domika integration module framework.",
    "long_description": long_description,
    "long_description_content_type": "text/markdown",
    "url": "https://github.com/DevPocket/domika-ha-framework",
    "project_urls": {
        "Source": "https://github.com/DevPocket/domika-ha-framework",
        "Tracker": "https://github.com/DevPocket/domika-ha-framework/issues",
    },
    "zip_safe": False,
    "package_dir": {
        "": "src",
    },
    "packages": find_packages("src"),
    "include_package_data": True,
    "scripts": [],
    "entry_points": {},
    "install_requires": requirements,
    "classifiers": [
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet",
        "Topic :: Home Automation",
        "Topic :: System :: Networking",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
}

setup(**_CONFIG)
