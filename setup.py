from setuptools import setup, find_packages

setup(
    name="heros_notepad",
    version="0.1.0",
    author="Yoon Doohyun",
    author_email="ydh2500@gmail.com",
    description="A notepad for HEROS",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/ydh2500/heros_notepad",  # 패키지의 홈페이지 URL
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
