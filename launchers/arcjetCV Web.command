#!/bin/bash
# Double-click on macOS to launch arcjetCV Web in your browser.
# Activates the "arcjetcv" conda environment if conda is available.
for c in "$HOME/miniconda3" "$HOME/anaconda3" "$HOME/miniforge3" "/opt/homebrew/Caskroom/miniconda/base"; do
  [ -f "$c/etc/profile.d/conda.sh" ] && source "$c/etc/profile.d/conda.sh" && break
done
command -v conda >/dev/null && conda activate arcjetcv 2>/dev/null
if ! python -c "import flask" 2>/dev/null; then
  echo "Installing Flask (one time)..."; python -m pip install flask
fi
python -m arcjetCV.webapp "$@"
