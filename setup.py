from setuptools import setup, find_packages

VERSION = '0.0.1' 
DESCRIPTION = 'QM/MM python package'
LONG_DESCRIPTION = 'Quantum mechanics / molecular mechanics python package'

# Setting up
setup(
       # the name must match the folder name 'verysimplemodule'
        name="pyQMMM", 
        version=VERSION,
        author="David W. Kastner",
        author_email="<kastner@mit.edu>",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=[], # add any additional packages that 
        # needs to be installed along with your package. Eg: 'caer'
        
        keywords=['python', 'qm/mm', 'quantum', 'molecular dynamics', 'amber'],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Education",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
        ]
)