"use client";

import NavbarDemo from "@/components/resizable-navbar-demo";
import { FooterSection } from "@/components/footer-section";
import { BackgroundBeams } from "@/components/ui/background-beams";
import { MorphingText } from "@/components/ui/morphing-text";
import { GlowCard } from "@/components/ui/spotlight-card";
import { TextScramble } from "@/components/ui/text-scramble";
import { motion, useInView } from "framer-motion";
import { useRef } from "react";
import { 
  Zap, 
  Eye, 
  MessageSquare, 
  Shield, 
  Layers, 
  RefreshCw,
  Terminal,
  Cpu,
  Globe
} from "lucide-react";
import { PixelCanvas } from "@/components/ui/pixel-canvas";

function AnimatedFeatureCard({ 
  icon: Icon, 
  title, 
  description, 
  glowColor,
  delay = 0 
}: { 
  icon: React.ElementType; 
  title: string; 
  description: string; 
  glowColor: "blue" | "purple" | "green" | "orange";
  delay?: number;
}) {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-50px" });

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 30 }}
      animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 30 }}
      transition={{ duration: 0.5, delay }}
    >
      <GlowCard glowColor={glowColor} customSize className="p-6 h-full">
        <div className="flex flex-col h-full">
          <div className="w-12 h-12 rounded-lg bg-neutral-900 flex items-center justify-center mb-4">
            <Icon className="w-6 h-6 text-gray-400" />
          </div>
          <h3 className="text-white font-semibold text-lg mb-2">{title}</h3>
          <p className="text-gray-500 text-sm leading-relaxed">{description}</p>
        </div>
      </GlowCard>
    </motion.div>
  );
}

function StatCounter({ value, label }: { value: string; label: string }) {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });

  return (
    <div ref={ref} className="text-center">
      <TextScramble
        className="text-5xl md:text-6xl font-bold text-white"
        as="p"
        duration={1.5}
        speed={0.04}
        characterSet="0123456789+%"
        trigger={isInView}
      >
        {value}
      </TextScramble>
      <p className="text-gray-500 mt-2">{label}</p>
    </div>
  );
}

const coreFeatures = [
  {
    icon: MessageSquare,
    title: "Natural Language Commands",
    description: "Simply tell JARVIS what you want to do in plain English. No scripting, no complex syntax — just natural conversation.",
    glowColor: "blue" as const,
  },
  {
    icon: Eye,
    title: "Visual Intelligence",
    description: "Advanced computer vision identifies UI elements in real-time, adapting to any application or screen layout.",
    glowColor: "purple" as const,
  },
  {
    icon: Zap,
    title: "Lightning Fast Execution",
    description: "Optimized pipeline delivers sub-second response times for most actions, keeping your workflow smooth.",
    glowColor: "green" as const,
  },
  {
    icon: Shield,
    title: "Secure & Local",
    description: "Your automation runs locally on your machine. No sensitive data leaves your computer.",
    glowColor: "orange" as const,
  },
  {
    icon: Layers,
    title: "Multi-Step Workflows",
    description: "Chain complex sequences of actions together. JARVIS breaks down tasks into executable steps automatically.",
    glowColor: "blue" as const,
  },
  {
    icon: RefreshCw,
    title: "Self-Correcting",
    description: "Built-in error handling and retry logic ensures tasks complete successfully even when things don't go as planned.",
    glowColor: "purple" as const,
  },
];

const advancedCapabilities = [
  {
    icon: Terminal,
    title: "Cross-Application Control",
    description: "Seamlessly interact with any Windows application — browsers, IDEs, office suites, and more.",
    color: "#0ea5e9",
    pixelColors: ["#0c4a6e", "#0369a1", "#0ea5e9"],
  },
  {
    icon: Cpu,
    title: "Two-Model Architecture",
    description: "Specialized AI models for planning and vision work together for maximum accuracy.",
    color: "#a855f7",
    pixelColors: ["#581c87", "#7e22ce", "#a855f7"],
  },
  {
    icon: Globe,
    title: "Remote Access",
    description: "Control your computer from anywhere using the companion mobile app.",
    color: "#22c55e",
    pixelColors: ["#14532d", "#15803d", "#22c55e"],
  },
];


export default function FeaturesPage() {
  return (
    <main className="relative min-h-screen bg-black">
      <NavbarDemo />
      
      {/* Hero Section */}
      <section className="relative pt-40 pb-24 px-6 md:px-8 overflow-hidden">
        <div className="absolute inset-0">
          <BackgroundBeams className="opacity-20" />
        </div>
        <div className="relative z-10 container mx-auto max-w-5xl text-center">
          <MorphingText 
            texts={["Features", "Capabilities", "Power"]} 
            className="text-white mb-6"
          />
          <p className="text-xl text-gray-400 max-w-2xl mx-auto mt-10">
            Everything you need to automate your computer with the power of AI
          </p>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 px-6 md:px-8 border-y border-neutral-900">
        <div className="container mx-auto max-w-4xl">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            <StatCounter value="100+" label="Supported Apps" />
            <StatCounter value="5s" label="Avg Task Time" />
            <StatCounter value="95%" label="Accuracy Rate" />
            <StatCounter value="24/7" label="Availability" />
          </div>
        </div>
      </section>

      {/* Core Features Grid */}
      <section className="py-24 px-6 md:px-8 bg-gradient-to-b from-black via-neutral-950 to-black">
        <div className="container mx-auto max-w-6xl">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">Core Features</h2>
            <p className="text-gray-400 max-w-2xl mx-auto">
              Built from the ground up for intelligent automation
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {coreFeatures.map((feature, idx) => (
              <AnimatedFeatureCard
                key={feature.title}
                icon={feature.icon}
                title={feature.title}
                description={feature.description}
                glowColor={feature.glowColor}
                delay={idx * 0.1}
              />
            ))}
          </div>
        </div>
      </section>

      {/* How It Works Visual */}
      <section className="py-24 px-6 md:px-8 bg-black">
        <div className="container mx-auto max-w-5xl">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">How It Works</h2>
            <p className="text-gray-400">Three simple steps to automation</p>
          </div>
          
          <div className="relative">
            <div className="hidden md:block absolute top-1/2 left-0 right-0 h-px bg-gradient-to-r from-transparent via-neutral-800 to-transparent -translate-y-1/2" />
            
            <div className="grid md:grid-cols-3 gap-8 relative">
              {[
                { step: "01", title: "Speak", desc: "Tell JARVIS what you want to accomplish" },
                { step: "02", title: "Plan", desc: "AI breaks down your request into steps" },
                { step: "03", title: "Execute", desc: "Watch as JARVIS completes the task" },
              ].map((item, idx) => (
                <motion.div
                  key={item.step}
                  initial={{ opacity: 0, scale: 0.9 }}
                  whileInView={{ opacity: 1, scale: 1 }}
                  viewport={{ once: true }}
                  transition={{ delay: idx * 0.2 }}
                  className="relative bg-neutral-950 border border-neutral-900 rounded-2xl p-8 text-center"
                >
                  <div className="w-16 h-16 mx-auto mb-6 rounded-full bg-neutral-900 flex items-center justify-center">
                    <span className="text-2xl font-bold text-gray-500">{item.step}</span>
                  </div>
                  <h3 className="text-xl font-semibold text-white mb-2">{item.title}</h3>
                  <p className="text-gray-500">{item.desc}</p>
                </motion.div>
              ))}
            </div>
          </div>
        </div>
      </section>


      {/* Advanced Capabilities */}
      <section className="py-24 px-6 md:px-8 bg-gradient-to-b from-black to-neutral-950">
        <div className="container mx-auto max-w-5xl">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              Advanced Capabilities
            </h2>
            <p className="text-gray-400 max-w-2xl mx-auto">
              JARVIS goes beyond simple automation. With cutting-edge AI and a modular architecture, 
              it adapts to your unique workflow needs.
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-6">
            {advancedCapabilities.map((cap, idx) => (
              <motion.div
                key={cap.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: idx * 0.15 }}
              >
                <button 
                  className="group relative w-full overflow-hidden border border-neutral-800 rounded-[32px] aspect-square transition-colors duration-200 hover:border-[var(--active-color)] focus:outline-none"
                  style={{ "--active-color": cap.color } as React.CSSProperties}
                >
                  <PixelCanvas
                    gap={10}
                    speed={25}
                    colors={cap.pixelColors}
                    variant="icon"
                  />
                  <div className="relative z-10 h-full w-full flex flex-col items-center justify-center p-6">
                    <cap.icon className="w-16 h-16 text-gray-500 transition-all duration-300 ease-out group-hover:scale-110 group-hover:text-[var(--active-color)]" />
                    <h3 className="text-white font-semibold text-lg mt-4 mb-2">{cap.title}</h3>
                    <p className="text-gray-500 text-sm text-center">{cap.description}</p>
                  </div>
                </button>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 px-6 md:px-8 bg-black">
        <div className="container mx-auto max-w-3xl text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">
            Ready to Get Started?
          </h2>
          <p className="text-gray-400 mb-10">
            Download JARVIS today and experience the future of computer automation.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button className="px-8 py-3 bg-white text-black font-semibold rounded-full hover:bg-gray-200 transition-colors">
              Download Now
            </button>
            <button className="px-8 py-3 border border-neutral-700 text-white font-semibold rounded-full hover:bg-neutral-900 transition-colors">
              View Documentation
            </button>
          </div>
        </div>
      </section>

      <FooterSection />
    </main>
  );
}
