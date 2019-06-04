from setuptools import setup

setup(name='o2_scrap',
    version='0.5.2',
    description='library to get data-usage and plan details from O2 germany mobile contracts',
    url='http://github.com/grindsa/o2_scrap',
    author='grindsa',
    author_email='grindelsack@gmail.com',
    license='GPL',
    packages=['o2_scrap'],
    install_requires=[
        'selenium',
        'bs4',
        'six',
        'lxml'
    ],    
    classifiers = [
        'Programming Language :: Python',
        'Development Status :: 4 - Beta',
        'Natural Language :: German',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],        
    zip_safe=False)