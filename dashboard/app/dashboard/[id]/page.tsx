"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { useParams, useRouter } from "next/navigation"
import { init, close, getDevice } from "@/lib/ws"
import { Button } from "@/components/ui/button"
import { SpaceBackground } from "@/components/space-background"

interface Report {
  id: string
  timestamp?: string
  reason?: string
  message?: string
  screen_shot_id?: string
  data?: any
}

interface DeviceData {
  id: string
  name?: string
  access_code?: string
  is_online?: boolean
  last_online?: string
  reports?: Report[]
}

export default function DevicePage() {
  const params = useParams() as { id?: string }
  const router = useRouter()
  const deviceId = params?.id ?? ""

  const [device, setDevice] = useState<DeviceData | null>(null)
  const [reports, setReports] = useState<Report[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    let mounted = true
    setLoading(true)
    init()
      .then(() => getDevice(deviceId))
      .then((res) => {
        if (!mounted) return
        if (res?.status === "success" && res.data) {
          setDevice(res.data)
          setReports(Array.isArray(res.data.reports) ? res.data.reports : [])
        } else {
          // could not fetch; navigate back
          router.back()
        }
      })
      .catch(() => {
        router.back()
      })
      .finally(() => setLoading(false))

    return () => {
      mounted = false
      close()
    }
  }, [deviceId])

  function severityOf(r: Report) {
    if (!r) return "normal"
    if (r.data && typeof r.data === "object") {
      if (r.data.severity) return String(r.data.severity)
    }
    if (r.reason && /critical/i.test(r.reason)) return "critical"
    return "normal"
  }

  return (
    <div className="min-h-screen relative bg-[#0a0e1a]">
      <SpaceBackground />
      <div className="container mx-auto px-4 py-6 relative z-10">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="font-mono text-accent text-lg">{">"} DEVICE_DETAILS</h2>
            <div className="font-mono text-sm text-muted-foreground">ID: {deviceId}</div>
          </div>
          <div className="flex gap-2">
            <Link href="/dashboard">
              <Button className="font-mono text-sm">◀ BACK</Button>
            </Link>
          </div>
        </div>

        <div className="border border-[#2a3f5f] rounded-lg p-4 mb-6 bg-[#0f1419]/80">
          <div className="grid grid-cols-3 gap-4">
            <div>
              <div className="font-mono text-sm text-muted-foreground">NAME</div>
              <div className="font-mono text-sm text-foreground">{device?.name ?? "-"}</div>
            </div>
            <div>
              <div className="font-mono text-sm text-muted-foreground">STATUS</div>
              <div className={`font-mono text-sm ${device?.is_online ? "text-green-500" : "text-gray-500"}`}>{device?.is_online ? "online" : "offline"}</div>
            </div>
            <div>
              <div className="font-mono text-sm text-muted-foreground">LAST ONLINE</div>
              <div className="font-mono text-sm text-foreground">{device?.last_online ? new Date(device.last_online).toLocaleString() : "-"}</div>
            </div>
          </div>
        </div>

        <div className="border border-[#2a3f5f] rounded-t-lg bg-[#0f1419]/90 font-mono text-sm p-3">REPORTS</div>
        <div className="overflow-x-auto">
          <div className="min-w-[800px]">
            <div className="grid grid-cols-5 gap-4 p-3 border border-[#2a3f5f] bg-[#0f1419]/80 text-sm text-accent">
              <div>TIMESTAMP</div>
              <div>REASON</div>
              <div>MESSAGE</div>
              <div>SEVERITY</div>
              <div>SCREENSHOT</div>
            </div>

            <div className="space-y-2 mt-2">
              {loading ? (
                <div className="p-4 font-mono text-muted-foreground">Loading...</div>
              ) : reports.length === 0 ? (
                <div className="p-4 font-mono text-muted-foreground">No reports available for this device.</div>
              ) : (
                reports.map((r) => (
                  <div
                    key={r.id}
                    className="grid grid-cols-5 gap-4 p-3 border border-[#2a3f5f] bg-[#0f1419]/80 rounded-lg items-center"
                  >
                    <div className="font-mono text-sm text-accent break-all">{r.timestamp ? new Date(r.timestamp).toLocaleString() : "-"}</div>
                    <div className="font-mono text-sm text-foreground truncate" title={r.reason}>{r.reason || "-"}</div>
                    <div className="font-mono text-sm text-foreground truncate" title={r.message}>{r.message || "-"}</div>
                    <div>
                      {severityOf(r) === "critical" ? (
                        <span className="font-mono text-sm text-destructive font-bold">CRITICAL</span>
                      ) : (
                        <span className="font-mono text-sm text-muted-foreground">normal</span>
                      )}
                    </div>
                    <div className="font-mono text-sm text-accent break-all">{r.screen_shot_id || "-"}</div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
