import slack


class SlackBot(object):

    def __init__(self, token):
        self.__slack_bot_api = slack.WebClient(token)

    def notify(self, channels, reviews, platform):

        for idx in range(0, len(reviews), 5):
            blocks = self.__interactive_message_builder(reviews=reviews[idx:idx+5],
                                                        platform=platform)
            for channel in channels:
                try:
                    self.__slack_bot_api.chat_postMessage(channel=channel, blocks=blocks)
                except Exception as e:
                    print(f"Slack-bot Notify ERROR: {e}")

    def __interactive_message_builder(self, reviews, platform):

        title = (" App Store 新的評論來囉～" if platform == "App Store"
                 else "➤ Google play 新的評論來囉～")

        block = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"　\n *{title}* \n 　"
                }
            }
        ]

        if platform == "App Store":
            for review in reviews:
                rating = int(review['rating']) * ":star:"
                section = [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": (f">*Rating:* {rating} \n"
                                     f">*App Version:* {review['version']} \n"
                                     f">*Title:* {review['title']} \n"
                                     f" {review['comment']}")
                        },
                        "accessory": {
                            "type": "image",
                            "image_url": "https://i.imgur.com/106NTJ7.png",
                            "alt_text": "App Store Review"
                        }
                    },
                    {
                        "type": "divider"
                    }
                ]

                block.extend(section)

        else:
            for review in reviews:
                rating = int(review['rating']) * ":star:"
                section = [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": (f"\n>*Rating:* {rating} \n"
                                     f">*Device:* {review['product_name']} \n"
                                     f">*OS Version:* {review['os_version']} \n"
                                     f">*App Version:* {review['version']} \n"
                                     f" {review['comment']}")
                        },
                        "accessory": {
                            "type": "image",
                            "image_url": "https://i.imgur.com/ME1bITU.png",
                            "alt_text": "Google Play Review"
                        }
                    },
                    {
                        "type": "divider"
                    }
                ]

                block.extend(section)

        return block
