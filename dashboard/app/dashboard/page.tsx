"use client"

import { useState } from "react"
import { SpaceBackground } from "@/components/space-background"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import { Plus, Settings, Trash2, LayoutGrid, LayoutList } from "lucide-react"

interface Device {
  id: string
  code: string
  name: string
  description: string
  status: "online" | "offline"
  lastOnline?: Date
}

export default function DashboardPage() {
  const [devices, setDevices] = useState<Device[]>([])
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false)
  const [deviceCode, setDeviceCode] = useState("")
  const [deviceName, setDeviceName] = useState("")
  const [isSettingsDialogOpen, setIsSettingsDialogOpen] = useState(false)
  const [editingDevice, setEditingDevice] = useState<Device | null>(null)
  const [editName, setEditName] = useState("")
  const [editDescription, setEditDescription] = useState("")
  const [layout, setLayout] = useState<"grid" | "list">("grid")

  const handleAddDevice = () => {
    if (!deviceCode.trim() || !deviceName.trim()) return

    const status = Math.random() > 0.5 ? "online" : "offline"
    const lastOnline =
      status === "offline"
        ? new Date(Date.now() - Math.floor(Math.random() * 7 * 24 * 60 * 60 * 1000)) // Random date within last 7 days
        : undefined

    const newDevice: Device = {
      id: `DEV-${Math.random().toString(36).substr(2, 9).toUpperCase()}`,
      code: deviceCode,
      name: deviceName,
      description: "",
      status,
      lastOnline,
    }

    setDevices([...devices, newDevice])
    setDeviceCode("")
    setDeviceName("")
    setIsAddDialogOpen(false)
  }

  const formatLastOnline = (date: Date) => {
    return date.toLocaleString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    })
  }

  const handleDeleteDevice = (id: string) => {
    setDevices(devices.filter((device) => device.id !== id))
  }

  const handleOpenSettings = (device: Device) => {
    setEditingDevice(device)
    setEditName(device.name)
    setEditDescription(device.description)
    setIsSettingsDialogOpen(true)
  }

  const handleConfirmSettings = () => {
    if (!editingDevice) return

    setDevices(
      devices.map((device) =>
        device.id === editingDevice.id ? { ...device, name: editName, description: editDescription } : device,
      ),
    )
    setIsSettingsDialogOpen(false)
    setEditingDevice(null)
    setEditName("")
    setEditDescription("")
  }

  const StatusDisplay = ({ device }: { device: Device }) => (
    <div className="flex items-center gap-2">
      <div
        className={`w-2 h-2 rounded-full ${device.status === "online" ? "bg-green-500 animate-pulse" : "bg-gray-500"}`}
      />
      {device.status === "offline" && device.lastOnline ? (
        <TooltipProvider delayDuration={0}>
          <Tooltip>
            <TooltipTrigger asChild>
              <span className="font-mono text-xs text-gray-500 cursor-help">{device.status.toUpperCase()}</span>
            </TooltipTrigger>
            <TooltipContent side="bottom" className="bg-[#0f1419] border-[#2a3f5f] font-mono text-xs text-accent">
              <p>Last online: {formatLastOnline(device.lastOnline)}</p>
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
      ) : (
        <span className={`font-mono text-xs ${device.status === "online" ? "text-green-500" : "text-gray-500"}`}>
          {device.status.toUpperCase()}
        </span>
      )}
    </div>
  )

  return (
    <div className="min-h-screen relative bg-[#0a0e1a]">
      <SpaceBackground />

      <div className="relative z-10">
        {/* Terminal Header */}
        <div className="border-b border-[#2a3f5f] bg-[#0f1419]/90 backdrop-blur">
          <div className="container mx-auto px-4 py-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-3 h-3 rounded-full bg-destructive animate-pulse" />
              <div className="w-3 h-3 rounded-full bg-accent" />
              <div className="w-3 h-3 rounded-full bg-primary" />
              <span className="ml-4 font-mono text-accent text-sm tracking-wider">
                {">"} SPACE_COWBOY_TERMINAL v2.1.0
              </span>
            </div>

            <div className="flex items-center gap-2">
              <div className="flex border border-[#2a3f5f] rounded-md overflow-hidden">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setLayout("grid")}
                  className={`font-mono text-xs rounded-none ${
                    layout === "grid" ? "bg-accent text-accent-foreground" : "text-muted-foreground hover:text-accent"
                  }`}
                >
                  <LayoutGrid className="w-4 h-4" />
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setLayout("list")}
                  className={`font-mono text-xs rounded-none ${
                    layout === "list" ? "bg-accent text-accent-foreground" : "text-muted-foreground hover:text-accent"
                  }`}
                >
                  <LayoutList className="w-4 h-4" />
                </Button>
              </div>

              <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
                <DialogTrigger asChild>
                  <Button className="font-mono bg-accent hover:bg-accent/80 text-accent-foreground">
                    <Plus className="w-4 h-4 mr-2" />
                    Add New Device
                  </Button>
                </DialogTrigger>
                <DialogContent className="bg-[#0f1419] border-[#2a3f5f] font-mono">
                  <DialogHeader>
                    <DialogTitle className="text-accent font-mono">{">"} ADD_NEW_DEVICE</DialogTitle>
                    <DialogDescription className="text-muted-foreground font-mono text-xs">
                      Enter device credentials to establish connection
                    </DialogDescription>
                  </DialogHeader>
                  <div className="space-y-4 mt-4">
                    <div className="space-y-2">
                      <Label htmlFor="device-code" className="text-accent font-mono text-xs">
                        DEVICE_CODE:
                      </Label>
                      <Input
                        id="device-code"
                        value={deviceCode}
                        onChange={(e) => setDeviceCode(e.target.value)}
                        className="font-mono bg-[#1a1f2e] border-[#2a3f5f] text-foreground focus:border-accent"
                        placeholder="Enter device code..."
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="device-name" className="text-accent font-mono text-xs">
                        DEVICE_NAME:
                      </Label>
                      <Input
                        id="device-name"
                        value={deviceName}
                        onChange={(e) => setDeviceName(e.target.value)}
                        className="font-mono bg-[#1a1f2e] border-[#2a3f5f] text-foreground focus:border-accent"
                        placeholder="Enter device name..."
                      />
                    </div>
                    <Button
                      onClick={handleAddDevice}
                      className="w-full font-mono bg-accent hover:bg-accent/80 text-accent-foreground"
                    >
                      {">"} CONNECT_DEVICE
                    </Button>
                  </div>
                </DialogContent>
              </Dialog>
            </div>
          </div>
        </div>

        <Dialog open={isSettingsDialogOpen} onOpenChange={setIsSettingsDialogOpen}>
          <DialogContent className="bg-[#0f1419] border-[#2a3f5f] font-mono">
            <DialogHeader>
              <DialogTitle className="text-accent font-mono">{">"} DEVICE_SETTINGS</DialogTitle>
              <DialogDescription className="text-muted-foreground font-mono text-xs">
                Edit device name and description
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4 mt-4">
              <div className="space-y-2">
                <Label htmlFor="edit-name" className="text-accent font-mono text-xs">
                  DEVICE_NAME:
                </Label>
                <Input
                  id="edit-name"
                  value={editName}
                  onChange={(e) => setEditName(e.target.value)}
                  className="font-mono bg-[#1a1f2e] border-[#2a3f5f] text-foreground focus:border-accent"
                  placeholder="Enter device name..."
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="edit-description" className="text-accent font-mono text-xs">
                  DESCRIPTION:
                </Label>
                <Textarea
                  id="edit-description"
                  value={editDescription}
                  onChange={(e) => setEditDescription(e.target.value)}
                  className="font-mono text-xs bg-[#1a1f2e] border-[#2a3f5f] text-foreground min-h-[100px] resize-none focus:border-accent"
                  placeholder="Add device details..."
                />
              </div>
              <Button
                onClick={handleConfirmSettings}
                className="w-full font-mono bg-accent hover:bg-accent/80 text-accent-foreground"
              >
                {">"} CONFIRM_CHANGES
              </Button>
            </div>
          </DialogContent>
        </Dialog>

        {/* Main Terminal Content */}
        <div className="container mx-auto px-4 py-8">
          {devices.length === 0 ? (
            <div className="flex items-center justify-center min-h-[60vh]">
              <div className="text-center space-y-4">
                <div className="font-mono text-muted-foreground text-lg animate-pulse">{">"} NO_DEVICES_CONNECTED</div>
                <div className="font-mono text-muted-foreground/60 text-sm">
                  [!] Use the button above to add a new device
                </div>
              </div>
            </div>
          ) : layout === "grid" ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {devices.map((device) => (
                <div
                  key={device.id}
                  className="border border-[#2a3f5f] bg-[#0f1419]/80 backdrop-blur rounded-lg p-4 space-y-3 hover:border-accent/50 transition-colors"
                >
                  {/* Row 1: Status */}
                  <div className="flex items-center justify-between pb-3 border-b border-[#2a3f5f]/50">
                    <span className="font-mono text-xs text-muted-foreground">STATUS:</span>
                    <StatusDisplay device={device} />
                  </div>

                  {/* Row 2: ID */}
                  <div className="space-y-1">
                    <span className="font-mono text-xs text-muted-foreground">ID:</span>
                    <div className="font-mono text-sm text-accent break-all">{device.id}</div>
                  </div>

                  {/* Row 3: Name */}
                  <div className="space-y-1">
                    <span className="font-mono text-xs text-muted-foreground">NAME:</span>
                    <div className="font-mono text-sm text-foreground">{device.name}</div>
                  </div>

                  {/* Row 4: Description */}
                  <div className="space-y-1">
                    <span className="font-mono text-xs text-muted-foreground">DESCRIPTION:</span>
                    <div className="font-mono text-xs text-foreground/80 min-h-[60px] p-2 bg-[#1a1f2e] border border-[#2a3f5f] rounded-md">
                      {device.description || "No description set"}
                    </div>
                  </div>

                  {/* Row 5 & 6: Settings and Delete Buttons */}
                  <div className="flex gap-2 pt-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleOpenSettings(device)}
                      className="flex-1 font-mono text-xs border-[#2a3f5f] hover:bg-[#2a3f5f] hover:text-accent bg-transparent"
                    >
                      <Settings className="w-3 h-3 mr-1" />
                      SETTINGS
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleDeleteDevice(device.id)}
                      className="flex-1 font-mono text-xs border-destructive/50 text-destructive hover:bg-destructive hover:text-destructive-foreground"
                    >
                      <Trash2 className="w-3 h-3 mr-1" />
                      DELETE
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="overflow-x-auto">
              <div className="min-w-[800px]">
                {/* Table Header */}
                <div className="grid grid-cols-6 gap-4 p-4 border border-[#2a3f5f] bg-[#0f1419]/90 backdrop-blur rounded-t-lg font-mono text-xs text-accent">
                  <div>STATUS</div>
                  <div>ID</div>
                  <div>NAME</div>
                  <div>DESCRIPTION</div>
                  <div>SETTINGS</div>
                  <div>DELETE</div>
                </div>

                {/* Table Rows */}
                <div className="space-y-2 mt-2">
                  {devices.map((device) => (
                    <div
                      key={device.id}
                      className="grid grid-cols-6 gap-4 p-4 border border-[#2a3f5f] bg-[#0f1419]/80 backdrop-blur rounded-lg hover:border-accent/50 transition-colors items-center"
                    >
                      {/* Status Column */}
                      <StatusDisplay device={device} />

                      {/* ID Column */}
                      <div className="font-mono text-xs text-accent break-all">{device.id}</div>

                      {/* Name Column */}
                      <div className="font-mono text-xs text-foreground">{device.name}</div>

                      {/* Description Column */}
                      <div className="font-mono text-xs text-foreground/80 truncate" title={device.description}>
                        {device.description || "No description"}
                      </div>

                      {/* Settings Column */}
                      <div>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleOpenSettings(device)}
                          className="w-full font-mono text-xs border-[#2a3f5f] hover:bg-[#2a3f5f] hover:text-accent bg-transparent"
                        >
                          <Settings className="w-3 h-3 mr-1" />
                          EDIT
                        </Button>
                      </div>

                      {/* Delete Column */}
                      <div>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleDeleteDevice(device.id)}
                          className="w-full font-mono text-xs border-destructive/50 text-destructive hover:bg-destructive hover:text-destructive-foreground"
                        >
                          <Trash2 className="w-3 h-3 mr-1" />
                          DELETE
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Terminal Footer */}
        <div className="fixed bottom-0 left-0 right-0 border-t border-[#2a3f5f] bg-[#0f1419]/90 backdrop-blur">
          <div className="container mx-auto px-4 py-2">
            <div className="font-mono text-xs text-muted-foreground flex items-center gap-4">
              <span>
                {">"} DEVICES_ACTIVE: {devices.filter((d) => d.status === "online").length}
              </span>
              <span>|</span>
              <span>TOTAL: {devices.length}</span>
              <span>|</span>
              <span className="text-accent">SYSTEM_READY</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
