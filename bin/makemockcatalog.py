#!/usr/bin/env python
import sys
import tempfile
import random
import sqlite3
import os
import datetime
import json
from dataclasses import asdict
from string import ascii_uppercase as auc
import numpy as np
import matplotlib
from matplotlib import pyplot as plt
from PIL import Image
from serverless_data import Catalog, Dataset, DataFile

cm_names = matplotlib.colormaps.keys()

base_url = 'https://g-b0978f.0ed28.75bc.data.globus.org'

def get_random_word_maker():
    def get_random_words(count=1):
        words = []
        rows = random.sample(range(0,row_count), count)
        for row in rows:
            cursor = con.execute('select word from words where rowid={};'.format(row))
            words.append(cursor.fetchone()[0])
        if count == 1:
            return words[0]
        else:
            return words
    con = sqlite3.connect('words.db')
    cursor = con.execute('select count(word) from words;')
    row_count = cursor.fetchone()[0]
    return get_random_words

def make_image(img_size = (1024, 1024)):
    colors = [0, 1, 2]
    n = random.randint(2,4)
    x = np.linspace(0,2*np.pi, 1024)
    y = np.linspace(0,2*np.pi, 1024)
    phi = np.random.uniform(0, 2*np.pi, (n, 2, 3))
    a = np.random.uniform(0, 1, (n,3))
    cscale = np.random.uniform(0.6, 2, 3)
    waves = np.random.normal(0.24, 4, (n,2,3,2))
    img = np.zeros((1024, 1024, 3))
    xv, xy = np.meshgrid(x,y)
    for i in range(0, n):
        random.shuffle(colors)
        for c in colors:
            img[:,:,c] += a[i][c]*np.cos(xv*waves[i][0][c][0]  + xy*waves[i][1][c][0]+ phi[i][0][c])*np.cos(xv*waves[i][0][c][1] + xy*waves[i][1][c][1] + phi[i][1][c])
    for c in (0, 1, 2):
        img[:,:,c] = img[:,:,c] - img[:,:,c].min()
        img[:,:,c] = img[:,:,c]/img[:,:,c].max()
        img[:,:,c] = img[:,:,c]*cscale[c]
    img = (img*255 % 255).astype(np.uint8)
    return img

def make_colorful_image(img_size = (1024, 1024)):
    n = 3
    x = np.linspace(0,2*np.pi, img_size[0])
    y = np.linspace(0,2*np.pi, img_size[1])
    waves = np.random.uniform(0.2, 4, (n,2))
    a = np.random.uniform(0, 1, n)
    phi = np.random.uniform(0, np.pi, (n,2))
    xv, xy = np.meshgrid(x,y)
    img = np.zeros(img_size)
    for i in range(0,n):
        img += a[i]*np.sin(xv*waves[i][0]+phi[i][0])*np.sin(xy*waves[i][1] +phi[i][1])

    return img
    
def show_save(img, name, cm=None, show=True, save=True):
    fig = plt.figure(frameon=False)
    fig.set_size_inches(6,6)
    ax = plt.Axes(fig, [0.,0.,1.,1.])
    ax.set_axis_off()
    fig.add_axes(ax)
    if cm:
        ax.imshow(img, cmap=plt.get_cmap(cm))
    else:
        ax.imshow(img)
    if show:
        plt.show()
    if save:
        fig.savefig(name, dpi=120)
    plt.close()

def make_images(folder, word_maker):
    image_names = []
    words = word_maker(6)
    for firstword in words:
        img = make_image()
        imgflat = img.sum(2)
        imgflat = imgflat/imgflat.sum()
        cimg = make_colorful_image()
        b = imgflat*np.abs(cimg)**.2
        lastwords = word_maker(4)
        imgname = '{}/{}-{}.png'.format(folder, firstword, lastwords[0])
        image_names.append(imgname)
        show_save(img,imgname, show=False)

        cm = random.sample(list(cm_names),1)[0]
        imgname = '{}/{}-{}.png'.format(folder, firstword, lastwords[1])
        image_names.append(imgname)
        show_save(imgflat,imgname, cm, show=False)

        cm = random.sample(list(cm_names),1)[0]
        imgname = '{}/{}-{}.png'.format(folder, firstword, lastwords[2])
        image_names.append(imgname)
        show_save(cimg,imgname, cm, show=False)

        cm = random.sample(list(cm_names),1)[0]
        imgname = '{}/{}-{}.png'.format(folder, firstword, lastwords[3])
        image_names.append(imgname)
        show_save(b,imgname, cm, show=False)
    return image_names

def random_date_generator(range_in_days):
    days = random.randint(0,range_in_days)
    seconds = random.randint(0,24*3600)
    delta = np.timedelta64(days, 'D') + np.timedelta64(seconds, 's')
    random_date = np.datetime64(datetime.datetime.utcnow()) - delta
    return random_date

def get_mock_dataset(internal_id,
                         range_in_days,
                         tags,
                         word_getter,
                         policy,
                         cat_dir,
                         dset_dir):

    os.mkdir(dset_dir)
    created = str(random_date_generator(range_in_days))
    dset_tags = [random.choice(tags), random.choice(tags)]
    sample_name = '{}{}'.format(internal_id, random.choice(auc))

    images = make_images(dset_dir, word_getter)
    manifest = []
    for img in images:
        imgbase = os.path.basename(img)
        url = '{}/serverless/{}/{}/{}'.format(base_url, policy['access_policy'], internal_id, imgbase)
        manifest.append(DataFile(img, url=url))

    words = word_getter(2)
    for i in words:
        for j in '.rw', '':
            fname = '{}_{}{}.dat'.format(sample_name, i, j)
            url = '{}/serverless/{}/{}/{}'.format(base_url, policy['access_policy'], internal_id, fname)
            fname = '{}/{}'.format(dset_dir, fname)
            with open(fname, 'w') as f:
                f.write('Mock dat file\n')
            manifest.append(DataFile(fname, url=url))

    dd = {'name': '(Mock) {}'.format(sample_name),
              'identifier': internal_id,
              'creator': 'Rick Wagner',
              'publisher': 'UCSD',
              'created': created,
              'version': '0.1',
              'description': 'A few random images as a dataset',
              'keywords': ['image', 'random'],
              'license': 'CC BY 4.0',
              'tags': dset_tags,
              'manifest': manifest
     }
    dd.update(policy)
    mock_dset = Dataset(**dd)
    with open('{}/{}.json'.format(cat_dir, mock_dset.identifier), "w") as f:
        json.dump(asdict(mock_dset), f, indent=4)
    with open('{}/{}.md'.format(cat_dir, mock_dset.identifier), "w") as f:
        f.write(mock_dset._as_markdown())

    return mock_dset

def make_full_catalog():
    word_getter = get_random_word_maker()

    access_policies = [{'access_policy': 'public'},
                        {'access_policy': 'allusers',
      'groupname': 'Serverless Data Users',
      'groupuuid': '260da91f-3496-11ed-b941-972795fc9504'},
            {'access_policy': 'restricted',
      'groupname': 'Serverless Data Project One',
      'groupuuid': 'cf9d1f5b-3496-11ed-b941-972795fc9504'}
      ]
    tags = word_getter(4)
    range_in_days = 21
    max_datasets_per_policy = 6
    tmpdir = tempfile.TemporaryDirectory(prefix='/Users/rpwagner/tmp/mock/')
    coll_dir = '{}/collection'.format(tmpdir.name)
    os.mkdir(coll_dir)
    cat_dir = '{}/catalog'.format(tmpdir.name)
    os.mkdir(cat_dir)
    cd = {'name': 'Serverless Data Image Catalog',
              'identifier': 'serverless-images',
              'creator': 'Rick Wagner',
              'publisher': 'UCSD',
              'created': '2022-09-14',
              'version': '0.1',
              'description': 'A catalog of random images for the Serverless Research Data Repository',
              'keywords': ['research', 'data', 'schema.org', 'catalog', 'repository', 'collection'],
              'license': 'CC BY 4.0',
              'tags': 'demo',
              'datasets':[]}

    catalog = Catalog(**cd)

    print('Making mock catalog in {}'.format(tmpdir.name))
    for policy in access_policies:
        base_dir = '{}/{}'.format(coll_dir, policy['access_policy'])
        os.mkdir(base_dir)

        count = np.random.randint(2, max_datasets_per_policy)
        for internal_id in word_getter(count):
            n = random.randint(0,999)
            internal_id = '{}{:03}'.format(internal_id.upper(), n)
            dset_dir = '{}/{}'.format(base_dir, internal_id)
            dset = get_mock_dataset(internal_id, range_in_days, tags, word_getter, policy, cat_dir, dset_dir)
            catalog.datasets.append(dset)

    
    with open('{}/index.json'.format(cat_dir ), "w") as f:
        json.dump(asdict(catalog), f, indent=4)
    with open('{}/index.md'.format(cat_dir), "w") as f:
        f.write(catalog._as_markdown())            

    print('temp catalog in {}'.format(tmpdir))
    resp = input('Keep? [Y/N]\n')
    if not (resp == 'y' or resp == 'Y'):
        tmpdir.cleanup()
    else:
        for labmember in labmembers:
            for dset in labmembers[labmember]['datasets']:
                print('Adding dataset {} for {}'.format(dset.internal_id, labmember))
                magdb.add_dataset(dset)

def make_small_catalog():
    word_getter = get_random_word_maker()

    labmember = 'Rick'
    tags = word_getter(4)
    range_in_days = 21
    tmpdir = tempfile.TemporaryDirectory(prefix='/Users/rpwagner/tmp/mock/')
    print('Making mock catalog in {}'.format(tmpdir.name))

    internal_id = word_getter(1)

    n = random.randint(0,999)
    internal_id = '{}{:03}'.format(internal_id.upper(), n)
    base_dir = '{}/{}'.format(tmpdir.name, 'public')
    os.mkdir(base_dir)

    dset = get_mock_dataset(internal_id, range_in_days, tags, word_getter, {'access_policy': 'public'}, base_dir)

    print('Mock catalog in {}'.format(tmpdir.name))
    resp = input('Keep? [Y/N]\n')
    if not (resp == 'y' or resp == 'Y'):
        tmpdir.cleanup()

if __name__ == '__main__':
    if len(sys.argv) ==1:
        make_full_catalog()
    else:
        make_small_catalog()
