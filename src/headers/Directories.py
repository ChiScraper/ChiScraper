import os
from pathlib import Path

directory_root = Path(__file__).resolve().parents[2]
directory_config  = os.path.join(directory_root, "configs")
directory_mdfiles = os.path.join(directory_root, "mdfiles")
directory_pdfs    = os.path.join(directory_root, "pdfs")

