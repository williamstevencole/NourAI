import { useEffect, useRef } from 'react';

interface Shape {
  x: number;
  y: number;
  vx: number;
  vy: number;
  radius: number;
  color: string;
  opacity: number;
}

export function FruitsBackground() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const shapesRef = useRef<Shape[]>([]);
  const animationFrameRef = useRef<number>();

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Set canvas size
    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    resize();
    window.addEventListener('resize', resize);

    // Subtle color palette
    const colors = [
      'rgba(121, 178, 155, 0.08)', // Soft teal
      'rgba(121, 178, 155, 0.06)', // Lighter teal
      'rgba(121, 178, 155, 0.04)', // Very light teal
    ];

    // Initialize floating shapes (minimal and elegant)
    shapesRef.current = Array.from({ length: 6 }, () => ({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      vx: (Math.random() - 0.5) * 0.3,
      vy: (Math.random() - 0.5) * 0.3,
      radius: 60 + Math.random() * 120,
      color: colors[Math.floor(Math.random() * colors.length)],
      opacity: 0.3 + Math.random() * 0.4,
    }));

    // Animation loop
    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      shapesRef.current.forEach((shape) => {
        // Update position
        shape.x += shape.vx;
        shape.y += shape.vy;

        // Bounce off edges
        if (shape.x < -shape.radius || shape.x > canvas.width + shape.radius) {
          shape.vx *= -1;
        }
        if (shape.y < -shape.radius || shape.y > canvas.height + shape.radius) {
          shape.vy *= -1;
        }

        // Draw shape with gradient
        const gradient = ctx.createRadialGradient(shape.x, shape.y, 0, shape.x, shape.y, shape.radius);
        gradient.addColorStop(0, shape.color);
        gradient.addColorStop(1, 'rgba(121, 178, 155, 0)');

        ctx.fillStyle = gradient;
        ctx.beginPath();
        ctx.arc(shape.x, shape.y, shape.radius, 0, Math.PI * 2);
        ctx.fill();
      });

      animationFrameRef.current = requestAnimationFrame(animate);
    };
    animate();

    return () => {
      window.removeEventListener('resize', resize);
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 pointer-events-none z-0"
      style={{ opacity: 0.7 }}
    />
  );
}
