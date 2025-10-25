import { useEffect, useRef, useState } from 'react';
import './DownloadPage.css';

function DownloadPage() {
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
    const mountains: { peaks: { x: number; y: number }[]; baseColor: string; shadowColor: string; offset: number; speed: number }[] = [];
    
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

    // Stars for dark theme
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

    let animationFrameId: number;
    
    function animate() {
      if (!ctx || !canvas) return;

      if (isDarkTheme) {
        const gradient = ctx.createLinearGradient(0, 0, 0, canvas.height);
        gradient.addColorStop(0, 'rgba(5, 5, 20, 0.4)');
        gradient.addColorStop(0.5, 'rgba(15, 10, 30, 0.3)');
        gradient.addColorStop(1, 'rgba(25, 15, 40, 0.2)');
        ctx.fillStyle = gradient;
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // Draw stars
        stars.forEach((star) => {
          star.twinkle += 0.02;
          const twinkleAlpha = 0.5 + Math.sin(star.twinkle) * 0.5;
          const brightness = star.brightness * twinkleAlpha;
          
          const gradient = ctx.createRadialGradient(star.x, star.y, 0, star.x, star.y, star.radius * 3);
          gradient.addColorStop(0, `rgba(255, 255, 255, ${brightness})`);
          gradient.addColorStop(0.3, `rgba(200, 220, 255, ${brightness * 0.5})`);
          gradient.addColorStop(1, 'rgba(138, 43, 226, 0)');
          ctx.fillStyle = gradient;
          ctx.beginPath();
          ctx.arc(star.x, star.y, star.radius * 3, 0, Math.PI * 2);
          ctx.fill();
          
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
        const gradient = ctx.createLinearGradient(0, 0, 0, canvas.height);
        gradient.addColorStop(0, 'rgba(180, 210, 240, 0.3)');
        gradient.addColorStop(0.5, 'rgba(200, 220, 245, 0.2)');
        gradient.addColorStop(1, 'rgba(220, 235, 250, 0.1)');
        ctx.fillStyle = gradient;
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // Draw mountains
        mountains.forEach((mountain, mountainIndex) => {
          ctx.beginPath();
          ctx.moveTo(-50, canvas.height);
          
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
          
          const gradient = ctx.createLinearGradient(0, canvas.height * 0.3, 0, canvas.height);
          gradient.addColorStop(0, mountain.baseColor);
          gradient.addColorStop(1, mountain.shadowColor);
          ctx.fillStyle = gradient;
          ctx.fill();
          
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
          
          if (mountainIndex < 2) {
            mountain.peaks.forEach((peak, i) => {
              if (i % 2 === 0 && peak.y < canvas.height * 0.6) {
                const x = peak.x + mountain.offset;
                
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
          
          mountain.offset -= mountain.speed;
          if (mountain.offset < -canvas.width / mountain.peaks.length) {
            mountain.offset = 0;
          }
        });
      }

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
      if (ctx && canvas) {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
      }
    };
  }, [isDarkTheme]);

  const handleDownload = () => {
    // Create an empty zip file (minimal zip file structure)
    const zipData = new Uint8Array([
      0x50, 0x4B, 0x05, 0x06, 0x00, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x00, 0x00
    ]);

    const blob = new Blob([zipData], { type: 'application/zip' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'download.zip';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <div className={`download-page ${isDarkTheme ? 'dark-theme' : 'light-theme'}`}>
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
        <div className="download-container">
          <div className="download-card">
            <div className="card-header">
              <div className="file-icon">
                <svg width="80" height="80" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M13 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V9L13 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  <path d="M13 2V9H20" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </div>
              <h1 className="download-title">Your Download is Ready</h1>
              <p className="download-subtitle">Click the button below to download your file</p>
            </div>
            
            <div className="file-info">
              <div className="info-item">
                <span className="info-label">File Name:</span>
                <span className="info-value">download.zip</span>
              </div>
              <div className="info-item">
                <span className="info-label">File Size:</span>
                <span className="info-value">~1 KB</span>
              </div>
              <div className="info-item">
                <span className="info-label">File Type:</span>
                <span className="info-value">ZIP Archive</span>
              </div>
            </div>

            <button className="download-button" onClick={handleDownload}>
              <svg className="download-icon" width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 3V16M12 16L7 11M12 16L17 11" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                <path d="M3 17V19C3 20.1046 3.89543 21 5 21H19C20.1046 21 21 20.1046 21 19V17" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
              </svg>
              <span>Download Now</span>
            </button>

            <div className="download-footer">
              <p className="security-note">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2C6.47715 2 2 6.47715 2 12C2 17.5228 6.47715 22 12 22Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  <path d="M9 12L11 14L15 10" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
                Secure download • Virus-free
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default DownloadPage;
