## ###############################################################
## LOAD MODULES
## ###############################################################
import json, yaml


## ###############################################################
## READING FILES
## ###############################################################
def readFile(filepath_file, expected_file_extension):
  if not(filepath_file.endswith(expected_file_extension)):
      raise ValueError(f"Error: File must use a '{expected_file_extension}' extension. Input filepath: {filepath_file}")
  try:
    if expected_file_extension == ".json":
      with open(filepath_file, "r") as fp:
        file_content = json.load(fp)
    elif (expected_file_extension == ".txt") or (expected_file_extension == ".md"):
      with open(filepath_file, "r", encoding="utf-8") as fp:
        file_content = fp.read()
    elif expected_file_extension == ".yaml":
      with open(filepath_file, "r") as yaml_file:
        file_content = yaml.safe_load(yaml_file)
    else: raise Exception(f"Error: Requested file-format `{expected_file_extension}` is not implemented.")
  except Exception as e: raise IOError(f"Error reading file {filepath_file}: {e}")
  return file_content

def readTextFile(filepath):
  return readFile(filepath, expected_file_extension=".txt")

def readMarkdownFile(filepath):
  return readFile(filepath, expected_file_extension=".md")

def readYamlFile(filepath):
  return readFile(filepath, expected_file_extension=".yaml")

def readSearchCriteria2Dict(directory, config_name):
  dict_config = readFile(f"{directory}/{config_name}.json", ".json")
  list_missing_keys = []
  for key in [
      "list_authors",
      "list_categories",
      "list_keywords_exclude",
      "list_keywords_include"
    ]:
    if key not in dict_config: list_missing_keys.append(f"'{key}'")
  if len(list_missing_keys) > 0:
    print(f"The following config keys are missing:")
    print("\t", ", ".join(list_missing_keys), "\n")
    raise Exception("Error: Config file is missing search keys")
  return dict_config


## ###############################################################
## PRINT DICTIONARY CONTENTS
## ###############################################################
def printDict(input_dict, indent=0):
  def _printWithIndent(indent, key, value, bool_print_type=True):
    if bool_print_type: print(" " * indent + f"'{key}' ({type(value).__name__}) : {value}")
    else:               print(" " * indent + f"'{key}' : {value}")
  def _printDict(d, indent):
    for key in sorted(d.keys()):
      value = d[key]
      if isinstance(value, dict):
        _printWithIndent(indent, key, "[dict]", False)
        _printDict(value, indent+4)
      elif isinstance(value, list):
        _printWithIndent(indent, key, "[list]", False)
        for idx, item in enumerate(value):
          if isinstance(item, dict) or isinstance(item, list):
            _printDict(item, indent+4)
          else: _printWithIndent(indent+4, f"{idx}->", item)
      else: _printWithIndent(indent, key, value)
  _printDict(input_dict, indent)
  return


## END OF HEADER FILE