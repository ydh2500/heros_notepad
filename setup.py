from setuptools import setup, find_packages

setup(
    name="heros_notepad",
    version="0.1.0",
    author="Yoon Doohyun",
    author_email="dhyoon@withtech.co.kr",
    description="A notepad for HEROS",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="http://192.168.0.203:7990/projects/HERO/repos/py_notepad/browse",  # 패키지의 홈페이지 URL
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "requests",
        "pyqt5",
    ],
    entry_points={
        'console_scripts': [
            'py-notepad=py_notepad.main:main',  # main.py의 main 함수를 진입점으로 설정
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',
)
