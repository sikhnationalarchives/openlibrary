#!/usr/local/bin/python2.5
import web, dbhash, sys
import cjson
from catalog.load import add_keys
from copy import deepcopy
from catalog.merge.index import *
from urllib import urlopen, urlencode
import psycopg2

path = '/1/pharos/edward/index/2/'
dbm_fields = ('lccn', 'oclc', 'isbn', 'title')
dbm = dict((i, dbhash.open(path + i + '.dbm', flag='w')) for i in dbm_fields)

store_db = dbhash.open(path + "store.dbm", flag='w')

urls = (
    '/', 'index',
    '/store/(.*)', 'store',
    '/keys', 'keys',
)

def build_pool(index_fields):
    pool = {}
    for field in dbm_fields:
        if not field in index_fields:
            continue
        for v in index_fields[field]:
            if field == 'isbn' and len(v) < 10:
                continue
            try:
                v = str(v)
            except UnicodeEncodeError:
                print index_fields
                print `field, v`
                print v
                raise
            if v not in dbm[field]:
                continue
            pool.setdefault(field, set()).update(dbm[field][v].split(' '))
    return dict((k, sorted(v)) for k, v in pool.iteritems())

def add_to_indexes(record, dbm):
    if 'title' not in record or record['title'] is None:
        return
    if 'subtitle' in record and record['subtitle'] is not None:
        title = record['title'] + ' ' + record['subtitle']
    else:
        title = record['title']
    st = str(short_title(title))
#    if st in dbm['title'] and id in dbm['title'][st].split(' '):
#        return # already done
    add_to_index(dbm['title'], st, record['key'])
    if 'title_prefix' in record and record['title_prefix'] is not None:
        title2 = short_title(record['title_prefix'] + title)
        add_to_index(dbm['title'], title2, record['key'])

    fields = [
        ('lccn', 'lccn', clean_lccn),
        ('oclc_numbers', 'oclc', None),
        ('isbn_10', 'isbn', None),
        ('isbn_13', 'isbn', None),
    ]
    for a, b, clean in fields:
        if a not in record:
            continue
        for v in record[a]:
            if not v:
                continue
            if clean:
                v = clean(v)
            add_to_index(dbm[b], v, record['key'])

class index:
    def GET(self):
        web.header('Content-Type','application/json; charset=utf-8', unique=True)
        q = web.input()
        fields = dict((f, q[f].split('_')) for f in dbm_fields if f in q)
        pool = build_pool(fields)
        print cjson.encode({'fields': fields, 'pool': pool})
    def POST(self):
        q = cjson.decode(web.data())
        add_to_indexes(q, dbm)
        print 'success',
        
class store:
    def GET(self, key):
        web.header('Content-Type','application/json; charset=utf-8', unique=True)
        if key in store_db:
            print store_db[key]
        else:
            print cjson.encode({'error': key + " not found", 'keys': store_db.keys() })
    def POST(self, key):
        store_db[key] = web.data()
        print "saved"

class keys:
    def GET(self):
        web.header('Content-Type','application/json; charset=utf-8', unique=True)
        print cjson.encode(store_db.keys())

if __name__ == '__main__':
    try:
        web.run(urls, globals(), web.reloader)
    except:
        print "closing dbm files"
        for v in dbm.itervalues():
            v.close()
        store_db.close()
        print "closed"
        raise
