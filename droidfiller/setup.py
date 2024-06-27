from setuptools import setup

setup(
   name='droidfiller',
   version='1.0',
   description='A droidfiller module for better GUI testing',
   author='greenmon',
   author_email='greenmon@kaist.ac.kr',
   packages=['droidfiller'],
   install_requires=['openai', 'python-dotenv'], 
)