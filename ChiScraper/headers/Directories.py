config  = "configs"
mdfiles = "mdfiles"
pdfs    = "pdfs"


import os
# This grabs the root directory of the project. I.e., one level above the headers directory.
root_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Construct the full path to each directory

directory_config  = os.path.join(root_directory, config)
directory_mdfiles = os.path.join(root_directory, mdfiles)
directory_pdfs    = os.path.join(root_directory, pdfs)

print(f"Root directory: {root_directory}")
print(f"Config directory: {directory_config}")
print(f"Markdown files directory: {directory_mdfiles}")
print(f"PDFs directory: {directory_pdfs}")