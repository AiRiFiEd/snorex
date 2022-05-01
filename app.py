# -*- coding: utf-8 -*-
"""
Created on Wed Dec 29 15:01:36 2021

@author: yuanq
"""

import sys
sys.path.append(r'E:\Dropbox\Yuan Qing\Work\Projects\Libraries\3. Python\dd8')
from flask.cli import load_dotenv
from snorex import app

if __name__ == '__main__':
    load_dotenv()
    app.run(host="0.0.0.0", debug=False)
