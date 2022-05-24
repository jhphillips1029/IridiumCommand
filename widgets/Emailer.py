"""
----------------------------------------------------------------------------
MIT License
Copyright (c) 2022 Joshua H. Phillips
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to
deal in the Software without restriction, including without limitation the
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
sell copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
IN THE SOFTWARE.
----------------------------------------------------------------------------

This is a wrapper class for the Google GMail API. It is used by Overview.py to send commands to the Iridium modem on the balloon.
"""

# General imports
import os
import pickle
import json

# Gmail API utils
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# for encoding/decoding messages in base64
from base64 import urlsafe_b64decode, urlsafe_b64encode

# for dealing with attachement MIME types
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from mimetypes import guess_type as guess_mime_type

# Request all access (permission to read/send/receive emails, manage the inbox, and more)
SCOPES = ['https://mail.google.com/']


def gmail_authenticate():
    """
    Authenticate gmail credentials; requires credentials.json from Google Cloud services; creates token.pickle
    
    Parameters:
    None
    
    Returns:
    ???: Google authentication I guess
    """

    creds = None
    # the file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time
    if os.path.exists("token.pickle"):
        with open("token.pickle","rb") as token:
            creds = pickle.load(token)
    # if there are no (valid) credentials availablle, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json',SCOPES)
            creds = flow.run_local_server(port=0)
        # save the credentials for the next run
        with open("token.pickle","wb") as token:
            pickle.dump(creds, token)
    return build('gmail','v1',credentials=creds)
    
    
# Adds the attachment with the given filename to the given message
def add_attachment(message,filename):
    """
    Add an attachment to the email
    
    Parameters:
    message  (???): The email object to be sent
    filename (str): The filename of the attachement to be attached
    
    Returns:
    None
    """

    content_type, encoding = guess_mime_type(filename)
    if content_type is None or encoding is not None:
        content_type = 'application/octet-stream'
    main_type,sub_type = content_type.split('/',1)
    if main_type=='text':
        fp = open(filename,'rb')
        msg = MIMEText(fp.read().decode(),_subtype=sub_type)
        fp.close()
    elif main_type=='image':
        fp = open(filename,'rb')
        msg = MIMEImage(fp.read(),_subtype=sub_type)
        fp.close()
    elif main_type=='audio':
        fp = open(filename,'rb')
        msg = MIMEAudio(fp.read(),_subtype=sub_type)
        fp.close()
    else:
        fp = open(filename,'rb')
        msg = MIMEBase(main_type,sub_type)
        msg.set_payload(fp.read())
        fp.close()
    filename = os.path.basename(filename)
    msg.add_header('Content-Disposition','attachment',filename=filename)
    message.attach(msg)
    
def build_message(destination,obj,body,attachments=[]):
    """
    Construct the body of the email
    
    Parameters:
    desitination (str): Who the email is to
    obj          (str): Subject of the email
    body         (str): The body of the email
    attachments (list): The attachments to send
    
    Returns:
    dict: Prepared email
    """
    
    if not attachments: # no attachments given
        message = MIMEText(body)
        message['to'] = destination
        message['subject'] = obj
    else:
        message = MIMEMultipart()
        message['to'] = destination
        message['subject'] = obj
        message.attach(MIMEText(body))
        for filename in attachments:
            add_attachment(message, filename)
    return {'raw':urlsafe_b64encode(message.as_bytes()).decode()}
    
def send_message(service,destination,obj,body,attachments=[]):
    """
    Sends an email
    
    Parameters:
    service      (???): The authenticated gmail service from above
    destination  (str): Who the email is to
    obj          (str): The subject line of the email
    body         (str): The body of the email
    attachments (list): The attachments to send
    
    Returns
    ???: It returns something
    """
    
    return service.users().messages().send(userId="me",body=build_message(destination,obj,body,attachments)).execute()
    
    
def read_messages(service,num_read=5):
    """
    Reads emails
    
    Parameters:
    service  (???): The authenticated gmail service from above
    num_read (int): The number of emails to read
    
    Returns:
    list: A list of the bodies of the read emails
    """
    
    result = service.users().messages().list(userId='me').execute()
    messages = result.get('messages')
    txts = [service.users().messages().get(userId='me',id=msg['id']).execute() for msg in messages[:num_read]]
    return txts

