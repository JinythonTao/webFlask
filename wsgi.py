# -*- coding: utf-8 -*-
# author: taojin
# time:  2019/9/18 16:55
import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
    
from app import app as application

if __name__ == '__main__':
    application.run()
