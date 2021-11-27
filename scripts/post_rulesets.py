#!/usr/bin/python
#
# POST rulesets files to Zentral
#
import argparse
import os
import json
import sys
from urllib.error import HTTPError
from urllib.request import urlopen, Request


def get_api_token():
    api_token = os.environ.get("ZTL_API_TOKEN")
    if not api_token:
        raise ValueError("Could not get API token")
    return api_token


def iter_files(rootdir):
    for dirpath, _, filenames in os.walk(rootdir):
        for filename in filenames:
            _, extension = os.path.splitext(filename)
            if extension in (".json",):
                yield os.path.join(dirpath, filename)


def post_file(filepath, url, token, configuration):
    with open(filepath, "r") as f:
        ruleset = json.load(f)
    ruleset["configurations"] = [configuration]
    req = Request(
        url,
        data=json.dumps(ruleset).encode("utf-8"),
        headers={
            "Authorization": f"Token {token}",
            "Content-Type": "application/json"
        }
    )
    resp = urlopen(req)
    resp_json = json.loads(resp.read().decode("utf-8"))
    return resp.status == 200, resp_json


def run(args, token):
    url = f"https://{args.fqdn}/api/santa/rulesets/update/"
    if args.dry_run:
        url = f"{url}?dryRun"
    exit_code = 0
    results = {"dry_run": args.dry_run,
               "fqdn": args.fqdn,
               "configuration": args.configuration,
               "files": []}
    for filepath in iter_files(args.rootdir):
        try:
            ok, resp_json = post_file(filepath, url, token, args.configuration)
        except HTTPError as e:
            ok = False
            if e.code == 400:
                resp_json = json.loads(e.read().decode("utf-8"))
            else:
                resp_json = {"exception": str(e)}
        except Exception as e:
            ok, resp_json = False, {"exception": str(e)}
        if not ok:
            exit_code = 1
        results["files"].append({"file": filepath, "ok": ok, "response": resp_json})
    print(json.dumps(results, indent=2))
    sys.exit(exit_code)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='POST ruleset files to Zentral')
    parser.add_argument('rootdir', help='A directory containing ruleset files')
    parser.add_argument('fqdn', help='The FQDN of the Zentral server')
    parser.add_argument('configuration', help='The name of the Santa configuration')
    parser.add_argument('--dry-run', action='store_true', help='If set, the changes are not persisted in the DB')
    args = parser.parse_args()
    token = get_api_token()
    run(args, token)
