"""Fit Platt/logistic calibration only on an independent calibration split."""
import numpy as np
from sklearn.linear_model import LogisticRegression

def logits(p):
    p=np.clip(np.asarray(p),1e-5,1-1e-5);return np.log(p/(1-p)).reshape(-1,1)
def fit_calibrator(predictions,labels):return LogisticRegression(C=1.,random_state=404).fit(logits(predictions),labels)
def calibrate(calibrator,p):return calibrator.predict_proba(logits(p))[:,1]
