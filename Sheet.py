import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

class Sheet:
	def __init__(self, scope, id):
		credentials = None
		if os.path.exists('token.pickle'):
			with open('token.pickle', 'rb') as token:
				credentials = pickle.load(token)
		if not credentials or not credentials.valid:
			if credentials and credentials.expired and credentials.refresh_token:
				credentials.refresh(Request())
			else:
				flow = InstalledAppFlow.from_client_secrets_file('credentials.json', scope)
				credentials = flow.run_local_server(port=0)
			with open('token.pickle', 'wb') as token:
				pickle.dump(credentials, token)
		service = build('sheets', 'v4', credentials=credentials)
		self.spreadsheet = service.spreadsheets()
		self.id = id

	def append(self, range, body):
		self.spreadsheet.values().append(spreadsheetId=self.id, range=range, valueInputOption='RAW', body=body).execute()

	def fetch(self, range):
		result = self.spreadsheet.values().get(spreadsheetId=self.id, range=range).execute()
		values = result.get('values')
		return values