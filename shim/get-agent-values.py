#!/usr/bin/python3

import requests, json, os, sys

ENTITY        = os.getenv('CLIENT_ENTITY', 'dev')
AGENT_ADDR    = os.getenv('VAULT_AGENT_ADDR', 'http://agent:8100')

try:
    CONN_STR = AGENT_ADDR + '/v1/secret/data/b2share/' + ENTITY + '/application'
    r = requests.get(CONN_STR)
    secrets = json.dumps(r.json()['data']['data'], indent = 2)
except:
    secrets = None
    sys.exit(f"NOTE -- VAULT AGENT did not respond at {AGENT_ADDR}.\nNOTE -- Has it been started before B2SHARE?\nNOTE -- Ignore this message, if Vault is not used for secrets.")


# Write secrets to a file, which if found, will be imported in config.py
if secrets is not None:
    with open('/eudat/b2share/b2share/secrets.py', 'w') as out_file:
        for var, val in json.loads(secrets).items():
            var = var.replace("B2SHARE_", "")
            if var == "PID_HANDLE_CREDENTIALS":
                out_file.write(f"{var} = {val}\n")
            else:
                out_file.write(f"{var} = '{val}'\n")

    # Write secrets as .json
    with open('/eudat/b2share/b2share/secrets.json', 'w') as out_file_j:
        out_file_j.write(secrets)


# Check if we have certificates to get
try:
    CRT_CONN_STR = AGENT_ADDR + '/v1/secret/data/b2share/' + ENTITY + '/certificates'
    rc = requests.get(CRT_CONN_STR)
    certs = json.dumps(rc.json()['data']['data'], indent = 2)
except:
    certs = None
    print(f"\nNOTE -- No certificates at {AGENT_ADDR}.\n")

if certs is not None:
    for var, val in json.loads(certs).items():
        with open(f'/usr/var/b2share-instance/{var}', 'w') as out_file:
            out_file.write(f"{val}")
