import os
import urllib

path = 'https://s3.amazonaws.com/mmcommons-tutorial/models/'
model_path = 'models/'
if not os.path.exists(model_path):
    os.mkdir(model_path)
urllib.urlretrieve(path+'RN101-5k500-symbol.json', model_path+'RN101-5k500-symbol.json')
urllib.urlretrieve(path+'RN101-5k500-0012.params', model_path+'RN101-5k500-0012.params')

#download test set used for evaluation
urllib.urlretrieve('https://s3.amazonaws.com/mmcommons-tutorial/datasets/location-estimation/mediaeval2016_test', 'mediaeval2016_test')
