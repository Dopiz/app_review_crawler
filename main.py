from bot.app_store_crawler import AppStoreCrawler
from bot.google_play_crawler import GooglePlayCrawler
from bot.line_bot import LineBot
from bot.slack_bot import SlackBot
from history.history import History
from options import app_list, line_info, slack_info


class ReviewCrawler(object):

    def __init__(self, app_info):
        self.new_reviews = None
        self.app_name = app_info['app_name']
        self.app_id = app_info['app_id']
        self.package_name = app_info['package_name']

    def notify(self, token, channel, platform):

        if channel is None:
            return

        if platform == "Line":
            bot = LineBot(token)
        elif platform == "Slack":
            bot = SlackBot(token)

        if bot.notify(channel, self.new_reviews, self.store):
            self.history.save()

    def crawling(self, store):

        self.store = store

        if self.store == "App Store":
            self.history = History(f"{self.app_name}_app_store")
            self.crawler = AppStoreCrawler(self.app_id, self.history.history_list)
        elif self.store == "Google Play":
            self.history = History(f"{self.app_name}_google_play")
            self.crawler = GooglePlayCrawler(self.package_name, self.history.history_list)

        self.new_reviews = self.crawler.crawling()
        print(f"➤ {self.store} - Get {len(self.new_reviews)} new comment !")

        new_reviews_id = [review['id'] for review in self.new_reviews]
        self.history.history_list = new_reviews_id + self.history.history_list


if __name__ == '__main__':

    for app in app_list:

        bot = ReviewCrawler(app)

        bot.crawling("App Store")
        bot.notify(line_info['token'], line_info['channel'], "Line")
        bot.notify(slack_info['token'], slack_info['channel'], "Slack")

        bot.crawling("Google Play")
        bot.notify(line_info['token'], line_info['channel'], "Line")
        bot.notify(slack_info['token'], slack_info['channel'], "Slack")
