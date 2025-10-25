import { useEffect, useRef } from 'react';
import './LandingPage.css';

function LandingPage() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

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

    function animate() {
      if (!ctx || !canvas) return;

      ctx.fillStyle = 'rgba(10, 10, 30, 0.3)';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

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

      // Draw cowboys (simple silhouettes)
      cowboys.forEach((cowboy) => {
        ctx.fillStyle = 'rgba(50, 30, 20, 0.8)';
        
        // Horse body
        ctx.fillRect(cowboy.x, cowboy.y + cowboy.size / 2, cowboy.size * 1.5, cowboy.size / 2);
        
        // Horse head
        ctx.fillRect(cowboy.x + cowboy.size * 1.5, cowboy.y + cowboy.size / 3, cowboy.size / 3, cowboy.size / 2);
        
        // Cowboy body
        ctx.fillRect(cowboy.x + cowboy.size / 2, cowboy.y, cowboy.size / 3, cowboy.size / 2);
        
        // Cowboy hat
        ctx.fillRect(cowboy.x + cowboy.size / 3, cowboy.y - cowboy.size / 4, cowboy.size / 2, cowboy.size / 6);

        cowboy.x += cowboy.vx;

        if (cowboy.x > canvas.width) {
          cowboy.x = -cowboy.size * 2;
          cowboy.y = canvas.height - 150 - Math.random() * 100;
        }
      });

      requestAnimationFrame(animate);
    }

    animate();

    const handleResize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, []);

  return (
    <div className="landing-page">
      <canvas ref={canvasRef} className="starry-background" />
      
      <div className="content">
        <section className="hero">
          <div className="hero-text">
            <h1 className="hero-line line-1">CheaterBuster for Meetings.</h1>
            <h1 className="hero-line line-2">Welcome to a new era of trust</h1>
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
