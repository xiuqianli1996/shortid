try:
    from setuptools import setup
except:
    from distutils.core import setup

__version__ = '0.0.1'

with open('README.md', encoding='utf-8') as fp:
    long_description = fp.read()

setup(
    name='shortid',
    version=__version__,
    description='Short id generator',
    long_description=long_description,
    author='xiuqian li',
    author_email='981764793@qq.com',
    keywords=['shortid'],
    packages=['shortid'],
    license='MIT',
    url='https://github.com/xiuqianli1996/shortid',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ]
)