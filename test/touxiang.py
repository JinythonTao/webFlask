# -*- coding: utf-8 -*-
# author: taojin
# time:  2019/9/6 13:08
import hashlib


def get_icon_url(username, size=150):
    '''返回头像url'''
    m5 = hashlib.md5(f'{username}'.encode('utf-8')).hexdigest()  # 返回16进制摘要字符串
    # s 返回头像大小 d 返回头像类型 没注册的邮箱需要加此参数
    url = f'http://www.gravatar.com/avatar/{m5}?s={size}&d=monsterid'
    return url

fileName = "taojin.jpg"
# 上传后存储位置和允许上传的图片格式
UPLOAD_FOLDER = r'E:\python36\microBlog/app/static/images/avatar/'
ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg', 'gif']
flag = '.' in fileName and fileName.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
print(flag)