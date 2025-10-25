import { redirect } from "next/navigation"
import { SpaceCowboyIcon } from "@/components/space-cowboy-icon"
import { SpaceBackground } from "@/components/space-background"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Shield, Eye, AlertTriangle, CheckCircle2, Users, Video } from "lucide-react"

export default function Home() {
  redirect("/dashboard")

  return (
    <div className="min-h-screen relative">
      <SpaceBackground />

      <div className="relative z-10">
        {/* Hero Section */}
        <section className="container mx-auto px-4 py-16 md:py-24">
          <div className="flex flex-col items-center text-center space-y-8">
            <SpaceCowboyIcon className="w-32 h-32 md:w-40 md:h-40" />

            <div className="space-y-4 max-w-3xl">
              <Badge variant="secondary" className="text-sm px-4 py-1">
                Frontier Justice for Digital Integrity
              </Badge>

              <h1 className="text-4xl md:text-6xl lg:text-7xl font-bold tracking-tight text-balance">
                Space Cowboy
                <span className="block text-primary">Anti-Cheat System</span>
              </h1>

              <p className="text-lg md:text-xl text-muted-foreground leading-relaxed max-w-2xl mx-auto text-pretty">
                Lasso cheaters across the digital frontier. Advanced monitoring for interviews and classroom integrity
                with real-time detection.
              </p>
            </div>

            <div className="flex flex-col sm:flex-row gap-4">
              <Button size="lg" className="text-lg px-8">
                Start Monitoring
              </Button>
              <Button size="lg" variant="outline" className="text-lg px-8 bg-transparent">
                View Demo
              </Button>
            </div>
          </div>
        </section>

        {/* Features Grid */}
        <section className="container mx-auto px-4 py-16">
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            <Card className="bg-card/50 backdrop-blur border-border">
              <CardHeader>
                <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
                  <Video className="w-6 h-6 text-primary" />
                </div>
                <CardTitle>Interview Monitoring</CardTitle>
                <CardDescription className="text-card-foreground/70">
                  Real-time surveillance during remote interviews to ensure candidate authenticity
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 text-sm text-muted-foreground">
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-accent" />
                    Face detection & tracking
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-accent" />
                    Multiple person detection
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-accent" />
                    Screen sharing analysis
                  </li>
                </ul>
              </CardContent>
            </Card>

            <Card className="bg-card/50 backdrop-blur border-border">
              <CardHeader>
                <div className="w-12 h-12 rounded-lg bg-accent/10 flex items-center justify-center mb-4">
                  <Users className="w-6 h-6 text-accent" />
                </div>
                <CardTitle>Student Monitoring</CardTitle>
                <CardDescription className="text-card-foreground/70">
                  Track student activity and engagement during online classes
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 text-sm text-muted-foreground">
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-accent" />
                    Attention tracking
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-accent" />
                    Tab switching detection
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-accent" />
                    Activity reports
                  </li>
                </ul>
              </CardContent>
            </Card>

            <Card className="bg-card/50 backdrop-blur border-border">
              <CardHeader>
                <div className="w-12 h-12 rounded-lg bg-destructive/10 flex items-center justify-center mb-4">
                  <AlertTriangle className="w-6 h-6 text-destructive" />
                </div>
                <CardTitle>Cheat Detection</CardTitle>
                <CardDescription className="text-card-foreground/70">
                  AI-powered detection of suspicious behavior and cheating attempts
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 text-sm text-muted-foreground">
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-accent" />
                    Unauthorized device usage
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-accent" />
                    Copy-paste detection
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-accent" />
                    Instant alerts
                  </li>
                </ul>
              </CardContent>
            </Card>

            <Card className="bg-card/50 backdrop-blur border-border">
              <CardHeader>
                <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
                  <Eye className="w-6 h-6 text-primary" />
                </div>
                <CardTitle>Live Dashboard</CardTitle>
                <CardDescription className="text-card-foreground/70">
                  Monitor all sessions from a centralized command center
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 text-sm text-muted-foreground">
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-accent" />
                    Real-time overview
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-accent" />
                    Multi-session support
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-accent" />
                    Instant intervention
                  </li>
                </ul>
              </CardContent>
            </Card>

            <Card className="bg-card/50 backdrop-blur border-border">
              <CardHeader>
                <div className="w-12 h-12 rounded-lg bg-accent/10 flex items-center justify-center mb-4">
                  <Shield className="w-6 h-6 text-accent" />
                </div>
                <CardTitle>Secure & Private</CardTitle>
                <CardDescription className="text-card-foreground/70">
                  Enterprise-grade security with full compliance
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 text-sm text-muted-foreground">
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-accent" />
                    End-to-end encryption
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-accent" />
                    GDPR compliant
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-accent" />
                    Data retention controls
                  </li>
                </ul>
              </CardContent>
            </Card>

            <Card className="bg-card/50 backdrop-blur border-border">
              <CardHeader>
                <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
                  <CheckCircle2 className="w-6 h-6 text-primary" />
                </div>
                <CardTitle>Detailed Reports</CardTitle>
                <CardDescription className="text-card-foreground/70">
                  Comprehensive analytics and incident documentation
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 text-sm text-muted-foreground">
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-accent" />
                    Session recordings
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-accent" />
                    Behavior analytics
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-accent" />
                    Export capabilities
                  </li>
                </ul>
              </CardContent>
            </Card>
          </div>
        </section>

        {/* CTA Section */}
        <section className="container mx-auto px-4 py-16 md:py-24">
          <Card className="bg-primary/5 border-primary/20 backdrop-blur">
            <CardContent className="p-8 md:p-12">
              <div className="flex flex-col items-center text-center space-y-6">
                <h2 className="text-3xl md:text-4xl font-bold text-balance">Ready to Wrangle Cheaters?</h2>
                <p className="text-lg text-muted-foreground max-w-2xl text-pretty">
                  Join the frontier of digital integrity. Start monitoring interviews and classrooms with confidence.
                </p>
                <div className="flex flex-col sm:flex-row gap-4">
                  <Button size="lg" className="text-lg px-8">
                    Get Started Free
                  </Button>
                  <Button size="lg" variant="outline" className="text-lg px-8 bg-transparent">
                    Schedule Demo
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </section>
      </div>
    </div>
  )
}
