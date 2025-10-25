import { useEffect, useRef, useState } from 'react';
import './LandingPage.css';

function LandingPage() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isDarkTheme, setIsDarkTheme] = useState(true);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    // Mountain peaks for light theme
    const mountains: { peaks: { x: number; y: number }[]; color: string; offset: number; speed: number }[] = [];
    
    // Create 3 mountain layers
    for (let layer = 0; layer < 3; layer++) {
      const peaks: { x: number; y: number }[] = [];
      const peakCount = 8 + layer * 2;
      const baseHeight = canvas.height * (0.5 + layer * 0.15);
      
      for (let i = 0; i < peakCount; i++) {
        peaks.push({
          x: (canvas.width / peakCount) * i,
          y: baseHeight - Math.random() * 150 - layer * 50,
        });
      }
      
      const lightness = 75 + layer * 8;
      mountains.push({
        peaks,
        color: `hsl(200, 30%, ${lightness}%)`,
        offset: 0,
        speed: 0.05 + layer * 0.02,
      });
    }

    // Stars
    const stars: { x: number; y: number; radius: number; vx: number; vy: number }[] = [];
    for (let i = 0; i < 200; i++) {
      stars.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        radius: Math.random() * 2,
        vx: Math.random() * 0.5 - 0.25,
        vy: Math.random() * 0.5 - 0.25,
      });
    }

    // Cowboys with horses
    const cowboys: { x: number; y: number; vx: number; size: number }[] = [];
    for (let i = 0; i < 5; i++) {
      cowboys.push({
        x: Math.random() * canvas.width,
        y: canvas.height - 150 - Math.random() * 100,
        vx: Math.random() * 0.3 + 0.1,
        size: 40 + Math.random() * 20,
      });
    }

    let animationFrameId: number;
    
    function animate() {
      if (!ctx || !canvas) return;

      // Always clear first, then draw appropriate background
      if (isDarkTheme) {
        ctx.fillStyle = 'rgba(10, 10, 30, 0.3)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
      } else {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
      }

      if (isDarkTheme) {
        // Draw stars
        stars.forEach((star) => {
          ctx.fillStyle = 'white';
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
        // Draw mountains
        mountains.forEach((mountain) => {
          ctx.beginPath();
          ctx.moveTo(0, canvas.height);
          
          // Draw mountain range
          for (let i = 0; i < mountain.peaks.length; i++) {
            const peak = mountain.peaks[i];
            const nextPeak = mountain.peaks[i + 1] || { x: canvas.width, y: canvas.height };
            
            // Peak point
            ctx.lineTo(peak.x + mountain.offset, peak.y);
            
            // Valley between peaks
            const midX = (peak.x + nextPeak.x) / 2 + mountain.offset;
            const midY = Math.max(peak.y, nextPeak.y) + 50;
            ctx.lineTo(midX, midY);
          }
          
          ctx.lineTo(canvas.width, canvas.height);
          ctx.closePath();
          
          ctx.fillStyle = mountain.color;
          ctx.fill();
          
          // Add snow caps to peaks
          mountain.peaks.forEach((peak) => {
            ctx.beginPath();
            ctx.moveTo(peak.x + mountain.offset - 20, peak.y + 30);
            ctx.lineTo(peak.x + mountain.offset, peak.y);
            ctx.lineTo(peak.x + mountain.offset + 20, peak.y + 30);
            ctx.closePath();
            ctx.fillStyle = 'rgba(255, 255, 255, 0.9)';
            ctx.fill();
          });
          
          // Parallax effect
          mountain.offset -= mountain.speed;
          if (mountain.offset < -canvas.width / mountain.peaks.length) {
            mountain.offset = 0;
          }
        });
      }

      // Draw cowboys (for both themes, but different colors)
      cowboys.forEach((cowboy) => {
        const x = cowboy.x;
        const y = cowboy.y;
        const s = cowboy.size;
        
        const horseColor = isDarkTheme ? 'rgba(90, 60, 40, 0.9)' : 'rgba(70, 50, 30, 0.7)';
        const cowboyColor = isDarkTheme ? 'rgba(40, 30, 20, 0.9)' : 'rgba(50, 40, 30, 0.7)';
        const hatColor = isDarkTheme ? 'rgba(60, 40, 20, 0.9)' : 'rgba(80, 60, 40, 0.7)';
        
        // Horse legs (back)
        ctx.fillStyle = horseColor;
        ctx.fillRect(x + s * 0.3, y + s * 0.9, s * 0.12, s * 0.4);
        ctx.fillRect(x + s * 1.1, y + s * 0.9, s * 0.12, s * 0.4);
        
        // Horse body (rounded)
        ctx.beginPath();
        ctx.ellipse(x + s * 0.75, y + s * 0.75, s * 0.6, s * 0.35, 0, 0, Math.PI * 2);
        ctx.fill();
        
        // Horse legs (front)
        ctx.fillRect(x + s * 0.5, y + s * 0.9, s * 0.12, s * 0.4);
        ctx.fillRect(x + s * 1.3, y + s * 0.9, s * 0.12, s * 0.4);
        
        // Horse neck
        ctx.beginPath();
        ctx.moveTo(x + s * 1.2, y + s * 0.6);
        ctx.lineTo(x + s * 1.5, y + s * 0.35);
        ctx.lineTo(x + s * 1.55, y + s * 0.5);
        ctx.lineTo(x + s * 1.3, y + s * 0.75);
        ctx.closePath();
        ctx.fill();
        
        // Horse head
        ctx.beginPath();
        ctx.ellipse(x + s * 1.6, y + s * 0.42, s * 0.15, s * 0.2, 0.3, 0, Math.PI * 2);
        ctx.fill();
        
        // Horse ear
        ctx.beginPath();
        ctx.moveTo(x + s * 1.65, y + s * 0.25);
        ctx.lineTo(x + s * 1.7, y + s * 0.3);
        ctx.lineTo(x + s * 1.6, y + s * 0.3);
        ctx.closePath();
        ctx.fill();
        
        // Horse tail
        ctx.beginPath();
        ctx.moveTo(x + s * 0.15, y + s * 0.7);
        ctx.quadraticCurveTo(x + s * 0.05, y + s * 0.9, x + s * 0.1, y + s * 1.1);
        ctx.lineWidth = s * 0.08;
        ctx.strokeStyle = horseColor;
        ctx.stroke();
        ctx.lineWidth = 1;
        
        // Cowboy body
        ctx.fillStyle = cowboyColor;
        ctx.fillRect(x + s * 0.65, y + s * 0.25, s * 0.28, s * 0.45);
        
        // Cowboy legs
        ctx.fillRect(x + s * 0.65, y + s * 0.7, s * 0.12, s * 0.3);
        ctx.fillRect(x + s * 0.81, y + s * 0.7, s * 0.12, s * 0.3);
        
        // Cowboy arm
        ctx.fillRect(x + s * 0.93, y + s * 0.3, s * 0.25, s * 0.1);
        
        // Cowboy head
        ctx.beginPath();
        ctx.arc(x + s * 0.79, y + s * 0.18, s * 0.12, 0, Math.PI * 2);
        ctx.fill();
        
        // Cowboy hat
        ctx.fillStyle = hatColor;
        // Hat top
        ctx.beginPath();
        ctx.arc(x + s * 0.79, y + s * 0.08, s * 0.1, 0, Math.PI * 2);
        ctx.fill();
        // Hat brim
        ctx.beginPath();
        ctx.ellipse(x + s * 0.79, y + s * 0.15, s * 0.2, s * 0.06, 0, 0, Math.PI * 2);
        ctx.fill();

        cowboy.x += cowboy.vx;

        if (cowboy.x > canvas.width) {
          cowboy.x = -cowboy.size * 2;
          cowboy.y = canvas.height - 150 - Math.random() * 100;
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

  return (
    <div className={`landing-page ${isDarkTheme ? 'dark-theme' : 'light-theme'}`}>
      <canvas ref={canvasRef} className="starry-background" />
      
      {/* Logo */}
      <div className="logo">
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
      
      <div className="content">
        <section className="hero">
          <div className="hero-text">
            <h1 className="hero-line line-1 animate-slide-in">CheaterBuster for Meetings.</h1>
            <h1 className="hero-line line-2 animate-slide-in">Welcome to a new era of trust</h1>
          </div>
          
          <button className="glass-button">
            <span>Get Started</span>
          </button>
        </section>

        <section className="demo-section">
          <h2>See It In Action</h2>
          <div className="video-container">
            <div className="video-placeholder">
              <p>Demo Video Coming Soon</p>
              <span className="play-icon">▶</span>
            </div>
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
