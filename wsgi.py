# -*- coding: utf-8 -*-
# author: taojin
# time:  2019/9/18 15:33
import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
from app import app
