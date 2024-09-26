#!/usr/bin/env python3


## ###############################################################
## LOAD MODULES
## ###############################################################
import sys, arxiv
from MyLibrary import HelperFuncs
import yaml

## ###############################################################
## OUTPUT DIRECTORY
## ###############################################################

with open('config.yaml', 'r') as config_file:
    config = yaml.safe_load(config_file)
DIRECTORY_OUTPUT = config['output_directory']


## ###############################################################
## ARXIV ID
## ###############################################################
def getUserInput():
  parser = HelperFuncs.MyParser(description="Calculate kinetic and magnetic energy spectra.")
  args_req = parser.add_argument_group(description="Required processing arguments:")
  args_req.add_argument("-id", type=str, required=True, help="type: %(type)s")
  args = vars(parser.parse_args())
  return args["id"]


## ###############################################################
## MAIN PROGRAM
## ###############################################################
def main():
  arxiv_id = getUserInput()
  HelperFuncs.createFolder(DIRECTORY_OUTPUT)
  client = arxiv.Client()
  search = arxiv.Search(id_list=[arxiv_id])
  article = next(client.results(search), None)
  if article is None:
    print(f"Error: the arXiv article '{arxiv_id}' does not exist.")
    return
  HelperFuncs.printArticle(article)
  filepath_file = f"{DIRECTORY_OUTPUT}/{arxiv_id}.md"
  if HelperFuncs.fileExists(filepath_file):
    print(f"Note: this arXiv article has already been saved:\n{filepath_file}\n")
  bool_save = input("Do you want to save this article? (y/n): ")
  if bool_save.lower() != "y": return
  config_tag = input("Enter a config tag: ")
  if config_tag == "":
    print("Error: config tag cannot be empty.")
    return
  if " " in config_tag:
    print("Error: config tag cannot contain spaces.")
    return
  HelperFuncs.saveArticle(
      article          = article,
      directory_output = DIRECTORY_OUTPUT,
      config_tag       = f"#{config_tag}"
    )
  print(f"Saved: {filepath_file}")


## ###############################################################
## RUN PROGRAM
## ###############################################################
if __name__ == "__main__":
  main()
  sys.exit()


## END OF PROGRAM