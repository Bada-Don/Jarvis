"use client";

import { HoverEffect } from "@/components/ui/card-hover-effect";

const features = [
  {
    title: "Natural Language Commands",
    description:
      "Simply tell JARVIS what you want to do in plain English. No coding required - just speak naturally like 'Open Chrome and go to YouTube'.",
    link: "#",
  },
  {
    title: "Two-Model Pipeline",
    description:
      "Our Planner Model (Gemini Flash Lite) understands WHAT to do, while the Vision Mapper (Gemini 2.5 Flash) figures out WHERE to click. Smart separation for maximum accuracy.",
    link: "#",
  },
  {
    title: "Visual Element Detection",
    description:
      "FastSAM-powered Set-of-Mark technique identifies every UI element on screen. JARVIS sees your screen like you do and clicks the right buttons.",
    link: "#",
  },
  {
    title: "Cross-Application Automation",
    description:
      "Works across any Windows application without pre-configuration. From Notepad to Chrome to specialized software - JARVIS handles them all.",
    link: "#",
  },
  {
    title: "Real-Time Execution",
    description:
      "WebSocket-powered communication ensures instant response. Plan generation in 1-2 seconds, full task completion typically in 5-15 seconds.",
    link: "#",
  },
  {
    title: "Full Debug Traceability",
    description:
      "Every execution creates detailed logs with screenshots, annotated images, and step-by-step records. Diagnose issues instantly with complete transparency.",
    link: "#",
  },
];

export function CollaborationSection() {
  return (
<section id="collaboration" className="min-h-screen w-full bg-gradient-to-b from-black via-neutral-950 to-black py-20">
      <div className="container mx-auto px-6 md:px-8">
        <div className="text-center mb-12">
          <h2 className="text-3xl md:text-5xl font-bold text-white mb-4">
            Powerful Features
          </h2>
          <p className="text-gray-400 text-lg max-w-2xl mx-auto">
            Advanced AI capabilities that make computer automation accessible to everyone
          </p>
        </div>
        <HoverEffect items={features} className="w-full" />
      </div>
    </section>
  );
}
