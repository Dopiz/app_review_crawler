import requests
from linebot import LineBotApi
from linebot.models import (BoxComponent, BubbleContainer, ButtonComponent,
                            CarouselContainer, FlexSendMessage, ImageComponent,
                            MessageAction, SeparatorComponent, SpacerComponent,
                            TextComponent, URIAction)


class LineBot(object):

    def __init__(self, token):
        self.__token = token
        self.__line_bot_api = LineBotApi(self.__token)

    def __check_usage(self):

        url = "https://api.line.me/v2/bot/message/quota/consumption"
        header = {
            'Authorization': f"Bearer {self.__token}"
        }

        total_usage = requests.get(url, headers=header).json()['totalUsage']

        return total_usage

    def notify(self, channels, reviews, platform):

        if self.__check_usage() > 490:
            print("Line-bot Push Message Usage 已達上限！")
            return False

        for idx in range(0, len(reviews), 10):
            contents = self.__flex_message_builder(reviews=reviews[idx:idx+10], platform=platform)

            message = FlexSendMessage(alt_text="➤ 新的 App 評論來囉！",
                                      contents=CarouselContainer(contents=contents))
            for channel in channels:
                try:
                    self.__line_bot_api.push_message(to=channel, messages=message)
                except Exception as e:
                    print(f"Line-bot Notify ERROR: {e}")

        return True

    def __flex_message_builder(self, reviews, platform):

        if platform == "App Store":
            header_text = " App Store 新的評論來囉～"
            text_color = "#0099e5"
            hero_image = "https://i.imgur.com/dp5OCjl.jpg"

        elif platform == "Google Play":
            header_text = "➤ Google play 新的評論來囉～"
            text_color = "#E00512"
            hero_image = "https://i.imgur.com/DRfTgac.png"

        contents = list()

        for review in reviews:

            if platform == "App Store":
                body_contents = [
                    TextComponent(
                        text=review['title'], wrap=True, weight='bold', size='md'),
                    BoxComponent(
                        layout='vertical', margin='lg', spacing='sm',
                        contents=[
                            BoxComponent(layout='baseline',
                                         spacing='sm',
                                         contents=[
                                             TextComponent(
                                                 text='Version', color='#aaaaaa',
                                                 size='sm', flex=1),
                                             TextComponent(
                                                 text=review['version'], wrap=True,
                                                 color='#666666', size='sm', flex=0)
                                         ],
                                         ),
                            BoxComponent(layout='baseline', spacing='sm',
                                         contents=[
                                             TextComponent(
                                                 text='Rating', color='#aaaaaa',
                                                 size='sm', flex=1),
                                             TextComponent(
                                                 text=str(review['rat']), wrap=True,
                                                 color='#666666', size='sm', flex=0),
                                         ],
                                         ),
                            SeparatorComponent(),
                            BoxComponent(layout='baseline', spacing='sm',
                                         contents=[
                                             TextComponent(
                                                 text=review['comment'], wrap=True,
                                                 color='#666666', size='sm', flex=1),
                                         ],
                                         ),
                        ],
                    )
                ]

            elif platform == "Google Play":
                body_contents = [
                    BoxComponent(
                        layout='vertical', margin='lg', spacing='sm',
                        contents=[
                            BoxComponent(layout='baseline', spacing='sm',
                                         contents=[
                                             TextComponent(
                                                 text='Device', color='#aaaaaa',
                                                 size='sm', flex=1),
                                             TextComponent(
                                                 text=review['product_name'], wrap=True,
                                                 color='#666666', size='sm', flex=0)
                                         ]
                                         ),
                            BoxComponent(layout='baseline', spacing='sm',
                                         contents=[
                                             TextComponent(
                                                 text='OS Version', color='#aaaaaa',
                                                 size='sm', flex=1),
                                             TextComponent(
                                                 text=review['os_version'], wrap=True,
                                                 color='#666666', size='sm', flex=0)
                                         ]
                                         ),
                            BoxComponent(layout='baseline', spacing='sm',
                                         contents=[
                                             TextComponent(
                                                 text='App Version', color='#aaaaaa',
                                                 size='sm', flex=1),
                                             TextComponent(
                                                 text=review['version'], wrap=True,
                                                 color='#666666', size='sm', flex=0)
                                         ]
                                         ),
                            BoxComponent(layout='baseline', spacing='sm',
                                         contents=[
                                             TextComponent(
                                                 text='Rating', color='#aaaaaa',
                                                 size='sm', flex=1),
                                             TextComponent(
                                                 text=str(review['rat']), wrap=True,
                                                 color='#666666', size='sm', flex=0),
                                         ]
                                         ),
                            SeparatorComponent(),
                            BoxComponent(layout='baseline', spacing='sm',
                                         contents=[
                                             TextComponent(
                                                 text=review['comment'], wrap=True,
                                                 color='#666666', size='sm', flex=1),
                                         ]
                                         )
                        ],
                    )
                ]

            bubble = BubbleContainer(
                direction='ltr',
                header=BoxComponent(
                    layout='vertical',
                    contents=[
                        TextComponent(
                            text=header_text, weight='bold', size='md', color=text_color)
                    ]
                ),
                hero=ImageComponent(
                    url=hero_image,
                    size='full',
                    aspect_ratio='5:3',
                    aspect_mode='cover'
                ),
                body=BoxComponent(
                    layout='vertical',
                    contents=body_contents
                ),
                footer=BoxComponent(
                    layout='vertical',
                    spacing='sm',
                    contents=[
                        SpacerComponent(size='sm'),
                        ButtonComponent(
                            style='secondary',
                            height='sm',
                            action=MessageAction(label='罵個幹！', text='幹！')
                        )
                    ]
                )
            )

            contents.append(bubble)

        return contents
