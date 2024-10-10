
import requests
from datetime import datetime

class Journal:
    def __init__(self, email,issn):
        self.base_url = "https://api.crossref.org/journals"
        self.email = email
        self.issn = issn

    def get_journal_dois(self, start_date, end_date, rows=20):
        filter = f"filter=from-pub-date:{start_date},until-pub-date:{end_date}&rows={rows}&select=DOI"
        query_url = f"{self.base_url}/{self.issn}/works?{filter}&mailto={self.email}"
        dois = []
        doi_data = requests.get(query_url).json()
        if doi_data['status'] == 'ok':
            for item in doi_data['message']['items']:
                dois.append(item['DOI'])
        else:
            print("Error retrieving DOIs")
            print(f"Status: {doi_data['status']}")
            print(f"Message: {doi_data['message']}")

        return dois
    
    def get_journal_metadata(self, start_date, end_date, rows=20):
        filter = f"filter=from-pub-date:{start_date},until-pub-date:{end_date}&rows={rows}"
        query_url = f"{self.base_url}/{self.issn}/works?{filter}&mailto={self.email}"
        articles = []
        request_data = requests.get(query_url).json()
        if request_data['status'] == 'ok':
            for item in request_data['message']['items']:
                item = dict(item)
                articles.append(self.format_data(item))
        else:
            print("Error retrieving DOIs")
            print(f"Status: {request_data['status']}")
            print(f"Message: {request_data['message']}")

        return articles

    def format_data(self, article):
        authors_RAW = article.get('author', None)
        authors = []
        if authors_RAW:
            for author in authors_RAW:
                authors.append(author['given'] + " " + author['family'])
        formatted_data = {
            'title': article.get('title', [''])[0] if article.get('title') else None,
            'doi': article.get('DOI', None),
            'url': f"https://doi.org/{article.get('DOI', '')}" if article.get('DOI') else None,
            'date_published': article.get('created', {}).get('date-time', None),
            'date_updated': article.get('issued', {}).get('date-time', None),
            'authors': authors,
            'abstract': article.get('abstract', None)
        }
        return formatted_data
        
    def validate_date(self, date_string):
        try:
            datetime.strptime(date_string, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def extract_dois(self, start_date, end_date,max_rows=100):
        if not self.validate_date(start_date) or not self.validate_date(end_date):
            print("Invalid date format. Please use YYYY-MM-DD.")
            return []
        
        return self.get_journal_dois(start_date, end_date, rows=max_rows)

def test():
    email = "cameron.jones@anu.edu.au"
    applied_optics_issn = "2155-3165"
    start_date = "2024-09-01"
    end_date   = "2024-09-28"
    AppliedOptics = Journal(email,applied_optics_issn)
    articles = AppliedOptics.get_journal_metadata(start_date, end_date,5)
    for article in articles:
        print("\n")
        print(article["title"])
        print(article["doi"])
        print(article["url"])
        print(article["date_published"])
        print(article["date_updated"])
        print(article["authors"])
        print("ABSTRACT:")
        print(article["abstract"])

if __name__ == "__main__":
    test()
