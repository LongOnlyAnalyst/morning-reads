#!/usr/bin/env python3
"""Merge Morning Reads ratings exports into feedback.json and print per-source / per-tag summaries.
Usage: python3 ingest_feedback.py export.json [more.json ...]   # exported/pasted JSON files
       python3 ingest_feedback.py --issues [--close]            # open GitHub issues on LongOnlyAnalyst/morning-reads
       python3 ingest_feedback.py                               # just print the summary"""
import json,sys,os,re,subprocess,datetime,collections
D=os.path.dirname(os.path.abspath(__file__));FB=os.path.join(D,'feedback.json');REPO='LongOnlyAnalyst/morning-reads'
def load():
    try: return json.load(open(FB))
    except FileNotFoundError: return {'ratings':{},'updated':None}
def parse(text):
    m=re.search(r'```(?:json)?\s*(.*?)```',text,re.S); text=m.group(1) if m else text
    d=json.loads(text.strip()); return d.get('items',d) if isinstance(d,dict) else d, (d.get('exportedAt') if isinstance(d,dict) else None)
def merge(fb,items,exportedAt):
    n=0
    for i in items:
        u=i.get('url')
        if not u: continue
        old=fb['ratings'].get(u,{}); ts=i.get('ratedAt') or exportedAt or ''
        if old and (old.get('ratedAt') or '')>ts: continue  # keep latest
        new={**old,**{k:v for k,v in i.items() if v is not None or k=='rating'}}; new['ratedAt']=ts or None
        if not new.get('tags'): new['tags']=old.get('tags',[])
        fb['ratings'][u]=new; n+=1
    return n
def summary(fb):
    S=collections.defaultdict(collections.Counter);T=collections.defaultdict(collections.Counter)
    for r in fb['ratings'].values():
        v=r.get('rating')
        if not v: continue
        S[r.get('source') or '?'][v]+=1
        for t in r.get('tags') or []: T[t][v]+=1
    for name,M in (('SOURCE',S),('TAG',T)):
        print(f'\n{name:40s} good neutral bad')
        for k,c in sorted(M.items(),key=lambda x:(-x[1]['good'],x[1]['bad'])): print(f'{k[:40]:40s} {c["good"]:4d} {c["neutral"]:7d} {c["bad"]:3d}')
    print('\nrated:',sum(1 for r in fb['ratings'].values() if r.get('rating')))
fb=load();a=sys.argv[1:];total=0
if '--issues' in a:
    iss=json.loads(subprocess.check_output(['gh','issue','list','-R',REPO,'--state','open','--json','number,title,body,createdAt']))
    for x in iss:
        try: items,ex=parse(x['body'])
        except Exception as e: print('skip issue',x['number'],e); continue
        total+=merge(fb,items,ex or x['createdAt']); print('issue',x['number'],len(items),'items')
        if '--close' in a:
            subprocess.run(['gh','issue','close',str(x['number']),'-R',REPO,'--comment','ingested'],check=True)
for f in [x for x in a if not x.startswith('--')]:
    items,ex=parse(open(f).read()); total+=merge(fb,items,ex)
if total: fb['updated']=datetime.datetime.now(datetime.timezone.utc).isoformat(); json.dump(fb,open(FB,'w'),indent=1,ensure_ascii=False)
print('merged',total); summary(fb)
