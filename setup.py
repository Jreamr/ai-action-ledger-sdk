from setuptools import setup, find_packages

setup(
    name="action-ledger",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.28.0",
    ],
    extras_require={
        "langchain": ["langchain>=0.1.0"],
    },
    author="Your Name",
    description="SDK for AI Action Ledger - tamper-evident logging for AI actions",
    python_requires=">=3.9",
)
```

Save.

---

Last one — right-click on **ai-action-ledger-sdk** → **New File** → name it:
```
README.md