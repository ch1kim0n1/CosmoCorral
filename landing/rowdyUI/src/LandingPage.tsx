import { useEffect, useRef, useState } from 'react';
import './LandingPage.css';
import horseyImg from '../assets/horsey.png';

function LandingPage() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isDarkTheme, setIsDarkTheme] = useState(true);
  const [showStickyButton, setShowStickyButton] = useState(false);
  const [showLogo, setShowLogo] = useState(true);
  const heroButtonRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    // Mountain peaks for light theme with more detail
    const mountains: { peaks: { x: number; y: number }[]; baseColor: string; shadowColor: string; offset: number; speed: number }[] = [];
    
    // Create 4 mountain layers for more depth
    for (let layer = 0; layer < 4; layer++) {
      const peaks: { x: number; y: number }[] = [];
      const peakCount = 6 + layer * 3;
      const baseHeight = canvas.height * (0.4 + layer * 0.15);
      
      for (let i = 0; i <= peakCount; i++) {
        const variance = Math.random() * 120 - 60;
        peaks.push({
          x: (canvas.width / peakCount) * i,
          y: baseHeight - Math.random() * 180 - layer * 40 + variance,
        });
      }
      
      const hue = 200 + layer * 5;
      const saturation = 35 - layer * 5;
      const lightness = 65 + layer * 10;
      mountains.push({
        peaks,
        baseColor: `hsla(${hue}, ${saturation}%, ${lightness}%, 0.85)`,
        shadowColor: `hsla(${hue}, ${saturation + 10}%, ${lightness - 15}%, 0.6)`,
        offset: 0,
        speed: 0.03 + layer * 0.015,
      });
    }

    // Stars with varied sizes and brightness
    const stars: { x: number; y: number; radius: number; vx: number; vy: number; brightness: number; twinkle: number }[] = [];
    for (let i = 0; i < 300; i++) {
      stars.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        radius: Math.random() * 2.5 + 0.5,
        vx: Math.random() * 0.3 - 0.15,
        vy: Math.random() * 0.3 - 0.15,
        brightness: Math.random(),
        twinkle: Math.random() * Math.PI * 2,
      });
    }

    // Load horsey image
    const horseyImage = new Image();
    horseyImage.src = horseyImg;
    
    // Horses with varied sizes and positions
    const horses: { x: number; y: number; vx: number; size: number; opacity: number }[] = [];
    for (let i = 0; i < 5; i++) {
      horses.push({
        x: Math.random() * canvas.width,
        y: canvas.height - 100 - Math.random() * 80,
        vx: Math.random() * 0.4 + 0.2,
        size: 60 + Math.random() * 40,
        opacity: isDarkTheme ? 0.85 : 0.75,
      });
    }

    let animationFrameId: number;
    
    function animate() {
      if (!ctx || !canvas) return;

      // Always clear first, then draw appropriate background
      if (isDarkTheme) {
        // Dark theme: Deep space gradient
        const gradient = ctx.createLinearGradient(0, 0, 0, canvas.height);
        gradient.addColorStop(0, 'rgba(5, 5, 20, 0.4)');
        gradient.addColorStop(0.5, 'rgba(15, 10, 30, 0.3)');
        gradient.addColorStop(1, 'rgba(25, 15, 40, 0.2)');
        ctx.fillStyle = gradient;
        ctx.fillRect(0, 0, canvas.width, canvas.height);
      } else {
        // Light theme: Sky gradient
        const gradient = ctx.createLinearGradient(0, 0, 0, canvas.height);
        gradient.addColorStop(0, 'rgba(180, 210, 240, 0.3)');
        gradient.addColorStop(0.5, 'rgba(200, 220, 245, 0.2)');
        gradient.addColorStop(1, 'rgba(220, 235, 250, 0.1)');
        ctx.fillStyle = gradient;
        ctx.fillRect(0, 0, canvas.width, canvas.height);
      }

      if (isDarkTheme) {
        // Draw stars with twinkling effect
        stars.forEach((star) => {
          star.twinkle += 0.02;
          const twinkleAlpha = 0.5 + Math.sin(star.twinkle) * 0.5;
          const brightness = star.brightness * twinkleAlpha;
          
          // Star glow
          const gradient = ctx.createRadialGradient(star.x, star.y, 0, star.x, star.y, star.radius * 3);
          gradient.addColorStop(0, `rgba(255, 255, 255, ${brightness})`);
          gradient.addColorStop(0.3, `rgba(200, 220, 255, ${brightness * 0.5})`);
          gradient.addColorStop(1, 'rgba(138, 43, 226, 0)');
          ctx.fillStyle = gradient;
          ctx.beginPath();
          ctx.arc(star.x, star.y, star.radius * 3, 0, Math.PI * 2);
          ctx.fill();
          
          // Star core
          ctx.fillStyle = `rgba(255, 255, 255, ${brightness})`;
          ctx.beginPath();
          ctx.arc(star.x, star.y, star.radius, 0, Math.PI * 2);
          ctx.fill();

          star.x += star.vx;
          star.y += star.vy;

          if (star.x < 0) star.x = canvas.width;
          if (star.x > canvas.width) star.x = 0;
          if (star.y < 0) star.y = canvas.height;
          if (star.y > canvas.height) star.y = 0;
        });
      } else {
        // Draw mountains with enhanced details
        mountains.forEach((mountain, mountainIndex) => {
          // Main mountain body
          ctx.beginPath();
          ctx.moveTo(-50, canvas.height);
          
          // Draw smooth mountain range using curves
          for (let i = 0; i < mountain.peaks.length - 1; i++) {
            const peak = mountain.peaks[i];
            const nextPeak = mountain.peaks[i + 1];
            
            const x = peak.x + mountain.offset;
            const nextX = nextPeak.x + mountain.offset;
            const midX = (x + nextX) / 2;
            const midY = (peak.y + nextPeak.y) / 2 + 30;
            
            ctx.lineTo(x, peak.y);
            ctx.quadraticCurveTo(midX, midY, nextX, nextPeak.y);
          }
          
          ctx.lineTo(canvas.width + 50, canvas.height);
          ctx.closePath();
          
          // Mountain gradient fill
          const gradient = ctx.createLinearGradient(0, canvas.height * 0.3, 0, canvas.height);
          gradient.addColorStop(0, mountain.baseColor);
          gradient.addColorStop(1, mountain.shadowColor);
          ctx.fillStyle = gradient;
          ctx.fill();
          
          // Add shading on the right side of peaks
          mountain.peaks.forEach((peak, i) => {
            if (i < mountain.peaks.length - 1) {
              const x = peak.x + mountain.offset;
              ctx.beginPath();
              ctx.moveTo(x, peak.y);
              ctx.lineTo(x + 40, peak.y + 60);
              ctx.lineTo(x, peak.y + 60);
              ctx.closePath();
              ctx.fillStyle = mountain.shadowColor;
              ctx.fill();
            }
          });
          
          // Add snow caps to peaks (only on front mountains)
          if (mountainIndex < 2) {
            mountain.peaks.forEach((peak, i) => {
              if (i % 2 === 0 && peak.y < canvas.height * 0.6) {
                const x = peak.x + mountain.offset;
                
                // Snow gradient
                const snowGradient = ctx.createLinearGradient(x, peak.y, x, peak.y + 40);
                snowGradient.addColorStop(0, 'rgba(255, 255, 255, 0.95)');
                snowGradient.addColorStop(1, 'rgba(240, 248, 255, 0.7)');
                
                ctx.beginPath();
                ctx.moveTo(x - 25, peak.y + 35);
                ctx.lineTo(x, peak.y);
                ctx.lineTo(x + 25, peak.y + 35);
                ctx.closePath();
                ctx.fillStyle = snowGradient;
                ctx.fill();
              }
            });
          }
          
          // Parallax effect
          mountain.offset -= mountain.speed;
          if (mountain.offset < -canvas.width / mountain.peaks.length) {
            mountain.offset = 0;
          }
        });
      }

      // Draw horses using the image
      horses.forEach((horse) => {
        if (horseyImage.complete) {
          ctx.save();
          ctx.globalAlpha = horse.opacity;
          
          // Add subtle shadow for depth
          ctx.shadowColor = 'rgba(0, 0, 0, 0.3)';
          ctx.shadowBlur = 10;
          ctx.shadowOffsetX = 5;
          ctx.shadowOffsetY = 5;
          
          // Draw the horse image
          ctx.drawImage(
            horseyImage,
            horse.x,
            horse.y,
            horse.size,
            horse.size * (horseyImage.height / horseyImage.width)
          );
          
          ctx.restore();
        }

        horse.x += horse.vx;

        if (horse.x > canvas.width) {
          horse.x = -horse.size;
          horse.y = canvas.height - 100 - Math.random() * 80;
        }
      });

      animationFrameId = requestAnimationFrame(animate);
    }

    animate();

    const handleResize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      cancelAnimationFrame(animationFrameId);
      // Clear canvas on cleanup
      if (ctx && canvas) {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
      }
    };
  }, [isDarkTheme]);

  // Sticky button visibility and logo hide on scroll
  useEffect(() => {
    const handleScroll = () => {
      if (heroButtonRef.current) {
        const rect = heroButtonRef.current.getBoundingClientRect();
        // Show sticky button when hero button is out of view
        setShowStickyButton(rect.bottom < 0);
      }
      
      // Hide logo when scrolled down
      setShowLogo(window.scrollY < 100);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <div className={`landing-page ${isDarkTheme ? 'dark-theme' : 'light-theme'}`}>
      <canvas ref={canvasRef} className="starry-background" />
      
      {/* Logo */}
      <div className={`logo ${showLogo ? 'visible' : 'hidden'}`}>
        <svg width="50" height="50" viewBox="0 0 50 50" fill="none" xmlns="http://www.w3.org/2000/svg">
          <circle cx="25" cy="25" r="20" stroke="currentColor" strokeWidth="2" fill="none" />
          <path d="M25 15 L25 35 M15 25 L35 25" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
          <circle cx="25" cy="25" r="3" fill="currentColor" />
        </svg>
        <span>CheaterBuster</span>
      </div>

      {/* Theme Toggle */}
      <button 
        className="theme-toggle"
        onClick={() => setIsDarkTheme(!isDarkTheme)}
        aria-label="Toggle theme"
      >
        {isDarkTheme ? '☀️' : '🌙'}
      </button>

      {/* Sticky Get Started Button */}
      <button 
        className={`sticky-get-started ${showStickyButton ? 'visible' : ''}`}
        aria-label="Get Started"
      >
        Get Started
      </button>
      
      <div className="content">
        <section className="hero">
          <div className="hero-text">
            <h1 className="hero-line line-1 animate-slide-in">CheaterBuster for Meetings.</h1>
            <h1 className="hero-line line-2 animate-slide-in">Welcome to a new era of trust</h1>
          </div>
          
          <button ref={heroButtonRef} className="glass-button">
            <span>Get Started</span>
          </button>

          {/* Laptop Mockup */}
          <div className="laptop-mockup">
            <div className="laptop-screen">
              <div className="dashboard-placeholder">
                <div className="dashboard-header">
                  <div className="dashboard-title">Meeting Dashboard</div>
                  <div className="status-indicators">
                    <span className="status-dot green"></span>
                    <span className="status-dot yellow"></span>
                    <span className="status-dot red"></span>
                  </div>
                </div>
                <div className="dashboard-content">
                  <div className="dashboard-card">
                    <div className="card-icon">📊</div>
                    <div className="card-text">Analytics</div>
                  </div>
                  <div className="dashboard-card">
                    <div className="card-icon">🔒</div>
                    <div className="card-text">Security</div>
                  </div>
                  <div className="dashboard-card">
                    <div className="card-icon">👥</div>
                    <div className="card-text">Participants</div>
                  </div>
                </div>
              </div>
            </div>
            <div className="laptop-base"></div>
            <div className="laptop-notch"></div>
          </div>
        </section>

        <section className="features-section">
          <h2>Features</h2>
          <div className="features-grid">
            <div className="feature-tile tile-1">
              <div className="feature-icon">🔍</div>
              <h3>Real-Time Detection</h3>
              <p>Monitor meetings in real-time for suspicious behavior and unauthorized participants.</p>
            </div>
            <div className="feature-tile tile-2">
              <div className="feature-icon">🛡️</div>
              <h3>Advanced Security</h3>
              <p>Enterprise-grade encryption and security protocols to protect your meetings.</p>
            </div>
            <div className="feature-tile tile-3">
              <div className="feature-icon">📊</div>
              <h3>Detailed Analytics</h3>
              <p>Get comprehensive reports and insights on meeting integrity and participant behavior.</p>
            </div>
            <div className="feature-tile tile-4">
              <div className="feature-icon">⚡</div>
              <h3>Instant Alerts</h3>
              <p>Receive immediate notifications when potential security threats are detected.</p>
            </div>
          </div>
        </section>

        <footer className="footer">
          <div className="footer-content">
            <div className="footer-section">
              <h4>CheaterBuster</h4>
              <p>Building trust in digital meetings</p>
            </div>
            <div className="footer-section">
              <h4>Product</h4>
              <ul>
                <li>Features</li>
                <li>Pricing</li>
                <li>Demo</li>
              </ul>
            </div>
            <div className="footer-section">
              <h4>Company</h4>
              <ul>
                <li>About Us</li>
                <li>Contact</li>
                <li>Careers</li>
              </ul>
            </div>
            <div className="footer-section">
              <h4>Legal</h4>
              <ul>
                <li>Privacy Policy</li>
                <li>Terms of Service</li>
                <li>Security</li>
              </ul>
            </div>
          </div>
          <div className="footer-bottom">
            <p>&copy; 2025 CheaterBuster. All rights reserved.</p>
          </div>
        </footer>
      </div>
    </div>
  );
}

export default LandingPage;
