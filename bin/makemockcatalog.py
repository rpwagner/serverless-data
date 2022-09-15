#!/usr/bin/env python
import sys
import tempfile
import random
import sqlite3
import os
import datetime
import json
from string import ascii_uppercase as auc
import numpy as np
from PIL import Image
import magdb
import magdb_types.raw_data as raw_data
import magdb_types.material.nanoparticle as nano
import magdb_types.research.magnetometry as magnet


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

def make_image(img_name='array'):
    funcs = (np.cos, np.tan, np.sin)
    img_size = (2048, 2048)
    n = random.randint(1,6)
    x = np.linspace(0,2*np.pi, 2048)
    y = np.linspace(0,2*np.pi, 2048)
    phi = np.random.uniform(0, 2*np.pi, (n, 2, 3))
    a = np.random.uniform(0, 1, (n,3))
    waves = np.random.normal(3, 4, (n,2,3))
    img = np.zeros((2048, 2048, 3))
    xv, xy = np.meshgrid(x,y)
    for i in range(0, n):
        for j in (0, 1, 2):
            c = random.randint(0,2)
            fx = random.choice(funcs)
            fy = random.choice(funcs)
            img[:,:,c] += a[i][j]*fx(xv*waves[i][0][j] + phi[i][0][j])*fy(xy*waves[i][1][j] + phi[i][1][j])
    img = (img*255 % 255).astype(np.uint8)
    a = Image.fromarray(img)
    a.save(img_name+'.tif')
    a = a.resize((512, 512))
    a.save(img_name+'.png')

def make_histogram(n_hist=20):
    twofivefive = (np.ones(n_hist, dtype=np.int64)*255).tolist()
    hist = {"area": [], "mean": [], "min": [], "max": []}
    hist["area"] = (9.5 + np.random.random_sample(n_hist)*110).tolist()
    hist["mean"] = twofivefive
    hist["min"] = twofivefive
    hist["max"] = twofivefive
    return hist

def random_date_generator(range_in_days):
    days = random.randint(0,range_in_days)
    seconds = random.randint(0,24*3600)
    delta = np.timedelta64(days, 'D') + np.timedelta64(seconds, 's')
    random_date = np.datetime64(datetime.datetime.utcnow()) - delta
    return random_date

def get_mock_dataset(labmember,
                         internal_id,
                         range_in_days,
                         materials,
                         shapes,
                         tags,
                         word_getter,
                         base_dir):
    dset_dir = '{}/{}/{}'.format(base_dir, labmember, internal_id)
    os.mkdir(dset_dir)
    for d in 'TEM', 'Magnetometry':
        os.mkdir('{}/{}'.format(dset_dir, d))

    created = str(random_date_generator(range_in_days))
    dset_tags = {random.choice(tags), random.choice(tags)}
    material = random.choice(materials)
    shape = random.choice(shapes)
    size = 6 + random.random()*6
    rsd = 0.08 + random.random()*0.07
    mass = 1.2 + random.random()*4.1
    histogram = make_histogram()
    sample_name = '{}{}'.format(internal_id, random.choice(auc))

    manifest = []
    for i in 8, 14, 15, 19:
        image_name = '{}/TEM/{}_30kx_{}'.format(dset_dir, sample_name, i)
        make_image(image_name)
        tif_tem = raw_data.TEM_File(
              local_filename='{}.tif'.format(image_name),
               magnification=30000,)
        png_tem = raw_data.TEM_File(
              local_filename='{}.png'.format(image_name),
               magnification=30000,)
        manifest.append(tif_tem)
        manifest.append(png_tem)            
    
    mock_tem = nano.TEM(
        raw_data=raw_data.TEM_RD(
            manifest=manifest
            ),
            histogram=histogram,
            size=size,
            rsd=rsd,
            shape=shape,
        )

    mock_np = nano.Nanoparticle(
        characterization_methods=mock_tem,
        nominal_molecular_formula="Fe3O4",
        common_name=material,
    )

    mock_mag_sample = magnet.MagSample(
        sample_name=sample_name, sample_holder="vsm", mass=mass
    )

    for i in 'MvSH', 'ZFCFC':
        for j in '.rw', '':
            with open('{}/Magnetometry/{}_{}{}.dat'.format(dset_dir, sample_name, i, j), 'w') as f:
                f.write('Mock dat file\n')

    mock_mvsh = raw_data.Magnetometry_File(
        data_type="dc",
        dc_meas_type="dc_scan",
        temperature=[5, 300],
        local_filename='{}/Magnetometry/{}_MvSH.dat'.format(dset_dir, sample_name),
        )

    mock_mvsh_raw = raw_data.Magnetometry_File(
        local_filename='{}/Magnetometry/{}_MvSH.rw.dat'.format(dset_dir, sample_name)
        )

    mock_zfcfc = raw_data.Magnetometry_File(
        data_type="dc",
        dc_meas_type="dc_scan",
        field=100,
        zfcfc="zfcfc",
        local_filename='{}/Magnetometry/{}_ZFCFC.dat'.format(dset_dir, sample_name),
        )

    mock_zfcfc_raw = raw_data.Magnetometry_File(
        local_filename='{}/Magnetometry/{}_ZFCFC.rw.dat'.format(dset_dir, sample_name)
        )

    mock_mag_rd = raw_data.Magnetometry_RD(
        manifest=[mock_mvsh, mock_mvsh_raw, mock_zfcfc, mock_zfcfc_raw]
        )

    
    mock_magnet = magnet.Magnetometry(
        raw_data=mock_mag_rd, sample_info=mock_mag_sample
        )

    mock_dset = magdb.Dataset(
        internal_id=internal_id,
        material=mock_np,
        research=mock_magnet,
        tags=dset_tags,
        labname=labmember
        )

    with open('{}/{}.json'.format(dset_dir, sample_name), "w") as f:
        json.dump(mock_dset, f, indent=4, default=magdb.magdb_dc.encoder_default)

    return mock_dset

def make_full_catalog():
    word_getter = get_random_word_maker()

    labmembers = {'Kyle': {}, 'Angelica': {},  'Phil': {}, 'Rick': {}}
    tags = word_getter(4)
    materials = ['magnetite', 'maghemite', 'mocketite']
    shapes = ['sphere', 'triangle', 'cube', 'hexago', 'oval', 'prism', 'rod', 'tube', 'helix']
    range_in_days = 21
    max_datasets_per_member = 5
    tmpdir = tempfile.TemporaryDirectory(prefix='/Users/rpwagner/tmp/mock/')
    print('Making mock catalog in {}'.format(tmpdir.name))
    for labmember in labmembers:
        os.mkdir('{}/{}'.format(tmpdir.name, labmember))
        labmembers[labmember]['datasets'] = []
        count = np.random.randint(2, max_datasets_per_member)
        for internal_id in word_getter(count):
            n = random.randint(0,999)
            internal_id = '{}{:03}'.format(internal_id.upper(), n)
            dset = get_mock_dataset(labmember, internal_id,
                                     range_in_days, materials, shapes, tags, word_getter, tmpdir.name)
            labmembers[labmember]['datasets'].append(dset)

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
    materials = ['magnetite', 'maghemite', 'mocketite']
    shapes = ['sphere', 'triangle', 'cube', 'hexago', 'oval', 'prism', 'rod', 'tube', 'helix']
    range_in_days = 21
    tmpdir = tempfile.TemporaryDirectory(prefix='/Users/rpwagner/tmp/mock/')
    print('Making mock catalog in {}'.format(tmpdir.name))

    os.mkdir('{}/{}'.format(tmpdir.name, labmember))
    internal_id = word_getter(1)
    n = random.randint(0,999)
    internal_id = '{}{:03}'.format(internal_id.upper(), n)
    dset = get_mock_dataset(labmember, internal_id,
                                     range_in_days, materials, shapes, tags, word_getter, tmpdir.name)

    print('Mock catalog in {}'.format(tmpdir.name))
    resp = input('Keep? [Y/N]\n')
    if not (resp == 'y' or resp == 'Y'):
        tmpdir.cleanup()
    else:
        magdb.add_dataset(dset)

if __name__ == '__main__':
    #make_small_catalog()
    if len(sys.argv) ==1:
        make_full_catalog()
    else:
        make_small_catalog()
