import os
os.system("clear")


## ###############################################################
## HELPER FUNCTIONS
## ###############################################################
def printHeading(str):
  print(str)
  print("=" * len(str))

def containsAllKeywords(phrase, list_search_terms):
  if len(list_search_terms) == 0: return False
  list_bools = []
  for term in list_search_terms:
    if type(term) is str:
      term_bool = (term in phrase)
      list_bools.append(term_bool)
    elif type(term) is list:
      list_bools.append(
        containsAnyKeyword(phrase, term)
      )
  return all(list_bools)

def containsAnyKeyword(phrase, list_search_terms):
  if len(list_search_terms) == 0: return False
  list_bools = []
  for term in list_search_terms:
    if type(term) is str:
      term_bool = (term in phrase)
      list_bools.append(term_bool)
      if term_bool: break
    elif type(term) is list:
      list_bools.append(
        containsAllKeywords(phrase, term)
      )
  return any(list_bools)


## ###############################################################
## DEMO PROGRAM
## ###############################################################
def main():
  list_animals    = [ "fox", "turtle", "cow" ]
  list_actions    = [ "jumped", "leaped" ]
  list_objects    = [ "moon", "log", "river" ]
  list_phrases    = []
  for animal in list_animals:
    for action in list_actions:
      for object in list_objects:
        list_phrases.append(f"the {animal} {action} over the {object}")
  printHeading("List of phrases:")
  print("\n".join(list_phrases))
  print(" ")
  list_search_terms = [
    # ## where: "turtle" appears
    # "turtle",

    # ## where: "cow" and "river" appear
    # [ "cow", "river" ],

    ## where: "fox" and ("jumped" or "river") appears
    [ "fox", ["jumped", "river"] ],

    # ## where: ("fox" or "cow") and "jumped" and ("moon" or "log") appears
    # [ ["fox", "cow"], "jumped", ["moon", "log"] ],
  ]
  printHeading("List of phrases that met the search conditions:")
  for phrase in list_phrases:
    if containsAnyKeyword(phrase, list_search_terms):
      print(phrase)
      continue


## ###############################################################
## RUN DEMO
## ###############################################################
if __name__ == "__main__":
  main()


## END OF DEMO PROGRAM