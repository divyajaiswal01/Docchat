import os
import sys

# Ensures `from services.chunker import ...` etc. work when pytest is run
# from the backend/ folder, regardless of pytest's rootdir auto-detection.
sys.path.insert(0, os.path.dirname(__file__))
