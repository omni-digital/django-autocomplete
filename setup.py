from setuptools import setup, find_packages

from autocomplete import get_version
setup(
    name = "django-autocomplete",
    packages = find_packages(),
    include_package_data=True,
    version = get_version(),
    description = "Django autocomplete widgets and views.",
    author = "Incuna Ltd",
    author_email = "admin@incuna.com",
    url = "http://incuna.com/",
    # download_url = "http://chardet.feedparser.org/download/python3-chardet-1.0.1.tgz",
    # long_description = """"""
)
