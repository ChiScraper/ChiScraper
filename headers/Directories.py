import os
# The root is the parent directory of the current file
directory_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(f"Root directory: {directory_root}")


directory_config  = os.path.join(directory_root, "configs")
directory_mdfiles = os.path.join(directory_root, "mdfiles")
directory_pdfs    = os.path.join(directory_root, "pdfs")
directory_webApp  = os.path.join(directory_root,"scripts", "WebAppConfig")