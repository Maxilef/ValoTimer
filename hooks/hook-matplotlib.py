# hook-matplotlib.py
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# Collect all submodules of matplotlib
hiddenimports = collect_submodules('matplotlib')

# Collect data files for matplotlib
datas = collect_data_files('matplotlib', subdir='mpl-data')
