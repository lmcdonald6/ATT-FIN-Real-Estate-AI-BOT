from setuptools import setup, find_packages

setup(
    name="real-estate-ai-bot",
    version="1.0.0",
    description="An intelligent real estate analysis bot with comprehensive property insights",
    author="Lewis McDaniel",
    packages=find_packages(),
    install_requires=[
        'python-dateutil>=2.8.2',
        'pytz>=2023.3',
        'aiohttp>=3.8.0',
        'python-dotenv>=1.0.0',
        'requests>=2.31.0',
        'numpy>=1.24.0',
        'pandas>=2.0.0',
        'scikit-learn>=1.3.0',
        'beautifulsoup4>=4.12.0',
        'lxml>=4.9.0',
        'aiosqlite>=0.19.0',
        'tqdm>=4.65.0',
        'colorama>=0.4.6',
        'plotly>=5.15.0',
        'matplotlib>=3.7.1',
        'firebase-admin>=6.2.0',
        'google-cloud-firestore>=2.11.1',
        'selenium>=4.10.0',
        'webdriver_manager>=4.0.0',
        'pyyaml>=6.0.1',
    ],
    extras_require={
        'dev': [
            'pytest>=7.4.0',
            'pytest-asyncio>=0.21.1',
            'pytest-cov>=4.1.0',
        ],
    },
    python_requires='>=3.8',
)
