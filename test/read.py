import pickle
import pprint

with open('./test/list.pkl', 'rb') as f:
    l = pickle.load(f)



pprint.pprint(l)