## ###############################################################
## HELPER FUNCTIONS
## ###############################################################
def shortenList(list_elems, max_elems=5):
  list_sub_elems = [
    str(elem)  if (elem_index <  max_elems+1)
    else "..." if (elem_index == max_elems+1)
    else None
    for elem_index, elem in enumerate(list_elems)
  ]
  return [
    elem
    for elem in list_sub_elems
    if elem is not None
  ]

def joinList(list_elems, str_sep="", bool_pre=False):
  list_elems = map(str, list_elems)
  if bool_pre: str_pre = str_sep
  else:        str_pre = ""
  return str_pre + str_sep.join(list_elems)


## ###############################################################
## APPLY SEARCH CRITERIA
## ###############################################################
def doesTextContainAllKeywords(phrase, list_search_keywords):
  if len(list_search_keywords) == 0: return False
  list_bools = []
  for keyword in list_search_keywords:
    if isinstance(keyword, str):
      bool_term_contained = keyword.lower() in phrase
      list_bools.append(bool_term_contained)
    elif isinstance(keyword, list):
      list_bools.append(
        doesTextContainAnyKeywords(phrase, keyword)
      )
  return all(list_bools)

def doesTextContainAnyKeywords(phrase, list_search_keywords):
  if len(list_search_keywords) == 0: return False
  list_bools = []
  for keyword in list_search_keywords:
    if isinstance(keyword, str):
      bool_term_contained = keyword.lower() in phrase.lower()
      list_bools.append(bool_term_contained)
      if bool_term_contained: break
    elif isinstance(keyword, list):
      list_bools.append(
        doesTextContainAllKeywords(phrase, keyword)
      )
  return any(list_bools)

def meetsSearchCriteria(phrase, list_search_conditions):
  return doesTextContainAnyKeywords(phrase, list_search_conditions)


## ###############################################################
## PRINT SEARCH CRITERIA
## ###############################################################
def lolsToSetNotation(list_elems, set_level=0):
  while isinstance(list_elems, list) and (len(list_elems) == 1):
    list_elems = list_elems[0]
    set_level += 1
  if not isinstance(list_elems, list): return f"'{list_elems}'"
  if set_level % 2 == 1: operator = " AND "
  else: operator = " OR "
  return operator.join(
    f"({lolsToSetNotation(elem, set_level+1)})"
    if isinstance(elem, list)
    else f"'{elem}'"
    for elem in list_elems
  )

def printSearchCriteria(dict_search, bool_search_authors=False):
  list_keywords_include = dict_search["list_keywords_include"]
  list_keywords_exclude = dict_search["list_keywords_exclude"]
  list_authors          = dict_search["list_authors"]
  print("> including articles with phrases:")
  print(lolsToSetNotation(list_keywords_include))
  print(" ")
  if len(list_keywords_exclude) > 0:
    print("> excluding articles with phrases:")
    print(lolsToSetNotation(list_keywords_exclude))
    print(" ")
  if len(list_authors) > 0:
    print("> including articles with authors:", end="")
    print(joinList(list_authors, str_sep="\n\t- ", bool_pre=True))
    print(" ")
  return


## END OF HEADER FILE