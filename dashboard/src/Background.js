import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/examples/jsm/postprocessing/UnrealBloomPass.js';

const Background = ({ theme }) => {
  const canvasRef = useRef(null);
  const particlesMeshRef = useRef(null);
  const isDark = theme === 'dark';

  useEffect(() => {
    if (!canvasRef.current) return;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(65, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.set(0, 5, 45);

    const renderer = new THREE.WebGLRenderer({
      canvas: canvasRef.current,
      antialias: true,
      alpha: true
    });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

    const particlesCount = 4000;
    const particlesGeometry = new THREE.BufferGeometry();
    
    const randomPos = new Float32Array(particlesCount * 3);
    const shieldPos = new Float32Array(particlesCount * 3);
    const currentPos = new Float32Array(particlesCount * 3);
    const velocities = new Float32Array(particlesCount * 3);

    // 1. Generate Shield & Fingerprint points
    const getShieldBoundary = (ny) => {
      if (ny > 0.4) return 0.9;
      if (ny > -0.2) return 1.0;
      return 1.0 - Math.pow(( -0.2 - ny ) / 0.8, 1.2);
    };

    const getFingerprintPoint = (i) => {
      // Outline points
      if (i < 800) {
        const t = (i / 800) * 2 - 1; 
        const xSign = i % 2 === 0 ? 1 : -1;
        const ny = t * 1.2;
        const limit = getShieldBoundary(ny);
        return { x: limit * 11 * xSign, y: ny * 14, z: (Math.random() - 0.5) * 0.5 };
      }

      // Arcs (Fingerprint pattern)
      const arcID = Math.floor(Math.random() * 10);
      const radius = 3 + arcID * 2.5;
      
      let cx = 0, cy = -6;
      if (arcID > 6) { cx = 6; cy = 6; } 
      
      const angle = Math.random() * Math.PI * 1.4 - Math.PI * 0.2;
      let px = cx + Math.cos(angle) * radius;
      let py = cy + Math.sin(angle) * radius;
      
      const ny = py / 14;
      const nx = Math.abs(px) / 11;
      const limit = getShieldBoundary(ny);
      
      if (nx > limit || ny > 1.1 || ny < -1.1) {
        return { x: (Math.random() - 0.5) * 15, y: (Math.random() - 0.5) * 20, z: (Math.random() - 0.5) * 2 };
      }
      
      return { x: px, y: py, z: (Math.random() - 0.5) * 0.5 };
    };

    for (let i = 0; i < particlesCount; i++) {
      // Random field
      randomPos[i * 3] = (Math.random() - 0.5) * 120;
      randomPos[i * 3 + 1] = (Math.random() - 0.5) * 120;
      randomPos[i * 3 + 2] = (Math.random() - 0.5) * 120;

      // Velocities for random motion
      velocities[i * 3] = (Math.random() - 0.5) * 0.05;
      velocities[i * 3 + 1] = (Math.random() - 0.5) * 0.05;
      velocities[i * 3 + 2] = (Math.random() - 0.5) * 0.05;

      // Shield Target
      const sp = getFingerprintPoint(i);
      shieldPos[i * 3] = sp.x;
      shieldPos[i * 3 + 1] = sp.y;
      shieldPos[i * 3 + 2] = sp.z;

      // Initial state
      currentPos[i * 3] = randomPos[i * 3];
      currentPos[i * 3 + 1] = randomPos[i * 3 + 1];
      currentPos[i * 3 + 2] = randomPos[i * 3 + 2];
    }

    particlesGeometry.setAttribute('position', new THREE.BufferAttribute(currentPos, 3));
    
    const particlesMaterial = new THREE.PointsMaterial({
      size: 0.22,
      color: isDark ? 0xbc13fe : 0xff0080,
      transparent: true,
      opacity: isDark ? 0.7 : 0.6,
      blending: THREE.AdditiveBlending
    });
    
    const particlesMesh = new THREE.Points(particlesGeometry, particlesMaterial);
    particlesMeshRef.current = particlesMesh;
    scene.add(particlesMesh);

    // Animation State Controller
    let startTime = Date.now();
    let state = 'RANDOM';
    let transitionDuration = 3500;
    let holdDuration = 6000;
    let lastStateChange = startTime;

    const animate = () => {
      requestAnimationFrame(animate);
      const now = Date.now();
      const elapsed = now - lastStateChange;

      const positions = particlesGeometry.attributes.position.array;

      if (state === 'RANDOM') {
        if (elapsed > 6000) { // Stay random longer
          state = 'CONVERGING';
          lastStateChange = now;
        }
        // Dynamic random motion
        for (let i = 0; i < particlesCount * 3; i++) {
          positions[i] += velocities[i];
          // Boundary check for random field
          if (Math.abs(positions[i]) > 70) velocities[i] *= -1;
        }
      } else if (state === 'CONVERGING') {
        const t = Math.min(elapsed / transitionDuration, 1);
        const easeT = t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
        
        for (let i = 0; i < particlesCount * 3; i++) {
          const base = randomPos[i] + (elapsed/1000) * (velocities[i] * 5); // Incorporate drift
          positions[i] = base + (shieldPos[i] - base) * easeT;
        }
        
        if (t === 1) {
          state = 'SHIELD';
          lastStateChange = now;
        }
      } else if (state === 'SHIELD') {
        if (elapsed > holdDuration) {
          state = 'DISPERSING';
          lastStateChange = now;
        }
        const pulse = Math.sin(now * 0.0015) * 0.15;
        particlesMesh.position.y = pulse;
        particlesMesh.rotation.y = Math.sin(now * 0.0005) * 0.15;
      } else if (state === 'DISPERSING') {
        const t = Math.min(elapsed / 2500, 1);
        const easeT = 1 - Math.pow(1 - t, 3);
        
        for (let i = 0; i < particlesCount * 3; i++) {
          positions[i] = shieldPos[i] + (randomPos[i] - shieldPos[i]) * easeT;
        }
        
        if (t === 1) {
          // Re-randomize field and velocities for fresh motion
          for(let i=0; i<particlesCount*3; i++) {
            randomPos[i] = (Math.random() - 0.5) * 120;
            velocities[i] = (Math.random() - 0.5) * 0.05;
          }
          state = 'RANDOM';
          particlesMesh.position.y = 0;
          particlesMesh.rotation.y = 0;
          lastStateChange = now;
        }
      }

      particlesGeometry.attributes.position.needsUpdate = true;
      renderer.render(scene, camera);
    };

    const handleResize = () => {
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    };

    window.addEventListener('resize', handleResize);
    animate();

    return () => {
      window.removeEventListener('resize', handleResize);
      renderer.dispose();
    };
  }, []);

  // Sync color with theme
  useEffect(() => {
    if (particlesMeshRef.current) {
      const color = isDark ? 0xbc13fe : 0xff0080;
      particlesMeshRef.current.material.color.setHex(color);
      particlesMeshRef.current.material.opacity = isDark ? 0.7 : 0.6;
    }
  }, [theme, isDark]);

  return (
    <canvas 
      ref={canvasRef} 
      style={{ 
        position: 'fixed', 
        top: 0, 
        left: 0, 
        zIndex: -1, 
        pointerEvents: 'none',
        background: isDark ? '#0a0a0c' : '#ffffff',
        transition: 'background 0.3s ease'
      }} 
    />
  );
};

export default Background;
