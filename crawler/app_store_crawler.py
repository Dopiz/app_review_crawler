import json
import urllib.request


class AppStoreCrawler(object):

    def __init__(self, app_id):
        self.app_id = app_id
        self.history_list = list()

    def load_history(self):
        with open("./crawler/app_store_history.json", 'r+') as f:
            self.history_list = json.load(f)

    def save_history(self, new_reviews):
        self.history_list = new_reviews + self.history_list
        with open("./crawler/app_store_history.json", 'r+') as f:
            json.dump(self.history_list, f)

    def crawling(self):

        self.load_history()

        url = f"https://itunes.apple.com/tw/rss/customerreviews/page=1/id={self.app_id}/sortby=mostrecent/json"
        res = json.load(urllib.request.urlopen(url))

        new_reviews = list()

        for entry in res['feed']['entry']:

            if entry['id']['label'] in self.history_list:
                break

            rating = int(entry['im:rating']['label'])

            review = {
                'id': entry['id']['label'],
                'version': entry['im:version']['label'],
                'rating': rating * '★' + (5 - rating) * '☆',
                'title': entry['title']['label'],
                'comment': entry['content']['label']
            }

            new_reviews.append(review)

        return new_reviews[::-1]
