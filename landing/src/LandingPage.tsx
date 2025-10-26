import { useEffect, useRef, useState } from 'react';
import './LandingPage.css';
import horseyImg from '../assets/horsey.png';
import capybaraImg from '../assets/capybarautsa-removebg-preview.png';
import roadrunnerImg from '../assets/roadrunner.png';
import roadrunner2Img from '../assets/roadrunner2.png';
import gunshotSound from '../assets/gunshot.mp3';
import roadrunner2Sound from '../assets/beep.mp3';

function LandingPage() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const audio2Ref = useRef<HTMLAudioElement | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isPlaying2, setIsPlaying2] = useState(false);

  // Prime and unlock audio on first user interaction (required by browsers)
  useEffect(() => {
    const a1 = new Audio(gunshotSound);
    const a2 = new Audio(roadrunner2Sound);
    a1.preload = 'auto';
    a2.preload = 'auto';
    audioRef.current = a1;
    audio2Ref.current = a2;

    const unlock = async () => {
      const prime = async (el: HTMLAudioElement) => {
        try {
          el.muted = true;
          await el.play();
          el.pause();
          el.currentTime = 0;
          el.muted = false;
        } catch {
          // ignore - user blocked or other transient errors
        }
      };
      if (audioRef.current) await prime(audioRef.current);
      if (audio2Ref.current) await prime(audio2Ref.current);
    };

    // pointerdown covers mouse, touch, pen. Use once to avoid leaks.
    window.addEventListener('pointerdown', unlock, { once: true });
    return () => {
      window.removeEventListener('pointerdown', unlock);
    };
  }, []);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    // Twinkling stars like dashboard
    const stars: { x: number; y: number; radius: number; opacity: number; speed: number }[] = [];
    for (let i = 0; i < 200; i++) {
      stars.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        radius: Math.random() * 1.5,
        opacity: Math.random(),
        speed: Math.random() * 0.02,
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

      // Draw twinkling stars
      stars.forEach((star) => {
        star.opacity += star.speed;
        if (star.opacity > 1 || star.opacity < 0.2) {
          star.speed = -star.speed;
        }
        
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

  const handleCactusMouseEnter = () => {
    if (isPlaying) return;

    const audio = audioRef.current ?? new Audio(gunshotSound);
    audioRef.current = audio;
    setIsPlaying(true);
    audio.currentTime = 0;
    audio.volume = 1;
    audio.play().catch(() => setIsPlaying(false));
    audio.onended = () => setIsPlaying(false);
  };

  const handleCactus2MouseEnter = () => {
    if (isPlaying2) return;

    const audio = audio2Ref.current ?? new Audio(roadrunner2Sound);
    audio2Ref.current = audio;
    setIsPlaying2(true);
    audio.currentTime = 0;
    audio.volume = 1;
    audio.play().catch(() => setIsPlaying2(false));
    audio.onended = () => setIsPlaying2(false);
  };

  return (
    <div className="landing-page">
      <canvas ref={canvasRef} className="background-canvas" />
      
      <main className="main">
        <div className="page-header">
          <div className="logo">Cosmo Corral</div>
          <div className="header-actions">
            <a href="http://localhost:3000"><button className="nav-cta">Head to Dashboard</button></a>
          </div>
        </div>

        <section className="hero">
          <div className="hero-content">
            <h1>The world's fastest monitoring</h1>
            
            <p className="hero-text">
              <span className="highlight">Cosmo Corral</span> delivers the <span className="highlight">fastest monitoring solution</span> available for modern networks. 
              Monitors and manages devices in real time with exceptional speed, reliability, and precision.
            </p>
            
            <p className="hero-text">
              Our <span className="highlight">distributed architecture</span> unlocks virtually unlimited monitoring capacity, 
              bringing enterprise-grade performance to organizations of any size. With flexible deployment options and robust security, 
              Cosmo Corral keeps your systems protected, compliant, and under control—no matter how wild the digital frontier gets.
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
        <div 
          className="cactus-container cactus-container-3"
          onMouseEnter={handleCactusMouseEnter}
        >
          <img src={roadrunnerImg} alt="roadrunner" className="roadrunner" />
          <div className="cactus cactus-3">🌵</div>
        </div>
        <div className="cactus cactus-4">🌵</div>
        <div className="cactus cactus-5">🌵</div>
        <div 
          className="cactus-container cactus-container-6"
          onMouseEnter={handleCactus2MouseEnter}
        >
          <img src={roadrunner2Img} alt="roadrunner2" className="roadrunner" />
          <div className="cactus cactus-6">🌵</div>
        </div>
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
