import pickle
import pprint

with open('list.pkl', 'rb') as f:
    l = pickle.load(f)



pprint.pprint(l)
print(len(l))