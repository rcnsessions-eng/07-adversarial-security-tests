import asyncio
import os
import sys
import uuid

import httpx


async def main() -> None:
    async with httpx.AsyncClient(timeout=5, trust_env=False) as http:
        endpoint = os.environ["LEARNING_IDP_URL"] + "/protocol/openid-connect/token"
        user = await http.post(
            endpoint,
            data={
                "grant_type": "password",
                "client_id": "learning-client",
                "username": "learner-red-1",
                "password": os.environ["LEARNING_DEMO_PASSWORD"],
            },
        )
        workload = await http.post(
            endpoint,
            data={
                "grant_type": "client_credentials",
                "client_id": "agent-adapter",
                "client_secret": os.environ["LEARNING_AGENT_SECRET"],
            },
        )
        assert user.status_code == workload.status_code == 200
        user_token = user.json()["access_token"]
        workload_token = workload.json()["access_token"]
        response = await http.post(
            os.environ["LEARNING_GATEWAY_URL"] + "/v1/delegated/tools/evidence.record",
            headers={
                "Authorization": "Bearer " + user_token,
                "X-Workload-Authorization": "Bearer " + workload_token,
            },
            json={
                "args": {
                    "course_id": "course-red",
                    "kind": "content_read",
                    "idempotency_key": uuid.uuid4().hex,
                }
            },
        )
        expected = 503 if sys.argv[1] == "denied" else 200
        assert response.status_code == expected
        if expected == 503:
            assert "created" not in response.text and "receipt" not in response.text
        else:
            assert response.json()["status"] == "created"
        assert user_token not in response.text and workload_token not in response.text
    print(
        "Actual OPA "
        + (
            "outage denied protected write"
            if expected == 503
            else "recovery permitted authorized write"
        )
    )


if __name__ == "__main__":
    asyncio.run(main())
