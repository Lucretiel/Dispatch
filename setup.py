from setuptools import setup

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst', 'markdown')
except (ImportError, FileNotFoundError, RuntimeError):
    #ImportError: pypandoc failed to import
    #FileNotFoundError: couldn't launch pandoc
    #RuntimeError: failed to convert
    long_description = open('README.md').read()

setup(
    name="Dispatching",
    version="1.4.0",
    py_modules=['dispatching',],
    test_suite='test',
    platforms='any',

    author="Nathan West",
    description="A library for overloading python functions",
    long_description=long_description,
    license="LGPLv3",
    url="https://github.com/Lucretiel/Dispatch",

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
