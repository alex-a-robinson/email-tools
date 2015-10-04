from gmail import Gmail

import urllib2
import re

mail = Gmail()

def is_validate_email(message):
  sbj = message['subject']
  to  = message['to']

  if not re.match(r'(?i)(validate)|(verify).*(email|account)', sbj):
    return False

  return True

def find_links(message):
  text = ''
  if message.is_multipart():
    for payload in message.get_payload():
      text += '\n' + payload.get_payload()
  else:
    text = message.get_payload()

  p = re.compile(r'href=["\'](.+)["\']')
  return p.findall(text)
  

def find_validate_link(message):
  links = find_links(message)
  if len(links) >= 1:
    return links[0]
  else:
    return None

def vist_link(link):
  urllib2.urlopen(link)

def archive(msg_id):
  mail.archive(msg_id)

def check():
  inbox = mail.inbox()

  for message in inbox:
    parsed, msg_id = message
    print 'Checking message...'
    if is_validate_email(parsed):
      print 'message is valid'
      val_link = find_validate_link(parsed)
      print 'found link %s' % val_link
      if val_link == None:
        continue
      vist_link(val_link)
      archive(msg_id)
    else:
      print 'validation not required'

