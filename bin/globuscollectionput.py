#!/usr/bin/env python

import os
import json
import requests
import click
import globus_sdk
from fair_research_login import NativeClient

CLIENT_ID = 'fe8e6f96-8254-4554-b4f6-0ba17e526669'

def get_https_token(collection_id, client_config='', no_browser=False):
    # returns the access token for the HTTPS collection
    # and base url of the collection,
    # e.g, https://example.edu

    ctx = click.get_current_context()
    scopes = [f'https://auth.globus.org/scopes/{collection_id}/https',
                  'urn:globus:auth:scope:transfer.api.globus.org:all']
    try:        
        if not client_config:
            client = NativeClient(client_id=CLIENT_ID, app_name='Serverless Data Examples')
            tokens = client.login(requested_scopes=scopes,
                                      no_local_server=no_browser,
                                      no_browser=no_browser,
                                      refresh_tokens=True)
            https_token = tokens[collection_id]['access_token']
            transfer_token = tokens['transfer.api.globus.org']['access_token']
        else:
            if VERBOSE:
                click.echo('Using Confidential Client')
            try:
                with open(client_config) as f:
                    c = json.load(f)
            except:
                fail_msg = f'Could not load client config file {client_config}'
                ctx.fail(fail_msg)
            client = globus_sdk.ConfidentialAppAuthClient(
                    c['client_id'], c['client_secret'])
            tokens = client.oauth2_client_credentials_tokens(requested_scopes=scopes)
            https_token = tokens.by_resource_server[collection_id]['access_token']
            transfer_token = tokens.by_resource_server['transfer.api.globus.org']['access_token']
    except:
        if fail_msg:
            ctx.fail(fail_msg)
        else:
            ctx.fail('Failed to get tokens')

    # get a TransferClient to find the base URL
    transfer_client = globus_sdk.TransferClient(
        authorizer=globus_sdk.AccessTokenAuthorizer(transfer_token))
    # get the collection info
    collection_info = transfer_client.get_endpoint(collection_id)
    try:
        base_url = collection_info['https_server']
    except:
        ctx.fail(f'HTTPS not found on collection {collection_id}')

    return (https_token, base_url)

@click.command()
@click.argument('filename')
@click.argument('destination')
@click.argument('collection_id')
@click.option('-n', '--no-browser', is_flag=True, show_default=True, default=False,
                  help='Do not use the local server and do not try to open browser. Use this when running remote (e.g., over SSH).')
@click.option('-c', '--client-config', type=str, default='', show_default=False, help='Confidential Client configuration file.')
@click.option('-v', '--verbose', is_flag=True, show_default=True, default=False, help='Print more information.')
@click.pass_context
def put_file(ctx, filename, destination,
                 collection_id, no_browser, client_config='', verbose=False):
    """
    Use HTTPS to PUT a file to a Globus Collection 

    FILENAME is the local file to be uploaded, data.json

    DESTINATION path (/foo) or URL (https://example.org/foo)

    COLLECTION_ID UUID of the Globus Collection

    \b
    By default, this is a Native App, and will prompt the user to login via
    Globus and then store their access and refresh tokens for reuse. You may
    also provide the path to a JSON file containing the client ID and secret
    of a Confidential Client specified as 'client_id' and 'client_secret':
    \b
    {
       "client_id": "82d3a...",
       "client_secret": "QmUvb..."
    }

    \b
    Follow these instructions to create a Confidential Client:
    https://docs.globus.org/api/auth/developer-guide/#register-app

    \b
    If DESTINATION is a path, it will be appended to the base URL of the
    collection to make the destination URL.

    \b
    If the destination ends with a slash, e.g. /foo/ or https://example.edu/foo/
    the file will be uploaded with its base name, like
    https://example.edu/foo/data.json. Otherwise, the DESTINATION will be the
    path of the file on the collection after upload.
    """

    global VERBOSE
    VERBOSE = verbose
    
    https_token, base_url = get_https_token(collection_id,
                                                client_config,
                                                no_browser)

    if destination.endswith('/'):
        file_basename = os.path.basename(filename)        
        destination = f'{destination}{file_basename}'

    if not destination.lower().startswith('https'):
        if destination.startswith('/'):
            destination = f'{base_url}{destination}'
        else:
            destination = f'{base_url}/{destination}'

    headers = {'Authorization': f'Bearer {https_token}'}

    if VERBOSE:
        click.echo(f'Filename: {filename}\nDestination: {destination}')

    # open file to stream out
    try:
        put_data = open(filename, 'rb')
    except:
        ctx.fail(f'Could not open file {filename}')

    try:
        resp = requests.put(destination,
                                headers=headers, data=put_data, allow_redirects=False)
        # don't believe the status code
        # Globus may attempt a step up authorization and send a page
        # with a client-side redirect
        # https://www.w3.org/TR/WCAG20-TECHS/H76.html
        if not resp.text:
            c = str(resp.status_code)
            if VERBOSE:
                click.echo(f'PUT to {destination} status {c}')
            else:
                ctx.fail(f'FAILED PUT to {destination}')
    except:
        ctx.fail(f'FAILED PUT to {destination}')


if __name__ == '__main__':
    put_file()

