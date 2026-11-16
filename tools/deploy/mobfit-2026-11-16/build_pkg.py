import pathlib, difflib, hashlib, json
import sys
W=pathlib.Path(sys.argv[1]); B,A=W/'before',W/'after'
ANCHOR='<style id="tel-plain">'
rows=[]
for fa in sorted(A.rglob('index.php')):
    rel=fa.relative_to(A).as_posix(); b=(B/rel).read_text(encoding='utf-8'); a=fa.read_text(encoding='utf-8')
    style=a[a.index('<style id="mob-fit">'):a.index(ANCHOR)]
    ops=[[ANCHOR, style+ANCHOR, 1]]
    t=b.replace(ANCHOR, style+ANCHOR, 1)
    bl=t.splitlines(True); al=a.splitlines(True)
    for tag,i1,i2,j1,j2 in difflib.SequenceMatcher(None,bl,al,autojunk=False).get_opcodes():
        if tag=='equal': continue
        assert tag=='replace', (rel,tag)
        old=''.join(bl[i1:i2]); new=''.join(al[j1:j2]); assert t.count(old)==1, rel
        ops.append([old,new,1])
    # self-test
    x=b
    for o,n,c in ops:
        assert x.count(o)==c; x=x.replace(o,n)
    assert x==a, rel
    rows.append({'file':rel,'before':hashlib.sha256(b.encode()).hexdigest(),'after':hashlib.sha256(a.encode()).hexdigest(),'replace':ops})
json.dump({'name':'mobfit-2026-11-16','pages':len(rows),'files':rows},open(pathlib.Path(__file__).parent/'deploy_payload.json','w'),ensure_ascii=False)
print(len(rows), sum(len(r['replace']) for r in rows), (pathlib.Path(__file__).parent/'deploy_payload.json').stat().st_size)
