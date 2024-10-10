
import feedparser


class RSSFeed(object):
    def __init__(self, rss_url):
        self.rss_url = rss_url
        self.getEntries()
    def getEntries(self):
        feed = feedparser.parse(self.rss_url)
        self.entries = feed.entries
        return self.entries
    def getEntry(self, index):
        return self.entries[index]
    def countEntries(self):
        return len(self.entries)
    def getEntryDOI(self, index):
        try:
            self.getEntry(index)['dc_identifier'].replace('doi:', '')
        except KeyError:
            print(f"Unexpected Format")
            return None


