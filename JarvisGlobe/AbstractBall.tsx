import * as THREE from 'three';
import { useEffect, useRef } from 'react';
import { gsap } from 'gsap';

const AbstractBall: React.FC<any> = ({
  perlinTime = 25.0,
  perlinMorph = 25.0,
  perlinDNoise = 0.0,
  chromaRGBr = 7.5,
  chromaRGBg = 5.0,
  chromaRGBb = 7.0,
  chromaRGBn = 1.0,
  chromaRGBm = 1.0,
  sphereWireframe = false,
  spherePoints = false,
  spherePsize = 1.0,
  cameraSpeedY = 0.0,
  cameraSpeedX = 0.0,
  cameraZoom = 150,
  cameraGuide = false,
}) => {
  const mountRef = useRef<HTMLDivElement>(null);
  const sceneRef = useRef<THREE.Scene | null>(null);
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const materialRef = useRef<THREE.ShaderMaterial | null>(null);
  const meshRef = useRef<THREE.Mesh | null>(null);
  const pointRef = useRef<THREE.Points | null>(null);
  const uniformsRef = useRef<any>({
    time: { value: 0.0 },
    RGBr: { value: chromaRGBr / 10 },
    RGBg: { value: chromaRGBg / 10 },
    RGBb: { value: chromaRGBb / 10 },
    RGBn: { value: chromaRGBn / 100 },
    RGBm: { value: chromaRGBm },
    morph: { value: perlinMorph },
    dnoise: { value: perlinDNoise },
    psize: { value: spherePsize }
  });

  useEffect(() => {
    const width = mountRef.current!.clientWidth;
    const height = mountRef.current!.clientHeight;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(20, width / height, 1, 1000);
    camera.position.set(0, 10, cameraZoom);

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(width, height);
    renderer.shadowMap.enabled = true;
    mountRef.current!.appendChild(renderer.domElement);

    const geometry = new THREE.IcosahedronGeometry(20, 20);

    const material = new THREE.ShaderMaterial({
      uniforms: uniformsRef.current,
      side: THREE.DoubleSide,
      vertexShader: document.getElementById('noiseVertexShader')!.textContent!,
      fragmentShader: document.getElementById('fragmentShader')!.textContent!,
      wireframe: sphereWireframe
    });

    const mesh = new THREE.Mesh(geometry, material);
    const point = new THREE.Points(geometry, material);

    mesh.castShadow = true;
    mesh.receiveShadow = true;
    mesh.geometry.morphTargetsRelative = true;

    scene.add(mesh);
    scene.add(point);

    let animationFrameId: number;

    const animate = () => {
        uniformsRef.current.time.value += perlinTime / 10000;
        uniformsRef.current.morph.value = perlinMorph;
        uniformsRef.current.dnoise.value = perlinDNoise;
      
      renderer.render(scene, camera);
      animationFrameId = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      cancelAnimationFrame(animationFrameId);
      renderer.dispose();
    };
  }, [perlinTime, perlinMorph, perlinDNoise, sphereWireframe]);

  return <div ref={mountRef} style={{ width: '100%', height: '100%' }} />;
};

export default AbstractBall;