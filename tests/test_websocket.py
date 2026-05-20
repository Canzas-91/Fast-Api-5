import pytest
from starlette.websockets import WebSocketDisconnect


def test_connect_with_valid_username(client):
    with client.websocket_connect("/ws/rooms/python?username=alice") as websocket:
        event = websocket.receive_json()

    assert event == {
        "type": "user_joined",
        "room_id": "python",
        "username": "alice",
    }


def test_message_round_trip(client):
    with client.websocket_connect("/ws/rooms/python?username=alice") as websocket:
        websocket.receive_json()
        websocket.send_json({"type": "message", "text": "Всем привет"})
        response = websocket.receive_json()

    assert response == {
        "type": "message",
        "room_id": "python",
        "username": "alice",
        "text": "Всем привет",
    }


def test_two_clients_receive_same_message(client):
    with client.websocket_connect("/ws/rooms/python?username=alice") as alice:
        alice.receive_json()
        with client.websocket_connect("/ws/rooms/python?username=bob") as bob:
            alice.receive_json()
            bob.receive_json()

            alice.send_json({"type": "message", "text": "hello"})

            alice_message = alice.receive_json()
            bob_message = bob.receive_json()

    expected = {
        "type": "message",
        "room_id": "python",
        "username": "alice",
        "text": "hello",
    }
    assert alice_message == expected
    assert bob_message == expected


def test_clients_in_different_rooms_do_not_receive_foreign_messages(client):
    with client.websocket_connect("/ws/rooms/python?username=alice") as python_socket:
        python_socket.receive_json()
        with client.websocket_connect("/ws/rooms/java?username=bob") as java_socket:
            java_socket.receive_json()

            python_socket.send_json({"type": "message", "text": "python only"})
            response = python_socket.receive_json()

            assert response["room_id"] == "python"
            assert client.get("/rooms/java/users").json() == {
                "room_id": "java",
                "users": ["bob"],
            }


def test_long_message_returns_error(client):
    with client.websocket_connect("/ws/rooms/python?username=alice") as websocket:
        websocket.receive_json()
        websocket.send_json({"type": "message", "text": "x" * 301})
        response = websocket.receive_json()

    assert response == {"type": "error", "detail": "Message is too long"}


def test_disconnected_user_removed_from_room(client):
    with client.websocket_connect("/ws/rooms/python?username=alice") as websocket:
        websocket.receive_json()
        assert client.get("/rooms/python/users").json() == {
            "room_id": "python",
            "users": ["alice"],
        }

    assert client.get("/rooms/python/users").json() == {
        "room_id": "python",
        "users": [],
    }


def test_blank_username_closes_connection(client):
    with pytest.raises(WebSocketDisconnect) as exc_info:
        with client.websocket_connect("/ws/rooms/python?username=   "):
            pass

    assert exc_info.value.code == 1008
