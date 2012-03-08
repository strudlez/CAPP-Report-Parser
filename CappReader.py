#!/usr/bin/env python2

#Reads CAPP Report sqlite file generated by CappParser.py
import sqlite3, sys
def get_arg(args, arg):
    if arg in args:
        ind = args.index(arg) + 1
        if ind < len(args):
            return args[ind]
    return None

def help():
    print 'usage: %s file.sqlite [option]' % sys.argv[0]
    print 'Options:'
    print '  -l: lists students'
    print '  -c STUDENT: lists students current classes'
    print '  -g STUDENT: lists brothers that can help student for current class'
    print '  -G STUDENT: lists brothers that a student can help'
    print '  -w STUDENT: lists classes a student did well in (B or A)'
    print '  -a GRADE: Counts AP grades as specified grade'
    print '  -o GRADE: sets the grade cutoff for "good grades"'
    print '            Grades: A B C P D F'

def list_students(c):
    c.execute('SELECT count, name FROM users')
    names = [i for i in c]
    if len(names):
        print 'Students:'
        for i in names: print '  %s: %s' % i
    else: print 'No Students in database'

def list_classes(c, student):
    id, name = get_data(c, student)
    if id:
        print 'Classes for %s:' % name    
        for i in get_current_classes(c, id):
            print '  %s %s: %s' % i
        
    pass

def get_help(c, student, cutoff, ap):
    id, name = get_data(c, student)
    print 'Classes for %s:' % name    
    for i in get_current_classes(c, id):
        print '  %s %s: %s' % i
        for j in find_help(c, i[0], i[1], cutoff,ap):
            oId, grade = j
            oId, oName = get_data(c, oId)
            print '    %s: %s' % (oName, grade)

    pass

def give_help(c, student, cutoff, ap):
    id, name = get_data(c, student)
    if id:
        print 'Old classes for %s:' % name
        for i in get_good_grades(c, id, cutoff, ap):
            prefix, num, name, grade = i
            can_help = find_other(c, prefix, num, id)
            if len(can_help):
                print '  %s %s: %s - %s' % i
                for j in can_help:
                    oId, oName = get_data(c, j)
                    print '    %s' % (oName,)


def see_good_grades(c, student, cutoff, ap):
    id, name = get_data(c, student)
    if id:
        print 'Good grades for %s:' % name    
        for i in get_good_grades(c, id, cutoff, ap):
            print '  %s %s: %s - %s' % i

def find_other(c, prefix, num, id):
    c.execute("""SELECT id FROM grades WHERE
            grade='Reg' AND prefix=? AND num=? AND id <> ?""",
            (prefix, num, id))
    
    return [i[0] for i in c]

def find_help(c, prefix, num, cutoff, ap):
    c.execute("""SELECT id, grade FROM grades WHERE
            grade <> 'Reg' AND prefix=? and num=?""", (prefix, num))

    return [i for i in c if is_good_grade(i[1], cutoff, ap)]

def is_good_grade(grade, cutoff, ap):
    grades = 'ABCPDF'
    if grade == 'AP': grade = ap
    else: grade = grade[0]
    return grade in grades and grades.find(grade) <= grades.find(cutoff)

def get_good_grades(c, id, cutoff, ap):
    c.execute("""SELECT prefix, num, name, grade FROM grades WHERE
            id = ? AND grade <> 'Reg'""", (id,))

    return [i for i in c if is_good_grade(i[3], cutoff, ap)]
def get_current_classes(c, id):
    c.execute("""SELECT prefix, num, name FROM grades WHERE
            id = ? AND grade = ?""", (id, 'Reg'))
    return [i for i in c]

def get_data(c, student):
    c.execute("SELECT id, name FROM users where id=? or count=? or name=?", 
            (student, student,student))
    id = [i for i in c]
    if len(id): return id[0]
    else: return None, None

def check_table(c, name):
    c.execute("""SELECT name FROM sqlite_master
        WHERE type='table' AND name=?""", (name,))
    return len([i for i in c]) > 0

def run():
    if len(sys.argv) < 2 or '-h' in sys.argv[1:]:
        help()
        return

    args = sys.argv[1:]
    cutoff = get_arg(args, '-o') or 'B'
    ap = get_arg(args, '-a') or 'AP'

    pass_cutoff = lambda x: lambda y, z: x(y, z, cutoff, ap)

    functions = {
        '-c': list_classes,
        '-g': pass_cutoff(get_help),
        '-G': pass_cutoff(give_help),
        '-w': pass_cutoff(see_good_grades)
    }
    
    db = sqlite3.connect('grades.sqlite')
    c = db.cursor()

    if not check_table(c, 'users') or not check_table(c, 'grades'):
        help()
        return
    
    if '-l' in args:
        list_students(c)
    else:
        arg = None
        for i in functions:
            arg = get_arg(args, i)
            if arg:
                functions[i](c, arg)
                break
        if not arg: help()

    db.commit()
    c.close()

if __name__ == '__main__':
    run()

