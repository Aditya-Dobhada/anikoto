from setuptools import setup, find_packages

setup(
    name='anikoto',
    version='8.3.1',
    packages=find_packages(),
    install_requires=[
        'requests',
        'yt-dlp',
        'bs4',
        'curl_cffi',
        'm3u8',
        'pycryptodome',
        'cryptography',
        'langcodes',
        'language-data',
        'customtkinter>=6.0.0',
        'darkdetect'
    ],
    entry_points={
        'console_scripts': [
            'anikoto=anikoto.anikoto:main',
            'anikoto-gui=anikoto.gui:run_gui',
        ],
    },
    author='Aditya-Dobhada',
    description='Download anime from `anikoto.tv` / `anikoto.bz` / `anikoto.net` / `anikoto.cz`',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Aditya-Dobhada/anikoto',
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
    python_requires='>=3.8',
)
