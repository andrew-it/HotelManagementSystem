from app import app, bcrypt
import time
import logging

logger = logging.getLogger(__name__)


def imgName(filename):
    img_name = None
    if '.' in filename and filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']:
        img_name = str(time.time()) + '.' + filename.rsplit('.', 1)[1]
    return img_name


def reverseDate(date):
    return '-'.join(date.split('-')[::-1])


def searchOp(args):
    d = ['is_bathroom', 'is_tv', 'is_wifi', 'is_bathhub', 'is_airconditioniring']
    s = []
    for key in d:
        if key in args:
            line = 'ro.' + key + '=%(' + key + ')s'
            s.append(line)
    if len(s) != 0:
        s = ' AND '.join(s)
        return '(' + s + ')'
    else:
        return ""


def check_password(hash, password):
    return bcrypt.check_password_hash(hash, password)
