import time
import app


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
        if args[key]:
            line = 'ro.' + key + '=%(' + key + ')s'
            s.append(line)
    s = ' AND '.join(s)
    return '(' + s + ')'
