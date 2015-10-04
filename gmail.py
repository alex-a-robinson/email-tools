# Class to talk to gmail api

import httplib2
import os
import email

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools

import argparse
import base64

SCOPES = 'https://www.googleapis.com/auth/gmail.modify'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Gmail API Python Quickstart'

flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()

class Gmail:
  def __init__(self):
    self.credentials = self.get_credentials()
    self.http = self.credentials.authorize(httplib2.Http())
    self.service = discovery.build('gmail', 'v1', http=self.http)

  def get_credentials(self):
    '''Gets valid user credentials
    '''
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
      os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir, 'gmail-python-quickstart.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
      flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
      flow.user_agent = APPLICATION_NAME
      credentials = tools.run_flow(flow, store, flags)
      print 'Storing credentials to ' + credential_path
  
    return credentials

  def _get_message(self, args):
    args['userId'] = 'me'
    return self.service.users().messages().get(**args).execute()
  
  def _list_messages(self, args):
    args['userId'] = 'me'
    return self.service.users().messages().list(**args).execute()

  def _get_thread(self, args):
    args['userId'] = 'me'
    return self.service.users().threads().get(**args).execute()

  def search_messages(self, query):
    return self._list_messages({'q': query})

  def inbox(self):
    messages = self._list_messages({'labelIds': ['INBOX']})
    m = []
    for message in messages['messages']:
      message_id = message['id']
      raw = self.get_message_text(message_id)
      parsed = self.parse_raw_message(raw)
      m.append((parsed, message_id))    

    return m

  def get_message(self, message_id):
    return self._get_message({'id': message_id, 'format': 'raw'})

  def get_thread(self, thread_id):
    return self._get_thread({'id': thread_id, 'format': 'raw'})

  def get_thread_text(self, message_id):
    msg = self.get_thread(message_id)
    msg_str = base64.urlsafe_b64decode(msg['raw'].encode('ASCII'))

    return msg_str 

  def get_message_text(self, message_id):
    msg = self.get_message(message_id)
    msg_str = base64.urlsafe_b64decode(msg['raw'].encode('ASCII'))

    return msg_str

  def parse_raw_message(self, raw):
    return email.message_from_string(raw)

  def archive(self, msg_id):
    print msg_id
    self.service.users().messages().modify(userId='me', id=msg_id, body={"removeLabelIds": ["INBOX"], "addLabelIds": []}).execute()


