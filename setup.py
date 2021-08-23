import os
from setuptools import setup, find_packages

version = '1.2.6'

with open('README.md') as readme:
    long_description = readme.read()

def recursive_requirements(requirement_file, libs, links, path=''):
    if not requirement_file.startswith(path):
        requirement_file = os.path.join(path, requirement_file)
    with open(requirement_file) as requirements:
        for requirement in requirements.readlines():
            if requirement.startswith('-r'):
                requirement_file = requirement.split()[1]
                if not path:
                    path = requirement_file.rsplit('/', 1)[0]
                recursive_requirements(requirement_file, libs, links,
                                       path=path)
            elif requirement.startswith('-f'):
                links.append(requirement.split()[1])
            elif requirement.startswith('--allow'):
                pass
            else:
                libs.append(requirement)

libraries, dependency_links = [], []
recursive_requirements('requirements.txt', libraries, dependency_links)

setup(name='django-cas-sso',
      version=version,
      install_requires=libraries,
      dependency_links=dependency_links,
      description="Django Cas SSO Client (inherited from django-cas)",
      long_description=long_description,
      long_description_content_type='text/markdown',
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "Environment :: Console",
          "Intended Audience :: End Users/Desktop",
          "Natural Language :: English",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
          "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries",
          "Topic :: Utilities",
          "License :: OSI Approved :: BSD License",
          ],
      keywords=['django', 'cas', 'sso'],
      author='di-dip-unistra',
      author_email='di-dip@unistra.fr',
      maintainer='di-dip-unistra',
      maintainer_email='di-dip@unistra.fr',
      url='http://github.com/unistra/django-cas/',
      download_url='http://pypi.python.org/pypi/django-cas-sso',
      license='MIT',
      entry_points={},
      packages=find_packages(),
      include_package_data=True,
      zip_safe=True,
      )
