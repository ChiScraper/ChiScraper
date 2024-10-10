import crossref_commons.retrieval


doi = '10.1364/AO.531095'
ref = crossref_commons.retrieval.get_publication_as_json(doi)

print(ref['abstract'])
