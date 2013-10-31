from setuptools import setup

setup(
    name="Dispatching",
    version="1.0",
    py_modules=['dispatching',],
    test_suite='test',
    platforms='any',
    package_data={
        '': ['README.md', 'LICENSE',],
    },

    author="Nathan West",
    description="A library for overloading python functions",
    long_description=open('README.md').read(),
    license="LGPLv3",
    url="https://github.com/Lucretiel/Dispatch",

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
