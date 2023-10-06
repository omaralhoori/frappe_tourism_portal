from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in tourism_portal/__init__.py
from tourism_portal import __version__ as version

setup(
	name="tourism_portal",
	version=version,
	description="B2B for tourism companies",
	author="omaralhoori",
	author_email="tourismportal@mail.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
