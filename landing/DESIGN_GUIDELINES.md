# Landing Page Design Guidelines

## Overview
The CheaterBuster landing page features an immersive, theme-switchable interface with animated backgrounds and a professional layout designed to build trust and showcase the monitoring solution.

---

## Color Palette

### Dark Theme (Default)
- **Primary Background**: Deep space gradient (#0a0a1e → #1a0a2e → #2a1a3e)
- **Accent Color**: Purple (#8a2be2, rgba(138, 43, 226))
- **Text Primary**: White (#ffffff)
- **Text Secondary**: rgba(255, 255, 255, 0.7)

### Light Theme
- **Primary Background**: Sky gradient (#b8d4e8 → #d4e4f0)
- **Mountain Colors**: Blue-grey range (hsl(200-220, 30-35%, 65-85%))
- **Accent Color**: Steel Blue (#4682b4)
- **Text Primary**: Dark slate (#2c3e50)
- **Text Secondary**: rgba(44, 62, 80, 0.8)

---

## Typography

### Font Families
- **Primary**: System font stack (-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', etc.)
- **Body**: 16px base, line-height 1.6
- **Monospace**: 'Courier New' for technical values

### Hierarchy
- **Hero Title**: 3.5rem (56px), font-weight 700
- **Section Headings**: 2.5rem (40px), font-weight 700
- **Body Text**: 1rem (16px), font-weight 400
- **Buttons**: 1.3rem (20.8px), font-weight 600

---

## Layout Structure

### Sections (in order)
1. **Hero Section**
   - Animated background (stars/mountains)
   - Hero text with two lines
   - Glass button CTA
   - Laptop mockup with dashboard preview

2. **Features Section**
   - 2x2 grid of feature tiles
   - Icons, titles, and descriptions
   - Staggered positioning (tile-1/2 left, tile-3/4 right)

3. **Footer**
   - 4-column grid (auto-fit, min 200px)
   - Company info, Product, Company, Legal sections
   - Copyright notice

### Key Components

#### Logo
- Position: Fixed top-left (2rem from edges)
- SVG icon + "CheaterBuster" text
- Floating animation (3s, ±5px vertical)
- Fades out on scroll (< 100px)

#### Theme Toggle
- Position: Fixed top-right (2rem from edges)
- Circular button (50px diameter)
- ☀️ (sun) in dark mode / 🌙 (moon) in light mode
- 180° rotation on hover

#### Sticky Get Started Button
- Appears when hero button scrolls out of view
- Fixed top-center
- Purple gradient background
- Smooth fade-in/out transition

---

## Animations

### Background Animations

#### Dark Theme - Starry Sky
- 300 stars with varied sizes (0.5-3px radius)
- Twinkling effect using sine wave
- Slow drift motion (0.15-0.3 px/frame)
- Radial glow gradient on each star

#### Light Theme - Mountain Parallax
- 4 layers of mountains with different speeds
- Smooth curves using quadraticCurveTo
- Snow caps on taller peaks
- Horizontal parallax scrolling

#### Horses (Light Theme Only)
- 5 horses using horsey.png image
- Varied sizes (60-100px)
- Different speeds (0.2-0.6 px/frame)
- Subtle shadows for depth
- Respawn on left when exiting right

### Component Animations
- **Hero Text**: Slide in from left (delay: 0.3s, 0.8s)
- **Laptop**: Float animation (3s, ±10px vertical)
- **Buttons**: Glow pulse (2s infinite)
- **Feature Tiles**: Rotate gradient background (10s infinite)

---

## Interactive Elements

### Glass Button
- Background: rgba(255, 255, 255, 0.1)
- Backdrop filter: blur(10px)
- Border: 2px solid rgba(255, 255, 255, 0.2)
- Shine effect: Linear gradient sweep animation
- Hover: Lift effect (translateY -2px)

### Feature Tiles
- Background: Glass morphism effect
- Border: 1px solid rgba(255, 255, 255, 0.1)
- Max-width: 500px
- Hover: Transform up 5px, stronger glow

### Dashboard Mockup
- **Laptop Screen**: Dark background (#1a1a2e)
- **Dashboard Cards**: 3-column grid with hover effects
- **Status Indicators**: Green, yellow, red dots with glow
- **Icons**: Analytics 📊, Security 🔒, Participants 👥

---

## Responsive Breakpoints

### Mobile (<768px)
- Hero text: 2rem font-size
- Features: Single column grid
- All tiles centered (justify-self: center)
- Laptop mockup: 95% width
- Dashboard: Single column
- Button: Smaller padding (1rem 2rem)

### Desktop (≥768px)
- Hero text: 3.5rem font-size
- Features: 2-column grid
- Tiles staggered (left/right positioning)
- Laptop mockup: Max 900px width
- Dashboard: 3-column grid
- Full button size

---

## Accessibility

### Contrast Ratios
- Dark theme text: WCAG AAA compliant (>7:1)
- Light theme text: WCAG AA compliant (>4.5:1)

### Interactive Elements
- All buttons have aria-labels
- Keyboard navigation supported
- Focus states visible
- Smooth scroll behavior

### Motion
- Animations respect prefers-reduced-motion
- Canvas cleared on unmount
- RequestAnimationFrame properly canceled

---

## Performance Considerations

### Canvas Optimization
- Single canvas for all background animations
- Efficient drawing: Clear only necessary areas
- RequestAnimationFrame for smooth 60fps
- Resize handler debounced

### Image Loading
- Lazy load horsey.png
- Check image.complete before drawing
- Proper aspect ratio maintained

### CSS Performance
- Transform and opacity for animations (GPU accelerated)
- Backdrop-filter used sparingly
- Will-change property avoided except where necessary

---

## Theme Switching

### Mechanism
- React state: `isDarkTheme` (boolean)
- Default: Dark theme (true)
- Persists in component lifecycle
- Instant toggle on click

### Transition Effects
- Background: 0.5s ease transition
- Text colors: 0.5s ease transition
- Canvas content: Immediate swap (no transition)
- Border colors: 0.5s ease transition

---

## Brand Identity

### Voice & Tone
- Professional yet approachable
- Emphasis on trust and security
- Educational context without being clinical
- Modern and tech-forward

### Key Messages
1. "CheaterBuster for Meetings"
2. "Welcome to a new era of trust"
3. Focus on meeting integrity and security
4. Real-time detection capabilities

---

## File Structure

```
landing/rowdyUI/
├── src/
│   ├── LandingPage.tsx      # Main component with canvas logic
│   ├── LandingPage.css       # All styles and animations
│   ├── App.tsx               # Root component
│   ├── main.tsx              # Entry point
│   └── index.css             # Base styles
├── assets/
│   └── horsey.png            # Horse sprite for light theme
├── package.json
├── vite.config.ts
└── tsconfig.json
```

---

## Browser Support
- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Canvas 2D API required
- ES2020+ features

---

## Future Enhancements
- [ ] Add prefers-reduced-motion support
- [ ] Implement theme preference persistence (localStorage)
- [ ] Add more interactive elements on scroll
- [ ] Optimize canvas for mobile devices
- [ ] Add loading states for images
- [ ] Consider WebGL for more complex effects
