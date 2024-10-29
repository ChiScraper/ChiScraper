## ###############################################################
## LOAD MODULES
## ###############################################################
import os


## ###############################################################
## CHECK IF A FILE EXISTS
## ###############################################################
def fileExists(filepath):
  return os.path.isfile(filepath)


## ###############################################################
## CREATE A DIRECTORY IF IT DOES NOT EXIST
## ###############################################################
def createDirectory(filepath, bool_add_space=True):
  if not(os.path.exists(filepath)):
    os.makedirs(filepath)
    print(f"Successfully created folder: {filepath}")
    if bool_add_space: print(" ")
  return


## END OF HEADER FILE