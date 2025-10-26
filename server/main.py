import asyncio, json, os, logging
import websockets
from websockets.asyncio.server import serve

from db_init import db_connect
from device import Devices
from pipeline import get_pipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Store connections for broadcasting
connected_professors = {}  # Maps professor_id to WebSocket connection
    

async def broadcast_to_professors(flagged_report: dict):
    """Broadcast flagged report to all connected professor dashboards."""
    if not connected_professors:
        return
    
    message = {
        "type": "FlaggedReportAlert",
        "data": flagged_report,
    }
    
    disconnected = []
    for prof_id, ws in connected_professors.items():
        try:
            await ws.send(json.dumps(message))
        except Exception as e:
            logger.error(f"Failed to broadcast to professor {prof_id}: {e}")
            disconnected.append(prof_id)
    
    # Clean up disconnected professors
    for prof_id in disconnected:
        del connected_professors[prof_id]


async def handler(ws, path=None):
    """Handle both student clients and professor dashboards."""
    db = db_connect()
    device_manager = Devices(db)
    pipeline = get_pipeline()
    response = {}
    professor_id = None
    student_token = None

    logger.info(f"New connection from {ws.remote_address}")

    try:
        async for raw in ws:
            try:
                message = json.loads(raw)
                method = message.get("method")
                msg_type = message.get("type")  # For professor dashboard messages
                data = message.get("data", {})

                # ========== PROFESSOR DASHBOARD MESSAGES ==========
                if msg_type == "RegisterProfessor":
                    professor_id = data.get("professor_id")
                    connected_professors[professor_id] = ws
                    response = {"type": "RegistrationConfirmed", "professor_id": professor_id}
                    logger.info(f"Professor {professor_id} connected")

                elif msg_type == "AcknowledgeReport":
                    report_id = data.get("report_id")
                    action = data.get("action")  # "flag_false_positive", "request_verification", etc
                    notes = data.get("notes", "")
                    # TODO: Store professor action in database
                    response = {"type": "ActionAcknowledged", "report_id": report_id}
                    logger.info(f"Professor {professor_id} took action: {action} on {report_id}")

                # ========== STUDENT CLIENT MESSAGES ==========
                elif method == "GetAllDevices":
                    devices = device_manager.get_all_devices()
                    response = {"status": "success", "data": devices}

                elif method == "GetDevice":
                    device_id = data.get("device_id")
                    device_info = device_manager.get_device(device_id)
                    if device_info:
                        response = {"status": "success", "data": device_info}
                    else:
                        response = {"status": "error", "message": "Device not found"}

                elif method == "CreateDevice":
                    name = data.get("name")
                    description = data.get("description")
                    created = device_manager.create_device(name, description)
                    response = {"status": "success", "data": created}

                elif method == "RemoveDevice":
                    device_id = data.get("device_id")
                    success = device_manager.remove_device(device_id)
                    response = {
                        "status": "success"
                        if success
                        else {"status": "error", "message": "Failed to remove device"}
                    }

                elif method == "EditDevice":
                    device_id = data.get("device_id")
                    name = data.get("name")
                    description = data.get("description")
                    success = device_manager.edit_device(device_id, name, description)
                    response = {
                        "status": "success"
                        if success
                        else {"status": "error", "message": "Failed to edit device"}
                    }

                elif method == "Authenticate":
                    access_code = data.get("access_code")
                    token = device_manager.authenticate(ws, access_code)
                    if token:
                        student_token = token
                        response = {"status": "success", "data": {"token": token}}
                        logger.info(f"Student authenticated with token: {token}")
                    else:
                        response = {"status": "error", "message": "Authentication failed"}

                elif method == "Package":
                    # MAIN PIPELINE: Process student activity package
                    token = data.get("token")
                    if token and device_manager.devices.get(token):
                        activity_package = data.get("data")
                        logger.debug(f"Received activity package from student {activity_package.get('student_id')}")

                        # Process through pipeline
                        flagged_report = await pipeline.process_package(
                            activity_package,
                            professor_broadcast_callback=broadcast_to_professors,
                        )

                        if flagged_report:
                            response = {
                                "status": "success",
                                "data": {
                                    "message": "Package processed and flagged",
                                    "flag_id": flagged_report["id"],
                                },
                            }
                            logger.warning(
                                f"FLAGGED: Student {activity_package.get('student_id')} - "
                                f"{flagged_report['gemini_analysis']['suspected_activity']}"
                            )
                        else:
                            response = {
                                "status": "success",
                                "data": {"message": "Package processed (clean)"},
                            }
                    else:
                        response = {"status": "error", "message": "Invalid token"}

                else:
                    response = {"status": "error", "message": f"Unknown method: {method}"}

            except json.JSONDecodeError:
                response = {"status": "error", "message": "Invalid JSON"}
            except Exception as exc:
                logger.exception(f"Error processing message: {exc}")
                response = {"status": "error", "message": f"Server error: {str(exc)}"}

            await ws.send(json.dumps(response))

    except websockets.exceptions.ConnectionClosed:
        logger.info(f"Connection closed from {ws.remote_address}")
    finally:
        # Clean up connections
        if professor_id and professor_id in connected_professors:
            del connected_professors[professor_id]
            logger.info(f"Professor {professor_id} disconnected")

        if student_token:
            device_manager.forget(student_token)
            logger.info(f"Student session {student_token} ended")
        
        tokens = [t for t, info in device_manager.devices.items() if info.get("session") is ws]
        for t in tokens:
            device_manager.forget(t)



async def main():
    async with websockets.serve(handler, "localhost", 8765):
        print("WebSocket server on ws://localhost:8765")
        await asyncio.Future()  # run forever

asyncio.run(main())