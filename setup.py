from setuptools import setup

setup(
    name='kickup',
    packages=['kickup'],
    include_package_data=True,
    install_requires=[
        'flask',
        #TODO: how to combine with requirements.txt ?
    ],
)