"""Fit a lightweight offline intent classifier on authored question examples."""
import json
from pathlib import Path

import joblib
from sklearn.pipeline import make_pipeline, FeatureUnion
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

folder = Path(__file__).resolve().parents[1] / "models/mission_qa"
questions = json.loads((folder / "questions.json").read_text())
train, train_labels, test, test_labels = [], [], [], []
for label, examples in questions.items():
    train.extend(examples[:9])
    train_labels.extend([label] * 9)
    test.extend(examples[9:])
    test_labels.extend([label] * (len(examples) - 9))
model = make_pipeline(FeatureUnion([
    ('words', TfidfVectorizer(ngram_range=(1,2),sublinear_tf=True)),
    ('characters', TfidfVectorizer(analyzer='char_wb',ngram_range=(3,5),sublinear_tf=True)),
]), LogisticRegression(max_iter=1500,C=18,random_state=404))
model.fit(train,train_labels)
labels = model.predict(test)
score = {"training_questions":len(train),"held_out_questions":len(test),"topics":len(questions),
         "intent_accuracy":accuracy_score(test_labels,labels),
         "dataset":"Hand-authored synthetic questions, split by phrasing within each topic",
         "errors":[{"question":q,"expected":y,"predicted":p} for q,y,p in zip(test,test_labels,labels) if y != p]}
joblib.dump(model,folder/'intent.joblib',compress=3)
(folder/'evaluation.json').write_text(json.dumps(score,indent=2)+'\n')
print(json.dumps(score,indent=2))
