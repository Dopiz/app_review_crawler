import json
import time

import jwt
import requests


class GooglePlayCrawler():

    def __init__(self, package_name, history_list):
        self.package_name = package_name
        self.history_list = history_list

    def load_service_account_data(self):
        with open('./bot/auth.json') as data_file:
            return json.load(data_file)

    def jwt_encode(self, payload, secret, algorithm):
        return jwt.encode(payload, secret, algorithm=algorithm)

    def jwt_decode(self, encode_token: str):
        return encode_token.decode()

    def android_os_version(self, api_level):
        return {
            21: '5.0',
            22: '5.1',
            23: '6.0',
            24: '7.0',
            25: '7.1',
            26: '8.0',
            27: '8.1',
            28: '9.0',
        }.get(api_level, 'Not Found')

    def google_auth_token(self, token):

        url = 'https://www.googleapis.com/oauth2/v4/token'

        headers = {
            'Content-Type': 'application/json'
        }

        body = {
            'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer',
            'assertion': token
        }

        res = requests.post(url, headers=headers, json=body).json()

        return res['access_token']

    def get_google_play_review(self, access_token):

        url = (f"https://www.googleapis.com/androidpublisher/v3/applications/"
               f"{self.package_name}/reviews")

        headers = {
            'Content-Type': 'application/json'
        }

        payload = {
            'access_token': access_token
        }

        res = requests.get(url, headers=headers, params=payload).json()

        return res['reviews'] if 'reviews' in res else dict()

    def crawling(self):

        data = self.load_service_account_data()

        payload = {
            'iss': data['client_email'],
            'scope': 'https://www.googleapis.com/auth/androidpublisher',
            'aud': 'https://www.googleapis.com/oauth2/v4/token',
            "exp": int(time.time()) + int(60 * 60),
            "iat": int(time.time())
        }

        new_reviews = list()

        secret = data['private_key']
        encode_token = self.jwt_encode(payload, secret, algorithm='RS256')
        decode_token = self.jwt_decode(encode_token)
        access_token = self.google_auth_token(decode_token)

        res = self.get_google_play_review(access_token)

        for entry in res:

            if entry['reviewId'][-6:] in self.history_list:
                break

            review_id = entry['reviewId'][-6:]
            comment = entry['comments'][0]['userComment']['text']
            if len(comment) > 100:
                comment = comment[:100]
            rating = int(entry['comments'][0]['userComment']['starRating'])
            rat = rating * "★" + (5 - rating) * "☆"
            os_version = manufacturer = product_name = version = ""
            os_version = entry['comments'][0]['userComment'].get('androidOsVersion')
            os_version = self.android_os_version(os_version)
            manufacturer = entry['comments'][0]['userComment'].get(
                'deviceMetadata').get('manufacturer')
            product_name = entry['comments'][0]['userComment'].get(
                'deviceMetadata').get('productName')
            version = entry['comments'][0]['userComment'].get('appVersionName')

            if '(' and ')' in product_name:
                product_name = product_name.split('(')[1].split(')')[0]

            review = {
                'id': review_id,
                'comment': comment.replace("\t", ""),
                'rating': rating,
                'rat': rat,
                'os_version': os_version,
                'product_name': f"{manufacturer} {product_name}",
                'version': version
            }

            new_reviews.append(review)

        return new_reviews[::-1]
