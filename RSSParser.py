import feedparser
import crossref_commons.retrieval


def fetch_rss_entries(rss_url):
    feed = feedparser.parse(rss_url)
    entries = feed.entries
    return entries

# def getAbstract(doi):
#     api_data = requests.get(base_url + doi + mailto).json()
#     try:
#         return api_data['message']['abstract']
#     except KeyError:
#         return None

class doiHandler(object):
    def __init__(self, doi):
        self.doi = doi
    def callCrossRef(self):
        self.ref = crossref_commons.retrieval.get_publication_as_json(self.doi)
    def getMetadata(self):
        if not hasattr(self, 'ref'):
            self.callCrossRef()
        self.articleMetadata = {
            'title': self.getTitle(),
            'doi': self.doi,
            'url': self.getURL(),
            'date_published': self.getDatePublished(),
            'date_updated': self.getDateUpdated(),
            'authors': self.getAuthors(),
            'abstract': self.getAbstract()
        }
        return self.articleMetadata
    def getURL(self):
        return f"https://doi.org/{self.doi}"
    def getAbstract(self):
        try:
            return self.ref['abstract']
        except KeyError:
            return None
    def getTitle(self):
        try:
            return self.ref['title']
        except KeyError:
            return None
    def getDatePublished(self):
        try:
            return self.ref['date-time']
        except KeyError:
            return None
    def getDateUpdated(self):
        try:
            return self.ref['issued']['date-time']
        except KeyError:
            return None
    def getAuthors(self):
        try:
            return self.ref['author']
        except KeyError:
            return None
    def getPublisher(self):
        try:
            return self.ref['publisher']
        except KeyError:
            return None
    
     

def getAbstract(doi):
    try:
        ref = crossref_commons.retrieval.get_publication_as_json(doi)
        return ref['abstract']
    except KeyError:
        return None
    ref = crossref_commons.retrieval.get_publication_as_json(doi)

def main():
    rss_url = 'https://opg.optica.org/rss/ao_feed.xml'  # Replace with the actual RSS feed URL
    import requests

    entries = fetch_rss_entries(rss_url)
    # print(entries[0]['dc_identifier'])
    abstracts = 0 
    doi = entries[0]['dc_identifier'].replace('doi:', '')
    for entry in entries:
        doi = entry['dc_identifier'].replace('doi:', '')
        abstract = getAbstract(doi)
        if abstract:
            abstracts += 1
        else:
            ref = crossref_commons.retrieval.get_publication_as_json(doi)
            print(ref)


    
    print(f"Total number of entries: {len(entries)}")
    print(f"Total number of abstracts: {abstracts}")


# doi = "10.1186/1758-2946-4-12" # example


if __name__ == "__main__":
    main()