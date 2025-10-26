// FlagReportsPanel Component for Dashboard
// Displays automatically-generated flag reports in the Next.js dashboard.
// Shows real-time alerts when suspicious activity is detected.

'use client'

import { useEffect, useState } from 'react'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { AlertCircle, CheckCircle, Clock, Download, ExternalLink } from 'lucide-react'

interface FlagNotification {
  analysis_id: string
  student_id: string
  severity: string
  title: string
  violation_count: number
  violations_summary: Array<{
    type: string
    severity: string
    description: string
  }>
  report_links: {
    html: string
    json: string
    markdown: string
  }
  recommended_actions: Array<{
    action: string
    priority: string
    description: string
  }>
  timestamp: string
}

interface AnalysisStatus {
  analysis_id: string
  status: 'analyzing' | 'generating_reports' | 'complete'
  message: string
  timestamp: string
}

interface SafeNotification {
  analysis_id: string
  student_id: string
  message: string
  timestamp: string
}

export default function FlagReportsPanel() {
  const [notifications, setNotifications] = useState<FlagNotification[]>([])
  const [statusUpdates, setStatusUpdates] = useState<AnalysisStatus[]>([])
  const [safeActivities, setSafeActivities] = useState<SafeNotification[]>([])
  const [expandedReport, setExpandedReport] = useState<string | null>(null)
  const [filter, setFilter] = useState<'all' | 'flags' | 'safe'>('all')

  useEffect(() => {
    // Connect to WebSocket
    const ws = new WebSocket('ws://localhost:8765')

    ws.onopen = () => {
      console.log('✅ Connected to analysis server')
    }

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data)

        if (message.type === 'FlagNotification') {
          // Add flag notification
          setNotifications((prev) => [message as FlagNotification, ...prev])
          // Play sound (optional)
          playAlertSound()
        } else if (message.type === 'AnalysisStatus') {
          // Add status update
          setStatusUpdates((prev) => [message as AnalysisStatus, ...prev])
        } else if (message.type === 'SafeNotification') {
          // Add safe activity
          setSafeActivities((prev) => [message as SafeNotification, ...prev])
        }
      } catch (error) {
        console.error('Error processing message:', error)
      }
    }

    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
    }

    return () => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.close()
      }
    }
  }, [])

  const playAlertSound = () => {
    // Create a simple beep sound
    const audioContext = new (window.AudioContext ||
      (window as any).webkitAudioContext)()
    const oscillator = audioContext.createOscillator()
    const gain = audioContext.createGain()

    oscillator.connect(gain)
    gain.connect(audioContext.destination)

    oscillator.frequency.value = 800
    oscillator.type = 'sine'

    gain.gain.setValueAtTime(0.3, audioContext.currentTime)
    gain.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5)

    oscillator.start(audioContext.currentTime)
    oscillator.stop(audioContext.currentTime + 0.5)
  }

  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'critical':
        return 'bg-red-100 text-red-800'
      case 'high':
        return 'bg-orange-100 text-orange-800'
      case 'medium':
        return 'bg-yellow-100 text-yellow-800'
      default:
        return 'bg-blue-100 text-blue-800'
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority.toLowerCase()) {
      case 'high':
        return 'bg-red-50 border-red-200'
      case 'medium':
        return 'bg-yellow-50 border-yellow-200'
      default:
        return 'bg-blue-50 border-blue-200'
    }
  }

  const downloadReport = (reportUrl: string, format: string) => {
    const link = document.createElement('a')
    link.href = reportUrl
    link.download = `report-${format}`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  const openReportInNewTab = (reportUrl: string) => {
    window.open(reportUrl, '_blank')
  }

  const displayedNotifications =
    filter === 'all'
      ? [...notifications, ...statusUpdates, ...safeActivities]
      : filter === 'flags'
      ? notifications
      : safeActivities

  return (
    <div className="w-full max-w-4xl mx-auto p-6 space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold flex items-center gap-2">
          <AlertCircle className="w-6 h-6 text-red-500" />
          Flag Reports & Analysis
        </h2>
        <div className="text-sm text-gray-500">
          {notifications.length} flags | {safeActivities.length} safe
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex gap-2 mb-4">
        {(['all', 'flags', 'safe'] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setFilter(tab)}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              filter === tab
                ? 'bg-blue-500 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            {tab === 'all'
              ? '📊 All'
              : tab === 'flags'
              ? '🚨 Flags'
              : '✅ Safe'}
          </button>
        ))}
      </div>

      {/* Notifications */}
      <div className="space-y-3">
        {displayedNotifications.length === 0 ? (
          <Card className="p-6 text-center text-gray-500">
            <Clock className="w-8 h-8 mx-auto mb-2 opacity-50" />
            <p>Waiting for analysis results...</p>
          </Card>
        ) : (
          displayedNotifications.map((notification: any, index: number) => {
            // Handle different notification types
            if ('violation_count' in notification) {
              // FlagNotification
              return (
                <Card
                  key={notification.analysis_id}
                  className="p-4 border-2 border-red-300 bg-red-50 cursor-pointer hover:shadow-md transition-shadow"
                  onClick={() =>
                    setExpandedReport(
                      expandedReport === notification.analysis_id
                        ? null
                        : notification.analysis_id
                    )
                  }
                >
                  {/* Header */}
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-start gap-3 flex-1">
                      <AlertCircle className="w-6 h-6 text-red-600 shrink-0 mt-0.5" />
                      <div className="flex-1">
                        <p className="font-bold text-red-900">
                          {notification.title}
                        </p>
                        <p className="text-sm text-gray-600">
                          ID: {notification.analysis_id}
                        </p>
                      </div>
                    </div>
                    <Badge className={getSeverityColor(notification.severity)}>
                      {notification.severity}
                    </Badge>
                  </div>

                  {/* Quick Stats */}
                  <div className="grid grid-cols-3 gap-2 mb-3 text-sm">
                    <div className="bg-white p-2 rounded">
                      <p className="text-gray-600">Violations</p>
                      <p className="font-bold text-lg">
                        {notification.violation_count}
                      </p>
                    </div>
                    <div className="bg-white p-2 rounded">
                      <p className="text-gray-600">Student</p>
                      <p className="font-bold">{notification.student_id}</p>
                    </div>
                    <div className="bg-white p-2 rounded">
                      <p className="text-gray-600">Time</p>
                      <p className="font-bold text-xs">
                        {new Date(notification.timestamp).toLocaleTimeString()}
                      </p>
                    </div>
                  </div>

                  {/* Violations Summary */}
                  <div className="mb-3 space-y-2">
                    {notification.violations_summary.map((v: any, i: number) => (
                      <div
                        key={i}
                        className="text-sm bg-white p-2 rounded border-l-4 border-red-400"
                      >
                        <p className="font-semibold">
                          {v.type.replace(/_/g, ' ')}
                        </p>
                        <p className="text-gray-600 text-xs">{v.description}</p>
                      </div>
                    ))}
                  </div>

                  {/* Expanded Details */}
                  {expandedReport === notification.analysis_id && (
                    <div className="mt-4 pt-4 border-t-2 border-red-200 space-y-3">
                      {/* Recommended Actions */}
                      <div>
                        <p className="font-semibold mb-2 text-gray-800">
                          Recommended Actions:
                        </p>
                        <div className="space-y-2">
                          {notification.recommended_actions.map((action: any, i: number) => (
                            <div
                              key={i}
                              className={`p-3 rounded border-l-4 ${getPriorityColor(
                                action.priority
                              )}`}
                            >
                              <p className="font-semibold">{action.action}</p>
                              <p className="text-sm text-gray-700">
                                {action.description}
                              </p>
                              <Badge className="mt-1 text-xs">
                                {action.priority} Priority
                              </Badge>
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* Report Links */}
                      <div>
                        <p className="font-semibold mb-2 text-gray-800">
                          Generated Reports:
                        </p>
                        <div className="grid grid-cols-3 gap-2">
                          {[
                            {
                              format: 'HTML',
                              url: notification.report_links.html,
                              icon: '📄',
                            },
                            {
                              format: 'JSON',
                              url: notification.report_links.json,
                              icon: '📋',
                            },
                            {
                              format: 'Markdown',
                              url: notification.report_links.markdown,
                              icon: '📝',
                            },
                          ].map((report) => (
                            <div
                              key={report.format}
                              className="flex gap-1 items-stretch"
                            >
                              <button
                                onClick={() =>
                                  openReportInNewTab(report.url)
                                }
                                className="flex-1 flex items-center justify-center gap-1 bg-blue-500 hover:bg-blue-600 text-white text-xs font-bold py-2 px-2 rounded"
                              >
                                <ExternalLink className="w-3 h-3" />
                                {report.format}
                              </button>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  )}
                </Card>
              )
            } else if ('status' in notification) {
              // AnalysisStatus
              return (
                <Card key={notification.analysis_id} className="p-4 bg-blue-50">
                  <div className="flex items-center gap-3">
                    <Clock className="w-5 h-5 text-blue-500 animate-spin" />
                    <div className="flex-1">
                      <p className="font-semibold text-blue-900">
                        {notification.message}
                      </p>
                      <p className="text-xs text-gray-600">
                        {notification.status}
                      </p>
                    </div>
                    <Badge className="bg-blue-100 text-blue-800">
                      {notification.status}
                    </Badge>
                  </div>
                </Card>
              )
            } else {
              // SafeNotification
              return (
                <Card key={notification.analysis_id} className="p-4 bg-green-50">
                  <div className="flex items-start gap-3">
                    <CheckCircle className="w-6 h-6 text-green-600 shrink-0 mt-0.5" />
                    <div className="flex-1">
                      <p className="font-semibold text-green-900">
                        Activity Marked as Safe
                      </p>
                      <p className="text-sm text-gray-600">
                        {notification.student_id}
                      </p>
                      <p className="text-xs text-gray-500 mt-1">
                        {notification.message}
                      </p>
                    </div>
                    <Badge className="bg-green-100 text-green-800">Safe</Badge>
                  </div>
                </Card>
              )
            }
          })
        )}
      </div>

      {/* Legend */}
      <Card className="p-4 bg-gray-50">
        <p className="text-sm font-semibold text-gray-700 mb-2">Legend:</p>
        <div className="grid grid-cols-2 gap-2 text-xs text-gray-600">
          <div>🚨 = Suspicious Activity Flagged</div>
          <div>✅ = Activity Marked as Safe</div>
          <div>⏳ = Analysis in Progress</div>
          <div>📄 = Report Available</div>
        </div>
      </Card>
    </div>
  )
}
