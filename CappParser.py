#!/usr/bin/env python2


#Parses CAPP Reports into an sqlite file
#Usage: CappParser FILES
from HTMLParser import HTMLParser
import sqlite3, glob, sys

def unescape(s):
    s = s.replace("&lt;", "<")
    s = s.replace("&gt;", ">")
    # this has to be last:
    s = s.replace("&amp;", "&")
    return s

prefixes = ('ARCH', 'ARTS', 'ASTR', 'BCBP', 'BIOL', 'BMED', 'CHEM', 'CHME',
        'CISH', 'CIVL', 'COGS', 'COMM', 'CSCI', 'ECON', 'ECSE', 'ENGR',
        'ENVE', 'ERTH', 'ECSI', 'IENV', 'IHSS', 'ISCI', 'ISYE', 'ITWS',
        'LANG', 'LGHT', 'LITR', 'MANE', 'MATH', 'MATP', 'MGMT', 'MTLE',
        'PHIL', 'PHYS', 'PSYC', 'STSH', 'STSS', 'USAF', 'USAR', 'USNA',
        'WRIT')
class Class():
    prefix = ''
    num = 0
    name = ''
    credits = ''
    term = ''
    grade = ''
    def __init__(self, prefix):
        self.prefix = prefix

def parse(file_name, c):
    Id = 0
    data = []
    isId = False
    isClass = False
    tmpClass = None
    classNum = 0
    f = open(file_name)
    d = f.read()
    

    for line in d.split('<'):
        line = '<'+line
        
        tags = line.split('>')
        for tag in tags:
            if tag and tag[0]=='<':
                if tag.find('class="f3"') != -1:
                    tags[1] = unescape(tags[1])
                    if isId:
                        Id = int(tags[1])
                        isId = False
                    elif isClass:
                        classNum += 1
                        if classNum == 1: tmpClass.num = int(tags[1])
                        elif classNum == 2: tmpClass.name = tags[1]
                        elif classNum == 3: tmpClass.credits = tags[1]
                        elif classNum == 4: tmpClass.term = tags[1]
                        elif classNum == 5:
                            tmpClass.grade = tags[1]
                            data.append(tmpClass)
                            isClass = False
                    else:
                        try:
                            prefixes.index(tags[1])
                            tmpClass = Class(tags[1])
                            isClass = True
                            classNum = 0
                        except:
                            if tags[1] == 'Student ID:':
                                isId = True
                tag = tag+'>'
    print 'Parsed: %s' % file_name

    c.execute('insert or ignore into users(id) values (%d)' % Id)
    for i in data:
        t = (Id, i.prefix, i.num, i.name, i.grade)
        c.execute("replace into grades(id, prefix, num, name, grade) values (%d, '%s', %d, '%s', '%s')" % t)

def run():
    if len(sys.argv) < 2:
        print 'usage: %s FILES' % sys.argv[0]
        print 'example: %s *.htm' % sys.argv[0]
        return

    files = glob.glob(sys.argv[1])
    if len(files) < 1: return

    db = sqlite3.connect('grades.sqlite')
    c = db.cursor()
    c.execute('create table if not exists users(id integer primary key)')
    c.execute('''create table if not exists grades(
        id integer,
        prefix varchar,
        num integer,
        name varchar,
        grade varchar,
        FOREIGN KEY(id) REFERENCES users(id),
        PRIMARY KEY (id, prefix, num)
    )''') 

    for f in files: parse(f, c)

    db.commit()
    c.close()

if __name__ == '__main__':
    run()

