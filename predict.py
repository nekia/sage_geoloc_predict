import os
import urllib

# path = 'https://s3.amazonaws.com/mmcommons-tutorial/models/'
# model_path = 'models/'
# if not os.path.exists(model_path):
#     os.mkdir(model_path)
# urllib.urlretrieve(path+'RN101-5k500-symbol.json', model_path+'RN101-5k500-symbol.json')
# urllib.urlretrieve(path+'RN101-5k500-0012.params', model_path+'RN101-5k500-0012.params')

# #download test set used for evaluation
# urllib.urlretrieve('https://s3.amazonaws.com/mmcommons-tutorial/datasets/location-estimation/mediaeval2016_test', 'mediaeval2016_test')

import mxnet as mx
import logging
import numpy as np
from skimage import io, transform
from collections import namedtuple
from math import radians, sin, cos, sqrt, asin

def predict_init():
    global grids
    global ground_truth
    global Batch
    global mod
    global mean_rgb

    # Load the pre-trained model
    prefix = "models/RN101-5k500"
    load_epoch = 12
    sym, arg_params, aux_params = mx.model.load_checkpoint(prefix, load_epoch)
    mod = mx.mod.Module(symbol=sym, context=mx.cpu())
    mod.bind([('data', (1,3,224,224))], for_training=False)
    mod.set_params(arg_params, aux_params, allow_missing=True)

    # Load labels.
    grids, ground_truth = [], {}
    with open('grids.txt', 'r') as f:
        for line in f:
            line = line.strip().split('\t')
            lat = float(line[1])
            lng = float(line[2])
            grids.append((lat, lng))
    with open('mediaeval2016_test', 'r') as f:
        for line in f:
            line = line.strip().split('\t')
            imghash = line[-1]
            lng = float(line[2])
            lat = float(line[3])
            ground_truth[imghash] = (lat, lng)

    # mean image for preprocessing
    mean_rgb = np.array([123.68, 116.779, 103.939])
    mean_rgb = mean_rgb.reshape((3, 1, 1))

    Batch = namedtuple('Batch', ['data'])


def distance(p1, p2):
        R = 6371 # Earth radius in km
        lat1, lng1, lat2, lng2 = map(radians, (p1[0], p1[1], p2[0], p2[1]))
        dlat = lat2 - lat1
        dlng = lng2 - lng1
        a = sin(dlat * 0.5) ** 2 + cos(lat1) * cos(lat2) * (sin(dlng * 0.5) ** 2)
        return 2 * R * asin(sqrt(a))

def PreprocessImage(path, show_img=False):
    # load image.
    img = io.imread(path)
    # We crop image from center to get size 224x224.
    short_side = min(img.shape[:2])
    yy = int((img.shape[0] - short_side) / 2)
    xx = int((img.shape[1] - short_side) / 2)
    crop_img = img[yy : yy + short_side, xx : xx + short_side]
    resized_img = transform.resize(crop_img, (224,224))
    if show_img:
        io.imshow(resized_img)
    # convert to numpy.ndarray
    sample = np.asarray(resized_img) * 256
    # swap axes to make image from (224, 224, 3) to (3, 224, 224)
    sample = np.swapaxes(sample, 0, 2)
    sample = np.swapaxes(sample, 1, 2)
    # sub mean 
    normed_img = sample - mean_rgb
    normed_img = normed_img.reshape((1, 3, 224, 224))
    return [mx.nd.array(normed_img)]

def predict_and_evaluate(imgname, prefix='images/'):
    result = list()
    imghash = imgname[:-4]
    gt_location = ground_truth[imghash]
    # Get preprocessed batch (single image batch)
    download_yfcc(imgname, prefix)
    batch = PreprocessImage(prefix + imgname)
    # Predict and show top 5 results!
    mod.forward(Batch(batch), is_train=False)
    prob = mod.get_outputs()[0].asnumpy()[0]
    pred = np.argsort(prob)[::-1]
    print("Ground truth: ", gt_location)
    result.append(gt_location)
    for i in range(5):
        pred_loc = grids[int(pred[i])]
        dist = distance(gt_location, pred_loc)
        res = (i+1, prob[pred[i]], pred_loc, "distance: ", dist)
        print('rank=%d, prob=%f, lat=%s, lng=%s, dist from groundtruth=%f km' \
              % (i+1, prob[pred[i]], pred_loc[0], pred_loc[1], dist))
        result.append(res[2])
    return { 'lat':result[0][0], 'lng':result[0][1] }

def download_yfcc(imgname, img_directory):
    #download the image if not downloaded
    if not os.path.exists(img_directory):
        os.mkdir(img_directory)
    url_prefix = 'https://multimedia-commons.s3-us-west-2.amazonaws.com/data/images/'
    filepath = os.path.join(img_directory, imgname)
    if not os.path.exists(filepath):
        url = url_prefix + imgname[0:3] + '/' + imgname[3:6] + '/' +imgname
        filepath, _ = urllib.urlretrieve(url, filepath)
        statinfo = os.stat(filepath)
        print('Succesfully downloaded', imgname, statinfo.st_size, 'bytes.')
    return filepath

def predict(imgurl, prefix='images/'):
    download_url(imgurl, prefix)
    imgname = imgurl.split('/')[-1]
    batch = PreprocessImage(prefix + imgname)
    #predict and show top 5 results
    mod.forward(Batch(batch), is_train=False)
    prob = mod.get_outputs()[0].asnumpy()[0]
    pred = np.argsort(prob)[::-1]
    result = list()
    for i in range(5):
        pred_loc = grids[int(pred[i])]
        res = (i+1, prob[pred[i]], pred_loc)
        print('rank=%d, prob=%f, lat=%s, lng=%s' \
              % (i+1, prob[pred[i]], pred_loc[0], pred_loc[1]))
        result.append(res[2])
    return result    

def download_url(imgurl, img_directory):
    if not os.path.exists(img_directory):
        os.mkdir(img_directory)
    imgname = imgurl.split('/')[-1]
    filepath = os.path.join(img_directory, imgname)
    if not os.path.exists(filepath):
        filepath, _ = urllib.urlretrieve(imgurl, filepath)
        statinfo = os.stat(filepath)
        print('Succesfully downloaded', imgname, statinfo.st_size, 'bytes.')
    return filepath

# imgname = 'd661b83d659af4d818ddd6edf54096.jpg'
# result = predict_and_evaluate(imgname)