import sys

from src.headers import WWLists


## ###############################################################
## HELPER FUNCTION
## ###############################################################
def printHeading(str):
  print(str)
  print("=" * len(str))
  return


## ###############################################################
## DEMO PROGRAM
## ###############################################################
def main():
  list_phrases    = []
  for animal in [ "fox", "turtle", "cow" ]:
    for action in [ "jumped", "leaped" ]:
      for object in [ "moon", "log", "river" ]:
        list_phrases.append(f"the {animal} {action} over the {object}")
  printHeading("List of phrases:")
  print("\n".join(list_phrases))
  print(" ")
  ## "fox" AND ("jumped" OR "river")
  list_search_conditions = [
    [ "fox", ["jumped", "river"] ]
  ]
  printHeading("Search condition:")
  print(WWLists.lolsToSetNotation(list_search_conditions))
  print(" ")
  printHeading("List of phrases that met the search conditions:")
  for phrase in list_phrases:
    if WWLists.meetsSearchCriteria(phrase, list_search_conditions):
      print(phrase)


## ###############################################################
## DEMO ENTRY POINT
## ###############################################################
if __name__ == "__main__":
  main()
  sys.exit()


## END OF DEMO PROGRAM