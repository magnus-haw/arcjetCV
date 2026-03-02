# Build the documentation locally (UNIX only)

## Primary documentation: django-wiki

The canonical docs now live in the django-wiki instance under `wiki_site/`. Follow `wiki_site/README.md` to spin it up locally and use the web UI to add or edit pages. This is the preferred place for all updates.

## Legacy Sphinx build

The Sphinx documentation (used for static HTML/PDF exports) is generated automatically by ReadTheDocs at every main branch commit. The main commands that tell Sphinx how to compile the documentation are inside `docs/source/conf.py`, which is called by the Makefile, whereas the main layout of the different webpages is controlled by `index.rst`.

To compile the legacy docs locally, create a dedicated conda environment:

```bash
conda env create --file sphinx_env.yml
conda activate sphinx_rtd
make html
```

This creates the documentation inside the `docs/build/html` folder (double-click `index.html` to open it in a browser). Alternatively, the `make latex` command compiles a PDF file, which serves as the user manual. Finally, you can use `make clean` to clear previous builds.

## MkDocs wiki

MkDocs powers a lightweight wiki using the pages in the `mkdocs/` folder and configuration in `mkdocs.yml`. To build or serve it locally:

```bash
pip install -r mkdocs/requirements.txt
mkdocs serve
```
