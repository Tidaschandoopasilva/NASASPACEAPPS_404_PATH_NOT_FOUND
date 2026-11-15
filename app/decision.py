"""Expected value of sample information, with one binary corridor observation."""
from math import erf,sqrt

def sensor_rates(sigma=.08,tau=.2):
    
    cdf=lambda x:.5*(1+erf(x/sqrt(2)))
    return 1-cdf((tau-.282915)/sigma),1-cdf((tau-.09748)/sigma)
def posterior(p,o,tpr,fpr):
    a=tpr if o else 1-tpr;b=fpr if o else 1-fpr;den=a*p+b*(1-p)
    return a*p/den if den else p

def estimate(p=.3,cost=5,detour=28,sigma=.08,rover_minutes=3):
    tpr,fpr=sensor_rates(sigma);positive=tpr*p+fpr*(1-p)
    loss=lambda p:min(100*p,detour)
    before=loss(p);after=sum(prob*loss(posterior(p,o,tpr,fpr)) for o,prob in [(1,positive),(0,1-positive)])
    total=cost+rover_minutes;vos=before-after-total
    return {'prior':p,'tpr':tpr,'fpr':fpr,'expected_loss_now':before,'expected_loss_after':after,'scout_cost':total,'vos':vos,'recommendation':'SCOUT' if vos>0 else ('AVOID' if 100*p>detour else 'PROCEED'),'why':f'Expected information saves {before-after:.2f} utility units; scouting costs {total:.2f}. Proceed loss = {100*p:.2f}; avoid detour = {detour:.2f}.','units':'assumed utility units; time penalties in minutes'}
