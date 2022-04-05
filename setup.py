from setuptools import setup

readme = open('README.rst').read()

setup(name='drf_dynamic_fields',
      version='0.4.0',
      description='Dynamically return subset of Django REST Framework serializer fields',
      author='Danilo Bargen',
      author_email='mail@dbrgn.ch',
      url='https://github.com/dbrgn/drf-dynamic-fields',
      packages=['drf_dynamic_fields'],
      zip_safe=True,
      include_package_data=True,
      license='MIT',
      keywords='drf restframework rest_framework django_rest_framework serializers',
      long_description=readme,
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3',
          'Framework :: Django',
          'Environment :: Web Environment',
      ],
)
