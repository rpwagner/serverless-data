import os
from matplotlib import pyplot as plt
from IPython.display import display, Markdown
import ipywidgets as widgets
import magdb
import magdb_types
import magdb_types.raw_data as raw_data
import magdb_types.material.nanoparticle as nano
import magdb_types.research.magnetometry as magnet

active = {}
def display_active_dataset():
    if not 'dataset' in active:
        return
    dset = active['dataset']
    dd = dset._as_dict()
    md_text = '# Dataset: {}/{}\n'.format(dd['labname'], dd['internal_id'])
    md_text += '- Created: {}\n'.format(dd['created'])
    if dd['tags']:
        md_text += '- Tags\n'
        for t in dd['tags']:
            md_text += '  - {}\n'.format(t)
    md_text += '## Material\n'
    material = dd['material']
    md_text += '- Common Name: {}\n'.format(material['common_name'])
    md_text += '- Nominal Molecular Formula: {}\n'.format(material['nominal_molecular_formula'])
    md_text += '### TEM\n'
    tem = material['characterization_methods'][0]
    md_text += '- Size: {:0.2f}\n'.format(tem['size'])
    md_text += '- RSD: {:0.2f}\n'.format(tem['rsd'])
    md_text += '- Shape: {}\n'.format(tem['shape'])
    md_text += '#### Histogram\n'
    p = plt.plot(dd['material']['characterization_methods'][0]['histogram']['area'], 'o')
    md_text += '#### TEM Images\n'
    png_urls = []
    for f in dset.get_manifest():
        if f.url.endswith('.png'):
            png_urls.append((os.path.basename(f.url), 'https://'+f.url))

    md_text += '| ![{}]({}) |  ![{}]({}) |   \n'.format(png_urls[0][0], png_urls[0][1], png_urls[1][0], png_urls[1][1])
    md_text += '| ![{}]({}) |  ![{}]({}) |   \n'.format(png_urls[2][0], png_urls[2][1], png_urls[3][0], png_urls[3][1])
    display(Markdown(md_text))

def _get_dataset(dset, display=True):
    active['dataset'] = magdb.get_dataset(dset[1], dset[0])

def dataset_picker():
    dsets = magdb.list_datasets()

    options = []
    for dset in dsets:
        o_name = '{}: {}'.format(dset['labname'], dset['internal_id'])
        options.append((o_name, ( dset['labname'], dset['internal_id']) ))

    output = widgets.Output()
    button = widgets.Button(description="Get selected dataset")
    dropdown = widgets.Dropdown(
        options=options,
        value=None,
        description='Select dataset:',
        disabled=False,
    )
    display_button = widgets.Button(description="Display active dataset", enabled=False)

    def on_value_change(change):
        active['dset_tuple'] = change['new']

    def on_button_clicked(b):
        display_button.enabled = True
        with output:
            print('Getting dataset {}: {}.'.format(active['dset_tuple'][0], active['dset_tuple'][1]))
        _get_dataset(active['dset_tuple'])
    
    button.on_click(on_button_clicked)
    dropdown.observe(on_value_change, names='value')
    display(dropdown, button, output)
