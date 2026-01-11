import React, { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { gsap } from 'gsap';
import { motion } from 'framer-motion';
import { noiseVertexShader, fragmentShader } from './shaders';
import { StatusDisplay } from './StatusDisplay';

const globConfig = {
    perlinTime: 50.0,
    perlinDNoise: 0.0,
    chromaRGBr: 255,
    chromaRGBg: 255,
    chromaRGBb: 255,
    chromaRGBn: 255,
    chromaRGBm: 255,
    sphereWireframe: true,
    spherePoints: true,
    spherePsize: 0.3,
    cameraSpeedY: 0.0,
    cameraSpeedX: 0.0,
    cameraZoom: 170,
    cameraGuide: false,
    perlinMorph: 5.5,
};

// Internal AbstractBall logic adapted to React component
const AbstractBall = ({
    perlinTime = 50.0,
    perlinMorph = 25.0,
    perlinDNoise = 2.5,
    chromaRGBr = 255,
    chromaRGBg = 255,
    chromaRGBb = 255,
    chromaRGBn = 255,
    chromaRGBm = 255,
    sphereWireframe = false,
    spherePoints = false,
    spherePsize = 1.0,
    cameraSpeedY = 0.0,
    cameraSpeedX = 0.0,
    cameraZoom = 175,
}) => {
    const mountRef = useRef(null);
    const sceneRef = useRef(null);
    const cameraRef = useRef(null);
    const rendererRef = useRef(null);
    const materialRef = useRef(null);
    const meshRef = useRef(null);
    const pointRef = useRef(null);
    const uniformsRef = useRef({
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
        if (!mountRef.current) return;

        // Cleanup any existing children to prevent duplicates
        while (mountRef.current.firstChild) {
            mountRef.current.removeChild(mountRef.current.firstChild);
        }

        const width = mountRef.current.clientWidth;
        const height = mountRef.current.clientHeight;

        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(20, width / height, 1, 1000);
        camera.position.set(0, 10, cameraZoom);

        const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        renderer.setSize(width, height);
        renderer.shadowMap.enabled = true;
        mountRef.current.appendChild(renderer.domElement);

        const geometry = new THREE.IcosahedronGeometry(20, 20);

        const material = new THREE.ShaderMaterial({
            uniforms: uniformsRef.current,
            side: THREE.DoubleSide,
            vertexShader: noiseVertexShader,
            fragmentShader: fragmentShader,
            wireframe: sphereWireframe
        });

        const mesh = new THREE.Mesh(geometry, material);
        const point = new THREE.Points(geometry, material);

        mesh.castShadow = true;
        mesh.receiveShadow = true;
        mesh.geometry.morphTargetsRelative = true;

        scene.add(mesh);
        scene.add(point);

        let animationFrameId;

        const animate = () => {
            uniformsRef.current.time.value += perlinTime / 10000;
            uniformsRef.current.morph.value = perlinMorph;
            uniformsRef.current.dnoise.value = perlinDNoise;

            uniformsRef.current.RGBr.value = chromaRGBr / 10;
            uniformsRef.current.RGBg.value = chromaRGBg / 10;
            uniformsRef.current.RGBb.value = chromaRGBb / 10;
            uniformsRef.current.RGBn.value = chromaRGBn / 100;
            uniformsRef.current.RGBm.value = chromaRGBm;
            uniformsRef.current.psize.value = spherePsize;

            mesh.rotation.y += cameraSpeedY / 100;
            mesh.rotation.z += cameraSpeedX / 100;
            point.rotation.y = mesh.rotation.y;
            point.rotation.z = mesh.rotation.z;

            // Toggle visibility based on props
            material.wireframe = sphereWireframe;
            mesh.visible = !spherePoints;
            point.visible = spherePoints;

            camera.lookAt(scene.position);
            renderer.render(scene, camera);
            animationFrameId = requestAnimationFrame(animate);
        };

        animate();

        const handleResize = () => {
            if (!mountRef.current) return;
            const width = mountRef.current.clientWidth;
            const height = mountRef.current.clientHeight;
            renderer.setSize(width, height);
            camera.aspect = width / height;
            camera.updateProjectionMatrix();
        };

        window.addEventListener('resize', handleResize);

        sceneRef.current = scene;
        cameraRef.current = camera;

        return () => {
            window.removeEventListener('resize', handleResize);
            cancelAnimationFrame(animationFrameId);
            // Strict cleanup
            if (mountRef.current) {
                while (mountRef.current.firstChild) {
                    mountRef.current.removeChild(mountRef.current.firstChild);
                }
            }
            renderer.dispose();
            geometry.dispose();
            material.dispose();
        };
    }, [
        sphereWireframe, spherePoints
        // Trigger re-init only if structural props change
    ]);

    // GSAP Animations
    useEffect(() => {
        if (cameraRef.current) {
            gsap.to(cameraRef.current.position, {
                duration: 2,
                z: 300 - cameraZoom
            });
        }
        gsap.to(uniformsRef.current.RGBr, { duration: 1, value: Math.random() * 10 });
        gsap.to(uniformsRef.current.RGBg, { duration: 1, value: Math.random() * 10 });
        gsap.to(uniformsRef.current.RGBb, { duration: 1, value: Math.random() * 10 });
        gsap.to(uniformsRef.current.RGBn, { duration: 1, value: Math.random() * 2 });
        gsap.to(uniformsRef.current.RGBm, { duration: 1, value: Math.random() * 5 });
    }, [cameraZoom]);

    return <div ref={mountRef} className="w-full h-full min-h-[400px]" />;
};

const VoiceOrb = ({ isListening }) => {
    const [config, setConfig] = useState(globConfig);

    useEffect(() => {
        if (isListening) {
            setConfig({
                ...globConfig,
                perlinTime: 20.0,
                perlinMorph: 25.0,
            });
        } else {
            setConfig({
                ...globConfig,
            });
        }
    }, [isListening]);

    return (
        <div className="relative w-full h-full flex flex-col justify-center items-center">
            <motion.div
                layout
                transition={{ duration: 0.5, ease: "easeInOut" }}
                className="w-full flex justify-center items-center h-full"
            >
                <div style={{ width: '100%', height: '100%', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
                    <AbstractBall {...config} />
                </div>
            </motion.div>

            <StatusDisplay status={isListening ? "Listening..." : "Idle"} />
        </div>
    );
};

export default VoiceOrb;
