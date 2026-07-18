import httpx
import pytest

from cortex.app import app


@pytest.mark.asyncio
async def test_api_goal_and_bounded_run() -> None:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        created = await client.post("/goals", json={"title": "hello"})
        assert created.status_code == 200
        goal_id = created.json()["goal_id"]
        started = await client.post(f"/goals/{goal_id}/run")
        assert started.status_code == 200
        run_id = started.json()["run_id"]
        for _ in range(8):
            await client.post(f"/runs/{run_id}/step")
        result = await client.get(f"/runs/{run_id}")
        assert result.json()["status"] == "completed"
        events = await client.get(f"/runs/{run_id}/events")
        assert events.status_code == 200
        assert events.json()[-1]["event_type"] == "RunCompleted"
        published = await client.post(
            "/events", json={"event_type": "external", "payload": {"ok": "yes"}}
        )
        assert published.status_code == 200
        assert published.json()["accepted"] == "external"
