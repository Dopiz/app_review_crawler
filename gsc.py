import gspread
from oauth2client.service_account import ServiceAccountCredentials


class GoogleSheetClient:

    def __init__(self):
        self.auth_path = 'secret/auth.json'
        self.gss_scopes = ['https://spreadsheets.google.com/feeds']
        self.gss_client = self.auth_gss_client(self.auth_path, self.gss_scopes)
        with open('secret/spreadsheet_key') as f:
            self.spreadsheet_key = f.read().strip()

    @staticmethod
    def auth_gss_client(path, scopes):
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            path, scopes)
        return gspread.authorize(credentials)

    def load_app_id_list(self, sheet_name):
        sheet = self.gss_client.open_by_key(
            self.spreadsheet_key).worksheet(sheet_name)

        app_list = sheet.col_values(1)[1:]

        return app_list

    def load_notify_list(self, sheet_name):
        sheet = self.gss_client.open_by_key(
            self.spreadsheet_key).worksheet(sheet_name)

        line_notify = sheet.col_values(2)[1:]
        slack_notify = sheet.col_values(3)[1:]

        return line_notify, slack_notify

    def load_token(self):
        sheet = self.gss_client.open_by_key(
            self.spreadsheet_key).worksheet('Token')

        line_token = str(sheet.col_values(1)[1])
        slack_token = str(sheet.col_values(2)[1])

        token = {'line_token': line_token, 'slack_token': slack_token}

        return token
