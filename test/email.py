# -*- coding: utf-8 -*-
# author: taojin
# time:  2019/9/9 16:11
from flask_mail import Message
from app import mail, app

msg = Message('test subject', sender=app.config['ADMINS'][0],
recipients=['taojin@viewhigh.com'])
msg.body = 'text body'
msg.html = '<h1>HTML body</h1>'
mail.send(msg)