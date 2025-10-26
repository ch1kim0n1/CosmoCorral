import { useEffect, useRef } from 'react';
import './LandingPage.css';
import horseyImg from '../assets/horsey.png';
import capybaraImg from '../assets/capybarautsa-removebg-preview.png';

function LandingPage() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    // Stars (static, no twinkling)
    const stars: { x: number; y: number; radius: number; opacity: number }[] = [];
    for (let i = 0; i < 150; i++) {
      stars.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        radius: Math.random() * 1.5 + 0.5,
        opacity: Math.random() * 0.4 + 0.3,
      });
    }

    // Cowboys with horses (static positions spread across page)
    const horseyImage = new Image();
    horseyImage.src = horseyImg;
    
    const cowboys: { x: number; y: number; size: number; opacity: number }[] = [];
    const positions = [
      { x: 0.08, y: 0.15 },
      { x: 0.2, y: 0.35 },
      { x: 0.12, y: 0.6 },
      { x: 0.35, y: 0.2 },
      { x: 0.3, y: 0.7 },
      { x: 0.48, y: 0.25 },
      { x: 0.52, y: 0.55 },
      { x: 0.45, y: 0.8 },
      { x: 0.65, y: 0.18 },
      { x: 0.7, y: 0.45 },
      { x: 0.62, y: 0.75 },
      { x: 0.82, y: 0.3 },
      { x: 0.88, y: 0.6 },
      { x: 0.92, y: 0.85 },
    ];
    
    positions.forEach(pos => {
      const initialX = pos.x * canvas.width;
      const initialY = pos.y * canvas.height;
      // Exclude cowboys from bottom area (desert + buffer)
      if (initialY < canvas.height - 200) {
        cowboys.push({
          x: initialX,
          y: initialY,
          size: 45 + Math.random() * 35,
          opacity: 0.35 + Math.random() * 0.25,
        });
      }
    });

    function animate() {
      if (!ctx || !canvas) return;

      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Draw stars (static, no animation)
      stars.forEach((star) => {
        ctx.fillStyle = `rgba(255, 255, 255, ${star.opacity})`;
        ctx.beginPath();
        ctx.arc(star.x, star.y, star.radius, 0, Math.PI * 2);
        ctx.fill();
      });

      // Draw cowboys (static positions)
      cowboys.forEach((cowboy) => {
        if (horseyImage.complete) {
          ctx.globalAlpha = cowboy.opacity;
          ctx.drawImage(
            horseyImage,
            cowboy.x,
            cowboy.y,
            cowboy.size,
            cowboy.size * (horseyImage.height / horseyImage.width)
          );
          ctx.globalAlpha = 1;
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
      <canvas ref={canvasRef} className="background-canvas" />
      
      <main className="main">
        <div className="page-header">
          <div className="logo">CheaterBuster</div>
          <div className="header-actions">
            <button className="nav-cta">Head to Dashboard</button>
          </div>
        </div>

        <section className="hero">
          <div className="hero-content">
            <h1>The world's fastest educational monitoring</h1>
            
            <p className="hero-text">
              CheaterBuster brings you the <span className="highlight">fastest monitoring solution</span> available for educational institutions. 
              Monitor student devices in real-time with exceptional speed and reliability.
            </p>
            
            <p className="hero-text">
              Our <span className="highlight">distributed architecture</span> unlocks unlimited monitoring capacity, 
              bringing enterprise performance to educational institutions. We offer a range of deployment options to cover 
              all of your security and compliance requirements.
            </p>
          </div>
        </section>

        <section className="features">
          <div className="feature-item">
            <div className="feature-symbol">◆</div>
            <h3>Real-time monitoring</h3>
            <p>Monitor all connected devices instantly with millisecond latency</p>
          </div>
          <div className="feature-item">
            <div className="feature-symbol">◇</div>
            <h3>Enterprise security</h3>
            <p>Built-in security and compliance features for educational institutions</p>
          </div>
          <div className="feature-item">
            <div className="feature-symbol">◈</div>
            <h3>Zero-config deployment</h3>
            <p>Deploy across your institution in minutes with automatic discovery</p>
          </div>
          <div className="feature-item">
            <div className="feature-symbol">◉</div>
            <h3>Advanced analytics</h3>
            <p>Deep insights into device usage patterns and behavior analysis</p>
          </div>
          <div className="feature-item">
            <div className="feature-symbol">◊</div>
            <h3>Multi-platform support</h3>
            <p>Works seamlessly across Windows, macOS, Linux, iOS, and Android</p>
          </div>
          <div className="feature-item">
            <div className="feature-symbol">○</div>
            <h3>Scalable architecture</h3>
            <p>From 10 to 100,000+ devices with consistent performance</p>
          </div>
        </section>

      </main>

      <div className="desert-scene">
        <div className="desert-ground"></div>
        <div className="cactus cactus-1">🌵</div>
        <div className="cactus cactus-2">🌵</div>
        <div className="cactus cactus-3">🌵</div>
        <div className="cactus cactus-4">🌵</div>
        <div className="cactus cactus-5">🌵</div>
        <div className="cactus cactus-6">🌵</div>
        <div className="cactus cactus-7">🌵</div>
        <img src={capybaraImg} alt="capybara" className="capybara capybara-1" />
        <img src={capybaraImg} alt="capybara" className="capybara capybara-2" />
        <img src={capybaraImg} alt="capybara" className="capybara capybara-3" />
      </div>

      <div className="aliens-background">
        <div className="alien alien-1">👽</div>
        <div className="alien alien-2">👽</div>
        <div className="alien alien-3">👽</div>
        <div className="alien alien-4">👽</div>
      </div>
    </div>
  );
}

export default LandingPage;
