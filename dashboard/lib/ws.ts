let ws: WebSocket | null = null

export function init(url = "ws://localhost:8765") {
  return new Promise<void>((resolve, reject) => {
    if (ws && ws.readyState === WebSocket.OPEN) return resolve()
    ws = new WebSocket(url)
    ws.onopen = () => resolve()
    ws.onerror = (e) => reject(e)
  })
}

export function close() {
  if (ws) {
    try {
      ws.close()
    } catch (e) {
      // ignore
    }
    ws = null
  }
}

export const sendRequest = (payload: any, timeout = 5000): Promise<any> => {
  return new Promise((resolve, reject) => {
    if (!ws || ws.readyState !== WebSocket.OPEN) return reject(new Error("WebSocket not connected"))

    const onMessage = (ev: MessageEvent) => {
      try {
        const data = JSON.parse(ev.data)
        ws?.removeEventListener("message", onMessage)
        clearTimeout(timer)
        resolve(data)
      } catch (err) {
        ws?.removeEventListener("message", onMessage)
        clearTimeout(timer)
        reject(err)
      }
    }

    const timer = setTimeout(() => {
      ws?.removeEventListener("message", onMessage)
      reject(new Error("WebSocket request timed out"))
    }, timeout)

    ws.addEventListener("message", onMessage)
    ws.send(JSON.stringify(payload))
  })
}

export async function getAllDevices() {
  return await sendRequest({ method: "GetAllDevices" })
}

export async function createDevice(name: string) {
  return await sendRequest({ method: "CreateDevice", data: { name } })
}

export async function editDevice(device_id: string, name: string) {
  return await sendRequest({ method: "EditDevice", data: { device_id, name } })
}

export async function removeDevice(device_id: string) {
  return await sendRequest({ method: "RemoveDevice", data: { device_id } })
}
