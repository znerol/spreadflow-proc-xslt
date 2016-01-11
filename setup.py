from setuptools import setup

setup(
    name='SpreadFlowProcXslt',
    version='0.0.1',
    description='XSLT processor for SpreadFlow metadata extraction and processing engine',
    author='Lorenz Schori',
    author_email='lo@znerol.ch',
    url='https://github.com/znerol/spreadflow-proc-xslt',
    packages=[
        'spreadflow_proc_xslt',
        'spreadflow_proc_xslt.test'
    ],
    install_requires=[
        'SpreadFlowCore',
        'defusedxml',
        'lxml'
    ],
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Twisted',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Multimedia'
    ]
)
