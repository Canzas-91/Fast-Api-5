import os

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, status

from app.routers import admin, tasks, users
from app.schemas import HealthResponse, RoomUsersResponse
from app.storage import room_manager

app = FastAPI(title="Fast API 5")
app.include_router(tasks.router)
app.include_router(users.router)
app.include_router(admin.router)


@app.get("/health", response_model=HealthResponse, tags=["system"])
def healthcheck() -> HealthResponse:
    return HealthResponse(status="ok", env=os.getenv("APP_ENV", "local"))


@app.get("/rooms/{room_id}/users", response_model=RoomUsersResponse, tags=["rooms"])
def get_room_users(room_id: str) -> RoomUsersResponse:
    return RoomUsersResponse(room_id=room_id, users=room_manager.get_users(room_id))


@app.websocket("/ws/rooms/{room_id}")
async def websocket_room(websocket: WebSocket, room_id: str) -> None:
    username = (websocket.query_params.get("username") or "").strip()
    if not username:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await room_manager.connect(room_id, username, websocket)
    await room_manager.broadcast(
        room_id,
        {"type": "user_joined", "room_id": room_id, "username": username},
    )

    try:
        while True:
            payload = await websocket.receive_json()
            text = payload.get("text", "")
            if len(text) > 300:
                await websocket.send_json(
                    {"type": "error", "detail": "Message is too long"}
                )
                continue

            await room_manager.broadcast(
                room_id,
                {
                    "type": "message",
                    "room_id": room_id,
                    "username": username,
                    "text": text,
                },
            )
    except WebSocketDisconnect:
        await room_manager.disconnect(room_id, username, websocket)
