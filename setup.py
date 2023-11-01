from setuptools import setup, find_packages
import os


# Utility function to read the README file.
# Used for the long_description. It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='django-dbdiff',
    version='0.9.5',
    description='Database data diffing against fixtures for testing',
    author='James Pic',
    author_email='jamespic@gmail.com',
    url='https://github.com/yourlabs/django-dbdiff',
    packages=find_packages(),
    include_package_data=True,
    long_description=read('README.rst'),
    license='MIT',
    keywords='django test database fixture diff',
    install_requires=['ijson', 'json_delta'],
    entry_points={'pytest11': ['dbdiff = dbdiff.plugin']},
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Framework :: Django',
        'Framework :: Django :: 3.2',
        'Framework :: Django :: 4.0',
        'Framework :: Django :: 4.1',
        'Framework :: Django :: 4.2',
        'Framework :: Django :: 5.0',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
