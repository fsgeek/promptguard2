import sys; sys.path.insert(0,'/home/tony/projects/promptguard2')
from src.database.client import get_client
from collections import defaultdict, Counter
import statistics
db = get_client().get_database()

def load(exp, pref):
    cur=db.aql.execute('FOR d IN phase3_principle_evaluations FILTER d.experiment_id==@exp AND STARTS_WITH(d.attack_id,@p) RETURN {a:d.attack_id,t:d.turn_number,F:d.scores.F}',bind_vars={'exp':exp,'p':pref})
    seqs=defaultdict(dict)
    for r in cur: seqs[r['a']][r['t']]=float(r['F'])
    return {a:[v[t] for t in sorted(v)] for a,v in seqs.items()}

xguard = load('exp_phase3a_cumulative','xguard')
benign = load('exp_phase4_benign_cumulative','tensortrust')

ALPHA=0.3; EMA_THR=0.7; SLOPE_THR=0.15
CUSUM_K=0.10; CUSUM_H=0.40

def detect(F):
    ema=F[0]
    for i in range(len(F)):
        if i>0: ema=ALPHA*F[i]+(1-ALPHA)*ema
        if ema>=EMA_THR:
            return True,i+1
    for i in range(1,len(F)):
        if F[i]-F[i-1]>SLOPE_THR:
            return True, i+1
    S=0.0; F1=F[0]
    for i in range(len(F)):
        S=max(0.0, S + (F[i]-F1-CUSUM_K))
        if S>CUSUM_H:
            return True, i+1
    return False, None

def is_clumsy(F):
    return any(F[i]-F[i-1]>SLOPE_THR for i in range(1,len(F)))

clumsy={a:F for a,F in xguard.items() if is_clumsy(F)}
disc={a:F for a,F in xguard.items() if not is_clumsy(F)}
print('xguard total',len(xguard),'clumsy',len(clumsy),'disciplined',len(disc),'benign',len(benign))

maxlen_all=max(max(len(F) for F in xguard.values()), max(len(F) for F in benign.values()))

def frac(group,k):
    n=0;fl=0
    for F in group.values():
        if len(F)<k: continue
        n+=1
        if detect(F[:k])[0]: fl+=1
    return fl,n

def fmt(f,n): return ('%d/%d=%.2f'%(f,n,f/n)) if n else '-/0'
print()
print('%3s | %16s | %16s | %16s'%('k','CLUMSY','DISCIPLINED','BENIGN(FP)'))
for k in range(2,maxlen_all+1):
    cf,cn=frac(clumsy,k); df,dn=frac(disc,k); bf,bn=frac(benign,k)
    print('%3d | %16s | %16s | %16s'%(k,fmt(cf,cn),fmt(df,dn),fmt(bf,bn)))

def full(group):
    return sum(1 for F in group.values() if detect(F)[0]),len(group)
print()
print('Full-sequence detection:')
for name,g in [('clumsy',clumsy),('disciplined',disc),('benign',benign)]:
    fl,n=full(g); print('  %s: %d/%d=%.2f'%(name,fl,n,fl/n))

ratios=[]
for F in clumsy.values():
    d,tt=detect(F)
    if d: ratios.append(tt/len(F))
print()
print('Detected clumsy n=%d median trigger/len=%.3f min=%.2f max=%.2f'%(len(ratios),statistics.median(ratios),min(ratios),max(ratios)))
print('ratio dist:',dict(sorted(Counter(round(r,2) for r in ratios).items())))
trigs=[detect(F)[1] for F in clumsy.values() if detect(F)[0]]
print('clumsy trigger-turn dist:',dict(sorted(Counter(trigs).items())))

dr=[(detect(F)[1],len(F)) for F in disc.values() if detect(F)[0]]
print('detected disciplined (trigturn,len):',dr)

# Which branch triggers clumsy? diagnostic
def branch(F):
    ema=F[0]
    for i in range(len(F)):
        if i>0: ema=ALPHA*F[i]+(1-ALPHA)*ema
        if ema>=EMA_THR: return 'EMA',i+1
    for i in range(1,len(F)):
        if F[i]-F[i-1]>SLOPE_THR: return 'SLOPE',i+1
    S=0.0;F1=F[0]
    for i in range(len(F)):
        S=max(0.0,S+(F[i]-F1-CUSUM_K))
        if S>CUSUM_H: return 'CUSUM',i+1
    return 'none',None
bc=Counter(branch(F)[0] for F in clumsy.values())
print('clumsy first-triggering branch:',dict(bc))
bb=Counter(branch(F)[0] for F in benign.values())
print('benign first-triggering branch:',dict(bb))
