import requests


class AppStoreCrawler(object):

    def __init__(self, app_id, history_list):
        self.app_id = app_id
        self.history_list = history_list

    def crawling(self):

        url = (f"https://itunes.apple.com/tw/rss/customerreviews/page=1/"
               f"id={self.app_id}/sortby=mostrecent/json")

        res = requests.get(url).json()

        new_reviews = list()

        for entry in res['feed']['entry']:

            if entry['id']['label'] in self.history_list:
                break

            rating = int(entry['im:rating']['label'])
            rat = rating * "★" + (5 - rating) * "☆"
            comment = entry['content']['label']
            if len(comment) > 100:
                comment = comment[:100]

            review = {
                'id': entry['id']['label'],
                'version': entry['im:version']['label'],
                'rating': rating,
                'rat': rat,
                'title': entry['title']['label'],
                'comment': comment
            }

            new_reviews.append(review)

        return new_reviews[::-1]
