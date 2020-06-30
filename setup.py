from setuptools import setup, find_packages

setup(
    name='sixfab-diagnostic-tool',
    version='0.0.2',
    author='Ensar Karabudak',
    author_email='ensarkarabudak@gmail.com',
    description='Sixfab Diagnostic Tool',
    license='MIT',
    url='https://github.com/sixfab/setup-and-diagnostic-tool.git',
    dependency_links  = [],
    install_requires  = [
        'prompt_toolkit==1.0.14',
        'pyinquirer',
        'tqdm',
        'yaspin',
        'serial',
        'rpi-gpio',
        'request',
        'pathlib',
        'pyserial'
        ],
	packages=find_packages()
)