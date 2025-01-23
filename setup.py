# -*- coding: utf-8 -*-
"""
Setup configuration for scrapy-rabbitmq package
"""

from setuptools import setup, find_packages
import io

# 使用 io.open 以 UTF-8 编码读取 README
with io.open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='scrapy-rabbitmq',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'scrapy>=2.5.0',
        'pika>=1.3.0',
        'redis>=4.0.0',
    ],
    author='Your Name',
    author_email='your.email@example.com',
    description='A RabbitMQ-based distributed crawler using Scrapy',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/scrapy-rabbitmq',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Framework :: Scrapy',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords=['scrapy', 'rabbitmq', 'distributed', 'crawler', 'spider', 'scraping'],
    python_requires='>=3.7',
    project_urls={
        'Bug Reports': 'https://github.com/yourusername/scrapy-rabbitmq/issues',
        'Source': 'https://github.com/yourusername/scrapy-rabbitmq',
    },
    entry_points={
        'console_scripts': [
            'scrapy-rabbitmq=scrapy_rabbitmq.spiders:main',
        ],
    },
    package_data={
        'scrapy_rabbitmq': ['*.json', '*.conf'],
    },
    include_package_data=True,
    zip_safe=False,
)
