import sys
import os
from unittest import mock

# Add the root directory of your package to the system path
sys.path.insert(0, os.path.abspath("../../arcjetCV"))  # Adjust path if necessary

# Liste des modules à mocker
MOCK_MODULES = [
    "matplotlib",
    "matplotlib.backends",
    "matplotlib.backends.backend_qt5agg",
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
    "scipy",
    "segmentation-models-pytorch",
    "torch",
    "torch.nn",
    "torch.nn.functional",
    "torchvision",
]

for module_name in MOCK_MODULES:
    sys.modules[module_name] = mock.Mock()

# Configurer le backend Matplotlib pour éviter les erreurs
import matplotlib

matplotlib.use("Agg")

# Configuration Sphinx
project = "arcjetCV"
author = "arcjetCV Team"

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.mathjax",
    "sphinx.ext.viewcode",
    "nbsphinx",
    "nbsphinx_link",
]

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
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "**.ipynb_checkpoints"]

html_theme = "sphinx_rtd_theme"
html_logo = "../../arcjetCV/gui/logo/arcjetCV_logo_.png"
html_theme_options = {
    "logo_only": True,
    "display_version": False,
}
