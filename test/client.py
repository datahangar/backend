#!/usr/bin/env python3
import sys
import json
import requests
import argparse

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8080
DEFAULT_PATH = "rest/turnilo/dashboards"


def create_dashboard(host, port, json_string) -> requests.Response:
    url = f"http://{host}:{port}/{DEFAULT_PATH}"
    data = json.loads(json_string)
    response = requests.post(url, json=data)
    print_response(response)
    return response


def update_dashboard(host, port, json_string, dashboard_id) -> requests.Response:
    url = f"http://{host}:{port}/{DEFAULT_PATH}/{dashboard_id}"
    data = json.loads(json_string)
    response = requests.put(url, json=data)
    print_response(response)
    return response


def delete_dashboard(host, port, dashboard_id) -> requests.Response:
    url = f"http://{host}:{port}/{DEFAULT_PATH}/{dashboard_id}"
    response = requests.delete(url)
    print_response(response)
    return response


def get_dashboard(host, port, dashboard_id=None, shortName=None, dataCube=None) -> requests.Response:
    params = None
    url = f"http://{host}:{port}/{DEFAULT_PATH}"
    if dashboard_id:
        url = f"{url}/{dashboard_id}"
    else:
        params = {}
        if shortName:
            params["shortName"] = shortName
        if dataCube:
            params["dataCube"] = dataCube
    response = requests.get(url, params=params)
    print_response(response)
    return response


def print_response(response) -> None:
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {response.json()}")
    except ValueError:
        print(f"Response: {response.text}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Interact with the REST API to create, update, delete, or get dashboards.")
    parser.add_argument('action', choices=['create', 'update', 'delete', 'get'], help="Action to perform")
    parser.add_argument(
        'json_file_path_or_id',
        nargs='?',
        help="Path to JSON file for create/update, ID for delete/get")
    parser.add_argument('dashboard_id', nargs='?', help="ID of the dashboard to update/delete/get")
    parser.add_argument('-H', '--host', default=DEFAULT_HOST, help="Host of the API (default: 127.0.0.1)")
    parser.add_argument('-p', '--port', type=int, default=DEFAULT_PORT, help="Port of the API (default: 8080)")

    args = parser.parse_args()

    action = args.action.lower()

    if action == "create":
        if not args.json_file_path_or_id:
            sys.exit(1)
        with open(args.json_file_path_or_id, 'r') as file:
            json_string = file.read()
        create_dashboard(args.host, args.port, json_string)
    elif action == "update":
        if not args.json_file_path_or_id or not args.dashboard_id:
            sys.exit(1)
        with open(args.json_file_path_or_id, 'r') as file:
            json_string = file.read()
        update_dashboard(args.host, args.port, json_string, args.dashboard_id)
    elif action == "delete":
        if not args.json_file_path_or_id:
            sys.exit(1)
        delete_dashboard(args.host, args.port, args.json_file_path_or_id)
    elif action == "get":
        get_dashboard(args.host, args.port, args.json_file_path_or_id)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
