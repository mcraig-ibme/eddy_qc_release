from setuptools import setup,find_packages
with open('requirements.txt', 'rt') as f:
    install_requires = [l.strip() for l in f.readlines()]

setup(name='squat',
	version='1.0.3',
	description='Quality Control tools',
	author='Matteo Bastiani',
	install_requires=install_requires,
    scripts=['squat/scripts/squat'],
	packages=find_packages(),
	include_package_data=True)
