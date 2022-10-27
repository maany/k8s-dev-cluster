from setuptools import setup


setup(
    name='dev-cluster-utils',
    version='0.1',
    py_modules=['dev_cluster_utils'],
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        dev_cluster_utils=dev_cluster_utils:cli
    ''',
)