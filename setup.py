from setuptools import setup, find_packages

setup(
    name='sixfab-tool',
    version='0.0.3',
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
        'RPi.GPIO',
        'request',
        'pathlib',
        'pyserial'
        ],
	packages=find_packages()
)