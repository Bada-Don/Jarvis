"use client";

import NavbarDemo from "@/components/resizable-navbar-demo";
import { FooterSection } from "@/components/footer-section";
import { BackgroundBeams } from "@/components/ui/background-beams";
import { MorphingText } from "@/components/ui/morphing-text";
import { GlowCard } from "@/components/ui/spotlight-card";
import TechStackListing, { TechItem } from "@/components/ui/tech-stack-listing";
import Image from "next/image";
import { TextScramble } from "@/components/ui/text-scramble";
import { useInView } from "framer-motion";
import { useRef } from "react";

function PerformanceStat({ value, label, color }: { value: string; label: string; color: string }) {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });

  return (
    <div ref={ref}>
      <TextScramble
        className={`text-4xl font-bold ${color}`}
        as="p"
        duration={1.2}
        speed={0.05}
        characterSet="0123456789.-s"
        trigger={isInView}
      >
        {value}
      </TextScramble>
      <p className="text-gray-500">{label}</p>
    </div>
  );
}

const techStack: TechItem[] = [
  {
    name: "Gemini AI",
    category: "Planner & Vision",
    logo: <Image src="/icons/gemini.png" alt="Gemini" width={24} height={24} />,
    description: "Google's advanced multimodal AI models power both the planning and vision components of JARVIS.",
    details: "Uses Gemini Flash Lite for fast plan generation and Gemini 2.5 Flash for accurate visual element identification with Set-of-Mark technique.",
    useCase: "Converts natural language commands into structured execution plans and identifies UI elements in screenshots.",
  },
  {
    name: "FastSAM",
    category: "UI Detection",
    logo: <Image src="/icons/python.png" alt="Python" width={24} height={24} />,
    description: "Fast Segment Anything Model for real-time UI element detection and segmentation.",
    details: "Ultralytics implementation that detects all UI elements on screen and draws numbered red boxes for the Set-of-Mark annotation technique.",
    useCase: "Creates annotated screenshots with numbered elements that the Vision Mapper can reference for precise clicking.",
  },
  {
    name: "React Native",
    category: "Mobile App",
    logo: <Image src="/icons/react.png" alt="React" width={24} height={24} />,
    description: "Cross-platform mobile framework for building the JARVIS companion app.",
    details: "Built with Expo for rapid development. Provides the user interface for sending voice/text commands to control your computer remotely.",
    useCase: "Mobile interface that lets users send natural language commands to JARVIS from anywhere.",
  },
  {
    name: "Flask",
    category: "Backend Server",
    logo: <Image src="/icons/flask.png" alt="Flask" width={24} height={24} />,
    description: "Lightweight Python web framework serving as the API gateway and WebSocket hub.",
    details: "Flask with Flask-SocketIO handles HTTP requests and real-time bidirectional communication between the mobile app and local client.",
    useCase: "Routes commands from mobile app to the Planner Model and coordinates execution with the local client.",
  },
  {
    name: "WebSocket",
    category: "Real-time Comm",
    logo: <Image src="/icons/socket .png" alt="Socket" width={24} height={24} />,
    description: "Bidirectional communication protocol for instant command execution and status updates.",
    details: "Enables real-time streaming of execution plans, status updates, and completion notifications between all system components.",
    useCase: "Ensures immediate response when you send a command and live feedback during task execution.",
  },
  {
    name: "Python",
    category: "Automation",
    logo: <Image src="/icons/python.png" alt="Python" width={24} height={24} />,
    description: "Python library for programmatic control of mouse and keyboard on Windows.",
    details: "Combined with pywin32 for Windows-specific automation. Executes clicks at precise coordinates and types keyboard input.",
    useCase: "Performs the actual mouse clicks and keyboard actions on your computer based on the execution plan.",
  },
];

export default function AboutPage() {
  return (
    <main className="relative min-h-screen bg-black">
      <NavbarDemo />
      
      {/* Hero Section */}
      <section className="relative pt-40 pb-20 px-6 md:px-8">
        <div className="absolute inset-0">
          <BackgroundBeams className="opacity-30" />
        </div>
        <div className="relative z-10 container mx-auto max-w-4xl text-center">
          <MorphingText 
            texts={["About", "JARVIS"]} 
            className="text-white mb-6"
          />
          <p className="text-xl text-gray-400 max-w-3xl mx-auto mt-10">
            Bridging the gap between natural language and precise computer automation
          </p>
        </div>
      </section>

      {/* Problem Section */}
<section className="py-20 px-6 md:px-8 bg-gradient-to-b from-black via-neutral-950 to-black">
        <div className="container mx-auto max-w-4xl">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-8">The Problem</h2>
          <p className="text-gray-400 text-lg mb-6">
            Modern computer automation faces a fundamental challenge: bridging the gap between natural language commands and precise UI interactions. Traditional automation tools require explicit scripting with exact coordinates or element identifiers, making them brittle and inaccessible to non-technical users.
          </p>
          <div className="grid md:grid-cols-2 gap-6 mt-10">
            <GlowCard glowColor="blue" customSize className="p-6 h-auto aspect-auto">
              <div>
                <h3 className="text-white font-semibold mb-2">Natural Language Ambiguity</h3>
                <p className="text-gray-500">Users express tasks in varied, informal ways like &quot;open notepad and type hello&quot;</p>
              </div>
            </GlowCard>
            <GlowCard glowColor="purple" customSize className="p-6 h-auto aspect-auto">
              <div>
                <h3 className="text-white font-semibold mb-2">Dynamic UI Elements</h3>
                <p className="text-gray-500">Screen layouts change based on resolution, themes, and application state</p>
              </div>
            </GlowCard>
            <GlowCard glowColor="green" customSize className="p-6 h-auto aspect-auto">
              <div>
                <h3 className="text-white font-semibold mb-2">Visual Element Identification</h3>
                <p className="text-gray-500">Clicking the right button requires understanding visual context</p>
              </div>
            </GlowCard>
            <GlowCard glowColor="orange" customSize className="p-6 h-auto aspect-auto">
              <div>
                <h3 className="text-white font-semibold mb-2">Cross-Application Automation</h3>
                <p className="text-gray-500">Different apps have different UI patterns and interaction models</p>
              </div>
            </GlowCard>
          </div>
        </div>
      </section>

      {/* Solution Section */}
      <section className="py-20 px-6 md:px-8 bg-black">
        <div className="container mx-auto max-w-4xl">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-8">Our Solution</h2>
          <p className="text-gray-400 text-lg mb-10">
            JARVIS implements a <span className="text-white font-semibold">Two-Model Pipeline</span> architecture that separates task planning from visual execution. This separation allows each model to specialize, improving accuracy and maintainability.
          </p>
          
          <div className="space-y-8">
            <div className="flex gap-6 items-start">
              <div className="w-12 h-12 rounded-full bg-[#171717] flex items-center justify-center flex-shrink-0">
                <span className="text-gray-500 font-bold">1</span>
              </div>
              <div>
                <h3 className="text-white font-semibold text-xl mb-2">Planner Model (Gemini Flash Lite)</h3>
                <p className="text-gray-400">Understands WHAT to do — converts natural language into structured execution plans with keyboard and visual click steps.</p>
              </div>
            </div>
            
            <div className="flex gap-6 items-start">
              <div className="w-12 h-12 rounded-full bg-[#171717] flex items-center justify-center flex-shrink-0">
                <span className="text-gray-500 font-bold">2</span>
              </div>
              <div>
                <h3 className="text-white font-semibold text-xl mb-2">Vision Mapper (Gemini 2.5 Flash)</h3>
                <p className="text-gray-400">Understands WHERE to click — uses FastSAM Set-of-Mark technique to identify UI elements in annotated screenshots.</p>
              </div>
            </div>
            
            <div className="flex gap-6 items-start">
              <div className="w-12 h-12 rounded-full bg-[#171717] flex items-center justify-center flex-shrink-0">
                <span className="text-gray-500 font-bold">3</span>
              </div>
              <div>
                <h3 className="text-white font-semibold text-xl mb-2">Local Execution Client</h3>
                <p className="text-gray-400">Executes the plan using pyautogui for mouse/keyboard control with real-time WebSocket communication.</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Tech Stack Section */}
      <section className="py-20 px-6 md:px-8 bg-gradient-to-b from-black via-neutral-950 to-black">
        <div className="container mx-auto max-w-4xl">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-10 text-center">Technology Stack</h2>
          <p className="text-gray-400 text-center mb-8">Click on any technology to learn more about how it powers JARVIS</p>
          <TechStackListing items={techStack} />
        </div>
      </section>

      {/* Performance Section */}
      <section className="py-20 px-6 md:px-8 bg-black">
        <div className="container mx-auto max-w-4xl text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-10">Performance</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            <PerformanceStat value="1-2s" label="Plan Generation" color="text-gray-400" />
            <PerformanceStat value="3-5s" label="Vision Pass" color="text-gray-400" />
            <PerformanceStat value="0.3s" label="Per Step" color="text-gray-400" />
            <PerformanceStat value="5-15s" label="Total Task" color="text-gray-400" />
          </div>
        </div>
      </section>

      <FooterSection />
    </main>
  );
}
