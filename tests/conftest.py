import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# perf_bot.py reads branches.json / steady_states.json from the working
# directory when it is imported, so run from the project root.
os.chdir(ROOT)
sys.path.insert(0, ROOT)
os.environ.setdefault("MPLBACKEND", "Agg")  # game.py imports matplotlib
