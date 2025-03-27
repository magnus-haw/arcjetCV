import sys, os
from unittest import mock

sys.path.insert(0, os.path.abspath("../.."))

# run api-doc in terminal
os.system("sphinx-apidoc -fMT ../../arcjetCV -o api --templatedir=template -e")

project = "arcjetCV"
author = "arcjetCV Team"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.mathjax",
    "sphinx.ext.viewcode",
    "nbsphinx",
    "nbsphinx_link",
]

# avoid running the notebook's cells
nbsphinx_execute = "never"

myst_enable_extensions = [
    "dollarmath",
    "amsmath",
    "deflist",
    "html_admonition",
    "html_image",
    "colon_fence",
    "smartquotes",
    "replacements",
    "substitution",
    "tasklist",
]

templates_path = ["_templates"]
exclude_patterns = []

language = "python"

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "**.ipynb_checkpoints"]

MOCK_MODULES = [
    "matplotlib",
    "matplotlib.backends",
    "matplotlib.backends.backend_qtagg",
    "matplotlib.backends.backend_qt5agg",
    "matplotlib.backends.backend_agg",
    "matplotlib.figure",
    "matplotlib.pyplot",
    "matplotlib.colors",
    "matplotlib.widgets",
    "PySide6",
    "PySide6.QtWidgets",
    "PySide6.QtGui",
    "PySide6.QtCore",
    "cv2",
    "numpy",
    "pandas",
    "pyarrow",
    "sklearn",
    "sklearn.neighbors",
    "scipy",
    "segmentation-models-pytorch",
    "torch",
    "torch.nn",
    "torch.nn.functional",
    "torchvision",
]
for module_name in MOCK_MODULES:
    sys.modules[module_name] = mock.Mock()

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_logo = "../../arcjetCV/gui/logo/arcjetCV_logo_.png"
html_theme_options = {
    "logo_only": True,
    "display_version": False,
}
