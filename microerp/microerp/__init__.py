from flask import Flask
import settings

app = Flask(__name__)
app.config.from_object('microerp.settings')

usuarios_autorizados = ['dsbraz@gmail.com', 'fabiportella@gmail.com']

from views import *

