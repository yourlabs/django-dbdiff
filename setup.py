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
    version='0.7.0',
    description='Database data diffing against fixtures for testing',
    author='James Pic',
    author_email='jamespic@gmail.com',
    url='https://github.com/yourlabs/django-dbdiff',
    packages=find_packages(),
    include_package_data=True,
    long_description=read('README.rst'),
    license='MIT',
    keywords='django test database fixture diff',
    install_requires=['ijson', 'json_delta', 'six'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
