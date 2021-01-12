import json
from datetime import datetime
import psycopg2.extras

def loadFile(fname):
    with open(fname, 'r', encoding="utf8") as fi:
        return json.load(fi)

def objectview(data):
    ndata = []
    for x in data:
        ndata.append(objview(x))
    return ndata

class objview(object):
    def __init__(self, d):
        self.__dict__ = d

def log(stri):
    print(stri)
    time = datetime.now()
    file = open("info.log", "a")
    file.write("{}: {}".format(str(time.strftime("%H:%M:%S")), stri+"\n"))
    file.close()

def db_commit(insc, tuple, db):
    cursor = db.cursor()
    cursor.execute(insc, tuple)
    db.commit()
    cursor.close()

def db_fetch(insc, tuple, db):
    cursor = db.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
    cursor.execute(insc, tuple)
    res = cursor.fetchall()
    cursor.close()
    return res