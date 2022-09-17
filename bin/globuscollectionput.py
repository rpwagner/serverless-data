#!/usr/bin/env python

import os
import sys
import json
import requests
import click
import globus_sdk
from fair_research_login import NativeClient
    
# By default, we will assume this is Native App
# If you want to use this as a service script,
# Register a new app with Globus and put your own
# Confidential Client ID and Secret here
# https://docs.globus.org/api/auth/developer-guide/#register-app
# https://developers.globus.org/

CLIENT_ID = 'fe8e6f96-8254-4554-b4f6-0ba17e526669'

def get_https_token(collection_id, client_config=''):
    # returns the access token for the HTTPS collection
    # and base url of the collection,
    # e.g, https://g-b0978f.0ed28.75bc.data.globus.org

    scopes = [f'https://auth.globus.org/scopes/{collection_id}/https',
                  'urn:globus:auth:scope:transfer.api.globus.org:all']
    try:        
        if not client_config:
            client = NativeClient(client_id=CLIENT_ID, app_name='Serverless Data Examples')
            tokens = client.login(requested_scopes=scopes, refresh_tokens=True)
            https_token = tokens[collection_id]['access_token']
            transfer_token = tokens['transfer.api.globus.org']['access_token']
        else:
            if VERBOSE:
                click.echo('Using Confidential Client')
            try:
                with open(client_config) as f:
                    c = json.load(f)
            except:
                click.echo(f'Could not load client config file {client_config}')
                sys.exit()
            client = globus_sdk.ConfidentialAppAuthClient(
                    c['client_id'], c['client_secret'])
            tokens = client.oauth2_client_credentials_tokens(requested_scopes=scopes)
            https_token = tokens.by_resource_server[collection_id]['access_token']
            transfer_token = tokens.by_resource_server['transfer.api.globus.org']['access_token']
    except:
        click.echo('Failed to get tokens')
        sys.exit()

    # get a TransferClient to find the base URL
    transfer_client = globus_sdk.TransferClient(
        authorizer=globus_sdk.AccessTokenAuthorizer(transfer_token))
    # get the collection info
    collection_info = transfer_client.get_endpoint(collection_id)
    try:
        base_url = collection_info['https_server']
    except:
        click.echo(f'HTTPS not found on collection {collection_id}')
        sys.exit()

    return (https_token, base_url)

@click.command()
@click.argument('filename')
@click.argument('destination')
@click.argument('collection_id')
@click.option('-c', '--client-config', type=str, default='', show_default=False, help='Confidential Client configuration file.')
@click.option('-v', '--verbose', is_flag=True, show_default=True, default=False, help='Print more information.')
def put_file(filename, destination,
                 collection_id, client_config='', verbose=False):
    """
    Use HTTPS to PUT a file to a Globus Collection 

    FILENAME is the local file to be uploaded, data.json

    DESTINATION path (/foo) or URL (https://example.org/foo)

    COLLECTION_ID UUID of the Globus Collection

    \b
    By default, this is a Native App, and will prompt the user
    to login via Globus and then store their access and refresh
    tokens for reuse. You may also provide the path to a JSON
    file containign the client ID and secret of a Confidential
    Client specified as 'client_id' and 'client_secret', e.g.,
    \b
    {
       "client_id": "82d3a...",
       "client_secret": "QmUvb..."
    }


    \b
    If DESTINATION is a path, it will be appended to the base URL
    of the collection to make the destination URL.

    \b
    If the destination ends with a slash, e.g. /foo/ or
    https://g-b0978f.0ed28.75bc.data.globus.org/foo/,
    the file will be uploaded with its base name, like
    https://g-b0978f.0ed28.75bc.data.globus.org/foo/data.json
    Otherwise, the DESTINATION will be path the file on the
    collection after upload.
    """

    global VERBOSE
    VERBOSE = verbose
    
    https_token, base_url = get_https_token(collection_id,
                                                client_config)

    if not destination.startswith('https'):
        if destination.startswith('/'):
            destination_url = f'{base_url}{destination}'
        else:
            destination_url = f'{base_url}/{destination}'

    if destination.endswith('/'):
        file_basename = os.path.basename(filename)        
        destination_url = f'{destination_url}{file_basename}'

    headers = {'Authorization': f'Bearer {https_token}'}

    if VERBOSE:
        click.echo(f'Filename: {filename}\nDestination: {destination_url}')

    # open file to stream out
    try:
        put_data = open(filename, 'rb')
    except:
        click.echo(f'Could not open file {filename}')
        sys.exit()

    resp = requests.put(destination_url,
                            headers=headers, data=put_data, allow_redirects=False)
    # don't believe the status code
    # Globus may attempt a step up authorization and send a page
    # with a client-side redirect
    # https://www.w3.org/TR/WCAG20-TECHS/H76.html
    if not resp.text:
        c = str(resp.status_code)
        if VERBOSE:
            click.echo(f'PUT to {destination_url} status {c}')
    else:
        click.echo(f'FAILED PUT to {destination_url}')
        sys.exit()

if __name__ == '__main__':
    put_file()

