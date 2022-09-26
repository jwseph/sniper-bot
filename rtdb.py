import firebase_admin
from firebase_admin import credentials, db
import os

cert = {
  "type": "service_account",
  "project_id": "sniper-mudae",
  "private_key_id": os.environ['PRIVATE_KEY_ID'],
  "private_key": os.environ['PRIVATE_KEY'],
  "client_email": "firebase-adminsdk-fbp5e@sniper-mudae.iam.gserviceaccount.com",
  "client_id": "110578361931967482061",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbp5e%40sniper-mudae.iam.gserviceaccount.com"
}

firebase_admin.initialize_app(credentials.Certificate(cert), {'databaseURL': 'https://sniper-mudae-default-rtdb.firebaseio.com'})

claims = db.reference('/claims')
