import os
from pathlib import Path
from src.headers import WWFnFs

directory_root = Path(__file__).resolve().parents[2]
directory_config  = WWFnFs.contstructPath(directory_root, "configs")
directory_mdfiles = WWFnFs.contstructPath(directory_root, "mdfiles")
directory_pdfs    = WWFnFs.contstructPath(directory_root, "pdfs")
directory_webApp  = WWFnFs.contstructPath(directory_root, "src","scripts", "WebAppConfig")

