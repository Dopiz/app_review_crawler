import slack
from flask import Flask
from linebot import LineBotApi
from linebot.models import (BoxComponent, BubbleContainer, ButtonComponent,
                            CarouselContainer, FlexSendMessage, ImageComponent,
                            MessageAction, SeparatorComponent, SpacerComponent,
                            TextComponent, URIAction)

from crawler.app_store_crawler import AppStoreCrawler
from crawler.google_play_crawler import GooglePlayCrawler
from gsc import GoogleSheetClient

app = Flask(__name__)
sheet_name = "Testing"


class SlackBot(object):
    
    def __init__(self, token):
        self.slack_bot_api = slack.WebClient(token)

    def notify(self, channels, review, platform):
        
        if platform == "App Store":
            content = (f" App Store 新的評論來囉～\n"
                        f"版本：{review['version']}\n"
                        f"評分：{review['rating']}\n"
                        f"標題：{review['title']}\n"
                        f"評論：{review['comment']}")
        else:
            content = (f"➤ Google play 新的評論來囉～\n"
                        f"裝置：{review['product_name']}\n"
                        f"系統：{review['os_version']}\n"
                        f"版本：{review['version']}\n"
                        f"評分：{review['rating']}\n"
                        f"評論：{review['comment']}")

        for channel in channels:
            self.slack_bot_api.chat_postMessage(
                channel=channel, text=content)


class LineBot(object):

    def __init__(self, token):
        self.line_bot_api = LineBotApi(token)

    def flex_message_builder(self, reviews, platform):

        contents = list()

        for review in reviews:
            # Line Flex Message
            bubble = BubbleContainer(
                direction='ltr',
                header=BoxComponent(
                    layout='vertical',
                    contents=[
                        TextComponent(
                            text=" App Store 評論來囉！", weight='bold', size='md', color='#0099e5')
                    ]
                ),
                hero=ImageComponent(
                    url='https://i.imgur.com/dp5OCjl.jpg',
                    size='full',
                    aspect_ratio='5:3',
                    aspect_mode='cover'
                ),
                body=BoxComponent(
                    layout='vertical',
                    contents=[
                        TextComponent(
                            text=review['title'], wrap=True, weight='bold', size='md'),
                        BoxComponent(
                            layout='vertical',
                            margin='lg',
                            spacing='sm',
                            contents=[
                                BoxComponent(layout='baseline', spacing='sm',
                                             contents=[
                                                 TextComponent(
                                                     text='Version', color='#aaaaaa', size='sm', flex=1),
                                                 TextComponent(
                                                     text=review['version'], wrap=True, color='#666666', size='sm', flex=0)
                                             ],
                                             ),
                                BoxComponent(layout='baseline', spacing='sm',
                                             contents=[
                                                 TextComponent(
                                                     text='Rating', color='#aaaaaa', size='sm', flex=1),
                                                 TextComponent(
                                                     text=review['rating'], wrap=True, color='#666666', size='sm', flex=0),
                                             ],
                                             ),
                                SeparatorComponent(),
                                BoxComponent(layout='baseline', spacing='sm',
                                             contents=[
                                                 TextComponent(
                                                     text=review['comment'], wrap=True, color='#666666', size='sm', flex=1),
                                             ],
                                             ),
                            ],
                        )
                    ],
                ),
                footer=BoxComponent(
                    layout='vertical',
                    spacing='sm',
                    contents=[
                        SpacerComponent(size='sm'),
                        ButtonComponent(
                            style='secondary',
                            height='sm',
                            action=MessageAction(label='罵個幹！', text='幹！'),
                        ),
                    ]
                ),
            )
            contents.append(bubble)

        return contents

    def notify(self, channels, reviews, platform):

        for idx in range(0, len(reviews), 10):

            contents = self.flex_message_builder(
                reviews[idx:idx + 10], platform)

            message = FlexSendMessage(
                alt_text="➤ 新的 App 評論來囉！", contents=CarouselContainer(contents=contents))

            for channel in channels:
                try:
                    self.line_bot_api.push_message(
                        to=channel, messages=message)
                except Exception as e:
                    print(f"Line error: {e}")


class ReviewCrawler:

    def __init__(self):
        self.gsc = GoogleSheetClient()
        self.history_list = list()

    def notify(self, reviews, platform):
        token = self.gsc.load_token()
        line_bot = LineBot(token['line_token'])
        slack_bot = SlackBot(token['slack_token'])
        line_channel, slack_channel = self.gsc.load_notify_list(sheet_name)
        new_reviews = list()

        line_bot.notify(line_channel, reviews, platform)

        for review in reviews:
            try:
                slack_bot.notify(slack_channel, review, platform)
                new_reviews.insert(0, review['id'])
            except Exception as e:
                print(f"Slack notify error: [{review['id']}] - {e}")

        self.crawler.save_history(new_reviews)

    def app_store_crawling(self, app_id):
    
        self.crawler = AppStoreCrawler(app_id)
        reviews = self.crawler.crawling()
        
        print(f"➤ App Store - Get {len(reviews)} new comment !")

        if reviews:
            self.notify(reviews, "App Store")

    def google_play_crawling(self, package_name):

        self.crawler = GooglePlayCrawler(package_name)
        reviews = self.crawler.crawling()
        
        print(f"➤ Google Play - Get {len(reviews)} new comment !")
        
        if reviews:
            self.notify(reviews, "Google Play")


@app.route('/CrAwlInG')
def crawler():

    app_list = {
        'app_name': {
            'app_id': 1000000000,
            'package_name': "com.example.app"
        }
    }

    for app_name, app_info in app_list.items():
        bot = ReviewCrawler()
        bot.app_store_crawling(app_info['app_id'])
        # bot.google_play_crawling(app_info['package_name'])

    return f"{app_name} Crawling Done ."


if __name__ == '__main__':
    crawler()
