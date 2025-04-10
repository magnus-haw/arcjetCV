import sys
import os
from unittest import mock

# Add the root directory of your package to the system path
sys.path.insert(0, os.path.abspath("../../arcjetCV"))  # Adjust path if necessary

# List of modules to mock
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
    "scipy.sparse",
    "scipy.linalg",
    "scipy.stats",
    "scipy.special",
    "scipy.optimize",
    "scipy.integrate",
    "segmentation_models_pytorch",
    "torch",
    "torch.nn",
    "torch.nn.functional",
    "torchvision",
]

# Mock each module and its submodules
for module_name in MOCK_MODULES:
    sys.modules[module_name] = mock.Mock()

# Configure the Matplotlib backend to avoid errors
import matplotlib
matplotlib.use("Agg")

# Sphinx Configuration
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