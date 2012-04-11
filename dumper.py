#!/usr/bin/env python

import sys
import re
import json
from collections import defaultdict

import sqlalchemy as sa
from sqlalchemy import orm


QUERY = '''SELECT c.name, v.value FROM factbook_values v
JOIN factbook_countries c ON v.countryid = c.id
JOIN factbook_fields f ON v.fieldid = f.id
WHERE LOWER(f.name) = LOWER(%s)'''


e = sa.create_engine('postgres://127.0.0.1/factbook')
meta = sa.MetaData(bind=e, reflect=True)
Session = orm.scoped_session(orm.sessionmaker(bind=e))
s = Session()

class Country(object):
    query = Session.query_property()
orm.Mapper(Country, meta.tables['factbook_countries'])

class Value(object):
    query = Session.query_property()
orm.Mapper(Value, meta.tables['factbook_values'])

class Field(object):
    query = Session.query_property()
orm.Mapper(Field, meta.tables['factbook_fields'])

class Rank(object):
    query = Session.query_property()
orm.Mapper(Rank, meta.tables['factbook_ranks'])


COUNTRIES = defaultdict(dict)
EXCLUDE_COUNTRIES = [x.strip() for x in '''
World
European Union
Greenland
Gaza Strip
British Indian Ocean Territory
'''.split('\n')]
CONVERTERS = {}
def converter(key):
    def inner(func):
        CONVERTERS[key] = func
        return func
    return inner


def fields():
    return sorted(x[0] for x in s.query(Field.name))

def query(fieldname):
    return (s.query(Value.value, Country.name)
            .join(Country)
            .join(Field)
            .filter(sa.not_(Country.name.in_(EXCLUDE_COUNTRIES)))
            .filter(sa.func.lower(Field.name) == fieldname.lower()))

def collect(field):
    conv = CONVERTERS.get(field.lower()) or (lambda x: x)
    for row in query(field):
        COUNTRIES[row[1]][field] = conv(row[0])

def rankq(fieldname):
    return (s.query(Rank.number, Country.name)
            .join((Country, Country.xmlid == Rank.country))
            .join(Field)
            .filter(sa.func.lower(Field.name) == fieldname.lower()))

def rankcollect(field, rename=None):
    for row in rankq(field):
        COUNTRIES[row[1]][rename or field] = float(row[0])


@converter('railways')
@converter('roadways')
def ways(data):
    m = re.search('([\d,]+) km', data)
    if not m:
        print 'not found length here:', data
        sys.exit(1)
    return int(m.group(1).replace(',', ''))

@converter('oil - consumption')
@converter('oil - production')
def oil(data):
    res = {
        '([\d,]+) bbl/day': lambda m: int(m.group(1).replace(',', '')),
        '([\d\.]+) million bbl/day': lambda m: float(m.group(1)) * 1000000,
        'NA bbl/day': lambda m: 0
        }
    for pat, proc in res.items():
        m = re.search(pat, data)
        if m:
            return proc(m)
    print 'not found length here:', data
    sys.exit(1)


def printx(x):
    print x

def dict2list(d):
    return [dict(name=x, **y) for x, y in d.items()]


if __name__ == '__main__':
    import pprint
    if len(sys.argv) < 2:
        map(printx, fields())
        sys.exit()

    if sys.argv[1] == '-c':
        collector = collect
        args = sys.argv[2:]
    else:
        collector = rankcollect
        args = sys.argv[1:]

    for arg in args:
        if '=' in arg:
            collector(*arg.split('='))
        else:
            collector(arg)

    data = dict2list(COUNTRIES)
    stuff = sorted(data,
                   key=lambda x: (x.get('railways'), x.get('roadways')),
                   reverse=True)
    print json.dumps(stuff, indent=2)
