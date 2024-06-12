import threading
import time
import json
import signal
import pytest

import uvicorn
from fastapi import FastAPI

# REST API routes
from routes import routes

# Python Client (test it too)
from client import create_dashboard, get_dashboard, update_dashboard, delete_dashboard
from typing import Generator, Any

HOST = "127.0.0.1"
PORT = 8080


@pytest.fixture(scope="module")
def sample_dashboard() -> dict[str, str]:
    return {
        "dataCube": "networkFlows",
        "shortName": "simple_dashboard",
        "name": "Simple dashboard that shows the power of the stack",
        "hash": "<hash>"
    }


@pytest.fixture(scope="session", autouse=True)
def rest_server() -> Generator[None, Any, None]:
    app = FastAPI()
    app.include_router(routes.api_router)
    c = uvicorn.Config(app, host=HOST, port=PORT)
    server = uvicorn.Server(c)
    t = threading.Thread(target=server.run)
    t.start()
    time.sleep(3)
    yield
    server.handle_exit(signal.SIGINT, None)
    t.join()


@pytest.mark.parametrize("with_optional_fields", [True, False])
def test_create_dashboard(sample_dashboard: dict[str, Any], with_optional_fields: bool) -> None:
    dashboard = sample_dashboard.copy()
    if with_optional_fields:
        dashboard["preset"] = True
        dashboard["description"] = "This is a description"
    dashboard["id"] = 999

    # Setting the ID should fail
    res = create_dashboard(HOST, PORT, json.dumps(dashboard))
    assert res.status_code == 400

    # Create the dashboard
    dashboard.pop("id", None)
    res = create_dashboard(HOST, PORT, json.dumps(dashboard))
    got = res.json()

    # Create should populate the id, and set {preset=False, description=""}
    dashboard["id"] = 1
    if not with_optional_fields:
        dashboard["preset"] = False
        dashboard["description"] = ""
    print(f"EXPECTED:\n{dashboard}")
    print(f"GOT:\n{got}")
    assert got == dashboard

    # Cleanup
    res = delete_dashboard(HOST, PORT, 1)
    assert res.status_code == 200


def test_get_all_dashboards(sample_dashboard: dict[str, Any]) -> None:
    res = get_dashboard(HOST, PORT)
    assert res.json() == []

    # Create two dashboards
    dashboard = sample_dashboard.copy()
    res = create_dashboard(HOST, PORT, json.dumps(dashboard))
    assert res.json()["id"] == 1

    dashboard = sample_dashboard.copy()
    dashboard["dataCube"] = "myDatacube"
    dashboard["shortName"] = "shortName"
    res = create_dashboard(HOST, PORT, json.dumps(dashboard))
    assert res.json()["id"] == 2

    # Get both
    res = get_dashboard(HOST, PORT)
    dashs = res.json()
    assert len(dashs) == 2
    for dash in dashs:
        assert dash["id"] == 1 or dash["id"] == 2
        if dash["id"] == 1:
            assert dash["dataCube"] == "networkFlows"
        elif dash["id"] == 2:
            assert dash["dataCube"] == "myDatacube"

    # Cleanup
    res = delete_dashboard(HOST, PORT, 1)
    assert res.status_code == 200
    res = delete_dashboard(HOST, PORT, 2)
    assert res.status_code == 200


def test_get_all_dashboards_query_params(sample_dashboard: dict[str, Any]) -> None:
    res = get_dashboard(HOST, PORT)
    assert res.json() == []

    # Create two dashboards
    dashboard = sample_dashboard.copy()
    res = create_dashboard(HOST, PORT, json.dumps(dashboard))
    assert res.json()["id"] == 1

    dashboard = sample_dashboard.copy()
    dashboard["dataCube"] = "myDatacube"
    dashboard["shortName"] = "shortName"
    res = create_dashboard(HOST, PORT, json.dumps(dashboard))
    assert res.json()["id"] == 2

    # Try with invalid query params
    res = get_dashboard(HOST, PORT, shortName=" ")
    assert res.status_code == 400
    res = get_dashboard(HOST, PORT, dataCube=" ")
    assert res.status_code == 400
    res = get_dashboard(HOST, PORT, shortName="name;test")
    assert res.status_code == 400
    res = get_dashboard(HOST, PORT, dataCube="name;test")
    assert res.status_code == 400
    res = get_dashboard(HOST, PORT, shortName="name?test")
    assert res.status_code == 400
    res = get_dashboard(HOST, PORT, dataCube="name?test")
    assert res.status_code == 400
    res = get_dashboard(HOST, PORT, shortName="name'test")
    assert res.status_code == 400
    res = get_dashboard(HOST, PORT, dataCube="name'test")
    assert res.status_code == 400
    res = get_dashboard(HOST, PORT, shortName="name\"test")
    assert res.status_code == 400
    res = get_dashboard(HOST, PORT, dataCube="name\"test")
    assert res.status_code == 400
    long_name = 's' * 280
    res = get_dashboard(HOST, PORT, shortName=long_name)
    assert res.status_code == 400
    res = get_dashboard(HOST, PORT, dataCube=long_name)
    assert res.status_code == 400

    # Now validate functionality

    # Name only
    res = get_dashboard(HOST, PORT, shortName="simple_dashboard")
    assert res.status_code == 200
    assert len(res.json()) == 1
    assert res.json()[0]["id"] == 1
    res = get_dashboard(HOST, PORT, shortName="shortName")
    assert res.status_code == 200
    assert len(res.json()) == 1
    assert res.json()[0]["id"] == 2
    res = get_dashboard(HOST, PORT, shortName="shortNameA")
    assert res.status_code == 200
    assert len(res.json()) == 0
    res = get_dashboard(HOST, PORT, shortName="shortName2")
    assert res.status_code == 200
    assert len(res.json()) == 0

    # DataCube only
    res = get_dashboard(HOST, PORT, dataCube="networkFlows")
    assert res.status_code == 200
    assert len(res.json()) == 1
    assert res.json()[0]["id"] == 1
    res = get_dashboard(HOST, PORT, dataCube="myDatacube")
    assert res.status_code == 200
    assert len(res.json()) == 1
    assert res.json()[0]["id"] == 2
    res = get_dashboard(HOST, PORT, dataCube="networkFlowsA")
    assert res.status_code == 200
    assert len(res.json()) == 0
    res = get_dashboard(HOST, PORT, dataCube="networkFlows2")
    assert res.status_code == 200
    assert len(res.json()) == 0

    # Both
    res = get_dashboard(HOST, PORT, dataCube="networkFlows", shortName="simple_dashboard")
    assert res.status_code == 200
    assert len(res.json()) == 1
    assert res.json()[0]["id"] == 1
    res = get_dashboard(HOST, PORT, dataCube="myDatacube", shortName="shortName")
    assert res.status_code == 200
    assert len(res.json()) == 1
    assert res.json()[0]["id"] == 2
    res = get_dashboard(HOST, PORT, dataCube="networkFlowsA", shortName="shortNameA")
    assert res.status_code == 200
    assert len(res.json()) == 0
    res = get_dashboard(HOST, PORT, dataCube="networkFlows2", shortName="shortName2")
    assert res.status_code == 200
    assert len(res.json()) == 0

    # Cleanup
    res = delete_dashboard(HOST, PORT, 1)
    assert res.status_code == 200
    res = delete_dashboard(HOST, PORT, 2)
    assert res.status_code == 200


def test_update_dashboard(sample_dashboard: dict[str, Any]) -> None:
    dashboard = sample_dashboard.copy()

    # Create dashboard
    res = create_dashboard(HOST, PORT, json.dumps(dashboard))
    got = res.json()
    dashboard["description"] = ""
    dashboard["preset"] = False
    dashboard["id"] = 1

    print(f"EXPECTED:\n{dashboard}")
    print(f"GOT:\n{got}")
    assert got == dashboard

    dashboard["name"] = "Updated Dashboard Name"
    res = update_dashboard(HOST, PORT, json.dumps(dashboard), 1)
    assert res.status_code == 200

    res = get_dashboard(HOST, PORT, 1)
    got = res.json()
    print(f"EXPECTED:\n{dashboard}")
    print(f"GOT:\n{got}")
    assert got == dashboard

    # Cleanup
    res = delete_dashboard(HOST, PORT, 1)
    assert res.status_code == 200


def test_delete_dashboard(sample_dashboard: dict[str, Any]) -> None:
    dashboard = sample_dashboard.copy()

    # Create dashboard
    res = create_dashboard(HOST, PORT, json.dumps(dashboard))
    got = res.json()
    dashboard["description"] = ""
    dashboard["preset"] = False
    dashboard["id"] = 1

    print(f"EXPECTED:\n{dashboard}")
    print(f"GOT:\n{got}")
    assert got == dashboard

    # Delete an inexistent Dashbaord
    res = delete_dashboard(HOST, PORT, 99)
    assert res.status_code == 404

    # Cleanup
    res = delete_dashboard(HOST, PORT, 1)
    assert res.status_code == 200

    # 100% dead
    res = delete_dashboard(HOST, PORT, 1)
    assert res.status_code == 404
