#!/usr/bin/env python3
"""Regenerate index.html from items.json and update history.json. Usage: python3 build.py [YYYY-MM-DD]"""
import json,sys,datetime
today=sys.argv[1] if len(sys.argv)>1 else datetime.date.today().isoformat()
items=json.load(open('items.json'))
try: hist=json.load(open('history.json'))
except FileNotFoundError: hist=[]
byurl={h['url']:h for h in hist}
cur={i['url'] for i in items}
for i in items:
    h=byurl.get(i['url'])
    if not h:
        h={'url':i['url'],'title':i['title'],'source':i['source'],'date':i['date'],'listedOn':today,'status':'listed'}
        hist.append(h); byurl[i['url']]=h
    i['listedOn']=h['listedOn']; h['status']='top' if i.get('top') else 'listed'
for h in hist:
    if h['url'] not in cur and h['status'] in ('top','listed'): h['status']='expired'
json.dump(hist,open('history.json','w'),indent=1,ensure_ascii=False)
items.sort(key=lambda i:(not i.get('top'),i['date']),reverse=False)
items=[i for i in items if i.get('top')]+sorted([i for i in items if not i.get('top')],key=lambda i:i['date'],reverse=True)
html=open('template.html').read().replace('/*DATA*/[]',json.dumps(items,ensure_ascii=False).replace('</','<\\/')).replace('/*UPDATED*/',today)
open('index.html','w').write(html); print(len(items),'items;',len(hist),'in history')
