import asyncio, json
import websockets
from websockets.asyncio.server import serve

from db_init import db_connect
from device import Devices
from analyze import analyze
from auto_integration import handle_package_auto
    

async def handler(ws):
    db = db_connect()
    device_manager = Devices(db)
    response = {}

    print(device_manager.devices)

    try:
        async for raw in ws:
            try:
                message = json.loads(raw)
                method = message.get("method")
                data = message.get("data", {})

                # handle incoming methods in a single dispatch
                match method:
                    case "GetAllDevices":
                        devices = device_manager.get_all_devices()
                        response = {"status": "success", "data": devices}

                    case "GetDevice":
                        device_id = data.get("device_id")
                        device_info = device_manager.get_device(device_id)
                        if device_info:
                            response = {"status": "success", "data": device_info}
                        else:
                            response = {"status": "error", "message": "Device not found"}

                    case "CreateDevice":
                        name = data.get("name")
                        created = device_manager.create_device(name)
                        # created is a dict {id, access_code}
                        response = {"status": "success", "data": created}

                    case "RemoveDevice":
                        device_id = data.get("device_id")
                        success = device_manager.remove_device(device_id)
                        if success:
                            response = {"status": "success"}
                        else:
                            response = {"status": "error", "message": "Failed to remove device"}

                    case "EditDevice":
                        device_id = data.get("device_id")
                        name = data.get("name")
                        success = device_manager.edit_device(device_id, name)
                        if success:
                            response = {"status": "success"}
                        else:
                            response = {"status": "error", "message": "Failed to edit device"}

                    case "Authenticate":
                        access_code = data.get("access_code")
                        print("Authenticating with access code:", access_code)
                        token = device_manager.authenticate(ws, access_code)
                        if token:
                            response = {"status": "success", "data": {"token": token}}
                        else:
                            response = {"status": "error", "message": "Authentication failed"}

                    case "Package":
                        token = data.get("token")
                        print("Received package with token:", token)
                        if token in device_manager.devices:
                            analyzed = await analyze(data)
                            saved = create_report_from_analysis(device_manager, token, analyzed, data)
                            response = {"status": "success"}

                        else:
                            response = {"status": "error", "message": "Invalid token"}

                    case _:
                        response = {"status": "error", "message": "Unknown method"}

            except json.JSONDecodeError:
                response = {"status": "error", "message": "Invalid JSON"}
            except Exception as exc:
                response = {"status": "error", "message": f"Server error: {exc}"}

            await ws.send(json.dumps(response))
    finally:
        # Clean up session when WebSocket connection closes
        tokens = [t for t, info in device_manager.devices.items() if info.get("session") is ws]
        for t in tokens:
            device_manager.forget(t)



async def main():
    async with websockets.serve(handler, "localhost", 8765):
        print("WebSocket server on ws://localhost:8765")
        await asyncio.Future()  # run forever

asyncio.run(main())