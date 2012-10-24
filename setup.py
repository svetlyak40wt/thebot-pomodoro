from setuptools import setup

setup(
    name='thebot-pomodoro',
    version='0.1.1',
    description='A simple productivity timer.',
    keywords='thebot pomodoro plugin',
    license = 'New BSD License',
    author="Alexander Artemenko",
    author_email='svetlyak.40wt@gmail.com',
    url='http://github.com/svetlyak40wt/thebot-pomodoro/',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Plugins',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
    ],
    py_modules=['thebot_pomodoro'],
    install_requires=[
        'thebot>=0.2.0',
        'times',
    ],
)
