# python-template-repo
Python template repository: A ready-to-use template repository with generic Github action workflows, directory structure and files. 

## Setup sphinx documentation

1. Install sphinx requirements (already in requirements.txt)

```bash
pip install -r requirements.txt
```

2 . Create sphinx documentation base files

```bash
sphinx-quickstart         
sphinx-apidoc -o docs src
```

3. Build sphinx documentation

```bash
cd docs
make html
```

or 

```bash
cd docs
sphinx-build docs build    
```