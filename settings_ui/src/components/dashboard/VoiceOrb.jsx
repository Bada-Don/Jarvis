import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';
import { noiseVertexShader, fragmentShader } from './shaders';

const VoiceOrb = ({
    perlinTime = 25.0,
    perlinMorph = 25.0,
    perlinDNoise = 0.0,
    chromaRGBr = 7.5,
    chromaRGBg = 5.0,
    chromaRGBb = 7.0,
    chromaRGBn = 1.0,
    chromaRGBm = 1.0,
    sphereWireframe = false, // Not fully supported with shader material easily without tweaks, keeping for prop compat with caller
    spherePsize = 1.0,
    cameraZoom = 150,
}) => {
    const mountRef = useRef(null);
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

        const width = mountRef.current.clientWidth;
        const height = mountRef.current.clientHeight;

        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(20, width / height, 1, 1000);
        camera.position.set(0, 10, cameraZoom);

        const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        renderer.setSize(width, height);
        renderer.shadowMap.enabled = true;
        mountRef.current.appendChild(renderer.domElement);

        const geometry = new THREE.IcosahedronGeometry(20, 30); // increased density for smoother noise

        const material = new THREE.ShaderMaterial({
            uniforms: uniformsRef.current,
            side: THREE.DoubleSide,
            vertexShader: noiseVertexShader,
            fragmentShader: fragmentShader,
            wireframe: sphereWireframe
        });

        const mesh = new THREE.Mesh(geometry, material);
        mesh.castShadow = true;
        mesh.receiveShadow = true;
        // morphTargetsRelative is not needed for vertex displacement shader approach

        scene.add(mesh);

        let animationFrameId;

        const animate = () => {
            uniformsRef.current.time.value += perlinTime / 10000;
            uniformsRef.current.morph.value = perlinMorph;
            uniformsRef.current.dnoise.value = perlinDNoise;

            // Update other uniforms if props change
            uniformsRef.current.RGBr.value = chromaRGBr / 10;
            uniformsRef.current.RGBg.value = chromaRGBg / 10;
            uniformsRef.current.RGBb.value = chromaRGBb / 10;
            uniformsRef.current.RGBn.value = chromaRGBn / 100;
            uniformsRef.current.RGBm.value = chromaRGBm;
            uniformsRef.current.psize.value = spherePsize;

            mesh.rotation.y += 0.002;
            mesh.rotation.x += 0.001;

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

        return () => {
            window.removeEventListener('resize', handleResize);
            cancelAnimationFrame(animationFrameId);
            if (mountRef.current && renderer.domElement) {
                mountRef.current.removeChild(renderer.domElement);
            }
            renderer.dispose();
            geometry.dispose();
            material.dispose();
        };
    }, [
        perlinTime, perlinMorph, perlinDNoise, sphereWireframe,
        chromaRGBr, chromaRGBg, chromaRGBb, chromaRGBn, chromaRGBm, spherePsize, cameraZoom
    ]);

    return <div ref={mountRef} className="w-full h-full" />;
};

export default VoiceOrb;
