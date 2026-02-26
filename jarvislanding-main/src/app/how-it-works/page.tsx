"use client";

import NavbarDemo from "@/components/resizable-navbar-demo";
import { FooterSection } from "@/components/footer-section";
import { BackgroundBeams } from "@/components/ui/background-beams";
import { LayoutTextFlip } from "@/components/ui/layout-text-flip";
import { GlowCard } from "@/components/ui/spotlight-card";
import { TextScramble } from "@/components/ui/text-scramble";
import { MermaidChart } from "@/components/ui/mermaid-chart";
import { motion, useInView } from "framer-motion";
import { useRef } from "react";
import { 
  Eye, 
  Monitor
} from "lucide-react";

// Main Pipeline Flowchart
const mainPipelineChart = `
flowchart LR
    A[User Command] --> B[Planner Model]
    B --> C[Execution Plan]
    C --> D[Local Client]
    D --> E{Step Type?}
    E -->|Keyboard| F[Direct Execution]
    E -->|Visual Click| G[Vision Pipeline]
    G --> H[Screenshot + FastSAM]
    H --> I[Vision Mapper]
    I --> J[Click Coordinates]
    F --> K[Task Complete]
    J --> K
`;

// Sequence Diagram
const sequenceDiagramChart = `
sequenceDiagram
    participant User
    participant Backend
    participant Planner as Planner Model<br/>(Gemini Flash Lite)
    participant Client as Local Client
    participant PC as Windows PC

    User->>Backend: "Open Chrome and go to google.com"
    Backend->>Planner: Generate execution plan
    Planner-->>Backend: JSON sequence of steps
    Backend->>Client: WebSocket: execute_plan
    
    loop For each step
        alt Keyboard Step
            Client->>PC: pyautogui keyboard action
        else Visual Click Step
            Client->>Client: Screenshot + FastSAM SoM
            Client->>Planner: Annotated image + targets
            Planner-->>Client: Target → Element ID mapping
            Client->>PC: Click at element center
        end
    end
    
    Client-->>User: Task complete
`;

// Vision Pipeline Flowchart
const visionPipelineChart = `
flowchart TD
    A[Plan Received] --> B{Has Visual Clicks?}
    B -->|No| C[Execute Keyboard Steps]
    B -->|Yes| D[Collect All Visual Targets]
    D --> E[Take Screenshot]
    E --> F[Run FastSAM SoM]
    F --> G[Call Vision Mapper Once]
    G --> H[Cache ID Map + Box Map]
    H --> I[Execute All Steps]
    I --> J{Step Type}
    J -->|Keyboard| K[pyautogui.press/write]
    J -->|Visual Click| L[Lookup cached coordinates]
    L --> M[pyautogui.click]
`;

// Execution Modes Flowchart
const executionModesChart = `
flowchart LR
    A[Execution Plan] --> B{Mode?}
    B -->|Vision| C[Screenshot-based]
    B -->|Direct| D[UIA-based]
    
    C --> E[FastSAM + Gemini Vision]
    C --> F[Click by coordinates]
    
    D --> G[Windows UI Automation]
    D --> H[Direct element access]
`;

// Architecture Diagram
const architectureChart = `
flowchart TB
    subgraph Frontend
        A[React Native Mobile App]
    end
    
    subgraph Backend[Backend Server]
        B[Flask + SocketIO]
        C[Gemini Flash Lite<br/>Planner Model]
    end
    
    subgraph LocalClient[Local Client]
        D[Python WebSocket Client]
        E[FastSAM<br/>UI Detection]
        F[Gemini 2.5 Flash<br/>Vision Mapper]
        G[pyautogui<br/>Mouse/Keyboard]
    end
    
    A <-->|HTTP/WebSocket| B
    B --> C
    B <-->|WebSocket| D
    D --> E
    D --> F
    D --> G
`;


// Step Card Component
function StepCard({ 
  number, 
  title, 
  description, 
  details,
  color,
  delay = 0 
}: { 
  number: string;
  title: string;
  description: string;
  details?: string[];
  color: "blue" | "purple" | "green" | "orange";
  delay?: number;
}) {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-50px" });

  const colorClasses = {
    blue: "border-blue-500/30 hover:border-blue-500/60",
    purple: "border-purple-500/30 hover:border-purple-500/60",
    green: "border-green-500/30 hover:border-green-500/60",
    orange: "border-orange-500/30 hover:border-orange-500/60",
  };

  const numberColors = {
    blue: "text-blue-400",
    purple: "text-purple-400",
    green: "text-green-400",
    orange: "text-orange-400",
  };

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 30 }}
      animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 30 }}
      transition={{ duration: 0.5, delay }}
      className={`bg-neutral-950 border ${colorClasses[color]} rounded-2xl p-6 transition-colors`}
    >
      <div className="flex items-start gap-4">
        <div className={`text-4xl font-bold ${numberColors[color]} opacity-50`}>{number}</div>
        <div className="flex-1">
          <h3 className="text-white font-semibold text-lg mb-2">{title}</h3>
          <p className="text-gray-400 text-sm mb-4">{description}</p>
          {details && (
            <ul className="space-y-2">
              {details.map((detail, idx) => (
                <li key={idx} className="text-gray-500 text-xs flex items-start gap-2">
                  <span className={`${numberColors[color]} mt-1`}>•</span>
                  {detail}
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </motion.div>
  );
}

export default function HowItWorksPage() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });

  return (
    <main className="relative min-h-screen bg-black">
      <NavbarDemo />
      
      {/* Hero Section */}
      <section className="relative pt-40 pb-24 px-6 md:px-8 overflow-hidden">
        <div className="absolute inset-0">
          <BackgroundBeams className="opacity-20" />
        </div>
        <div className="relative z-10 container mx-auto max-w-5xl text-center">
          <div className="flex flex-col items-center justify-center gap-4 sm:flex-row mb-6">
            <LayoutTextFlip
              text="Discover "
              words={["How It Works", "The Pipeline", "Under The Hood"]}
              duration={3000}
            />
          </div>
          <p className="text-xl text-gray-400 max-w-2xl mx-auto mt-10">
            A deep dive into JARVIS&apos;s Two-Model Pipeline architecture
          </p>
        </div>
      </section>

      {/* Overview Stats */}
      <section className="py-12 px-6 md:px-8 border-y border-neutral-900">
        <div className="container mx-auto max-w-4xl">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            <div ref={ref}>
              <TextScramble
                className="text-3xl font-bold text-white"
                as="p"
                duration={1.2}
                speed={0.05}
                characterSet="0123456789"
                trigger={isInView}
              >
                2
              </TextScramble>
              <p className="text-gray-500 text-sm mt-1">AI Models</p>
            </div>
            <div>
              <TextScramble
                className="text-3xl font-bold text-white"
                as="p"
                duration={1.2}
                speed={0.05}
                characterSet="0123456789ms"
                trigger={isInView}
              >
                1-2s
              </TextScramble>
              <p className="text-gray-500 text-sm mt-1">Plan Generation</p>
            </div>
            <div>
              <TextScramble
                className="text-3xl font-bold text-white"
                as="p"
                duration={1.2}
                speed={0.05}
                characterSet="0123456789ms-"
                trigger={isInView}
              >
                3-5s
              </TextScramble>
              <p className="text-gray-500 text-sm mt-1">Vision Pass</p>
            </div>
            <div>
              <TextScramble
                className="text-3xl font-bold text-white"
                as="p"
                duration={1.2}
                speed={0.05}
                characterSet="0123456789.s"
                trigger={isInView}
              >
                0.3s
              </TextScramble>
              <p className="text-gray-500 text-sm mt-1">Per Step</p>
            </div>
          </div>
        </div>
      </section>


      {/* Main Pipeline Flowchart */}
      <section className="py-24 px-6 md:px-8 bg-gradient-to-b from-black via-neutral-950 to-black">
        <div className="container mx-auto max-w-6xl">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">Main Pipeline</h2>
            <p className="text-gray-400 max-w-2xl mx-auto">
              From natural language command to task completion
            </p>
          </div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="bg-neutral-950 border border-neutral-800 rounded-2xl p-8 overflow-x-auto"
          >
            <MermaidChart chart={mainPipelineChart} className="flex justify-center" />
          </motion.div>
        </div>
      </section>

      {/* Two Model Explanation */}
      <section className="py-24 px-6 md:px-8 bg-black">
        <div className="container mx-auto max-w-5xl">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">Two-Model Architecture</h2>
            <p className="text-gray-400 max-w-2xl mx-auto">
              Separating task planning from visual execution for maximum accuracy
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 gap-8">
            <StepCard
              number="01"
              title="Planner Model (Gemini Flash Lite)"
              description="Understands WHAT to do — converts natural language into structured execution plans."
              details={[
                "Supports General and FlexiSIGN modes",
                "Outputs JSON sequence of steps",
                "Handles keyboard and visual click actions",
                "~1-2 seconds response time"
              ]}
              color="purple"
              delay={0}
            />
            <StepCard
              number="02"
              title="Vision Mapper (Gemini 2.5 Flash)"
              description="Understands WHERE to click — identifies UI elements in annotated screenshots."
              details={[
                "Uses Set-of-Mark (SoM) technique",
                "FastSAM detects all UI elements",
                "Returns element ID mappings",
                "Single-pass for efficiency"
              ]}
              color="blue"
              delay={0.1}
            />
          </div>
        </div>
      </section>

      {/* Sequence Diagram */}
      <section className="py-24 px-6 md:px-8 bg-gradient-to-b from-black via-neutral-950 to-black">
        <div className="container mx-auto max-w-6xl">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">Communication Flow</h2>
            <p className="text-gray-400 max-w-2xl mx-auto">
              How components interact during task execution
            </p>
          </div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="bg-neutral-950 border border-neutral-800 rounded-2xl p-8 overflow-x-auto"
          >
            <MermaidChart chart={sequenceDiagramChart} className="flex justify-center" />
          </motion.div>
        </div>
      </section>

      {/* Architecture Diagram */}
      <section className="py-24 px-6 md:px-8 bg-black">
        <div className="container mx-auto max-w-5xl">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">System Architecture</h2>
            <p className="text-gray-400 max-w-2xl mx-auto">
              How the components communicate and work together
            </p>
          </div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="bg-neutral-950 border border-neutral-800 rounded-2xl p-8 overflow-x-auto"
          >
            <MermaidChart chart={architectureChart} className="flex justify-center" />
          </motion.div>
        </div>
      </section>


      {/* Vision Pipeline */}
      <section className="py-24 px-6 md:px-8 bg-gradient-to-b from-black via-neutral-950 to-black">
        <div className="container mx-auto max-w-5xl">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">Single-Pass Vision Pipeline</h2>
            <p className="text-gray-400 max-w-2xl mx-auto">
              Efficient visual processing with caching for multi-step tasks
            </p>
          </div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="bg-neutral-950 border border-neutral-800 rounded-2xl p-8 overflow-x-auto"
          >
            <MermaidChart chart={visionPipelineChart} className="flex justify-center" />
          </motion.div>
        </div>
      </section>

      {/* Execution Modes */}
      <section className="py-24 px-6 md:px-8 bg-black">
        <div className="container mx-auto max-w-5xl">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">Execution Modes</h2>
            <p className="text-gray-400 max-w-2xl mx-auto">
              Two strategies for different scenarios
            </p>
          </div>
          
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="bg-neutral-950 border border-neutral-800 rounded-2xl p-8 overflow-x-auto mb-8"
          >
            <MermaidChart chart={executionModesChart} className="flex justify-center" />
          </motion.div>
          
          <div className="grid md:grid-cols-2 gap-8">
            <GlowCard glowColor="purple" customSize className="p-8">
              <div>
                <div className="flex items-center gap-3 mb-4">
                  <Eye className="w-8 h-8 text-purple-400" />
                  <h3 className="text-white font-semibold text-xl">Vision Mode</h3>
                </div>
                <p className="text-gray-400 mb-4">Screenshot-based automation using FastSAM + Gemini Vision</p>
                <div className="space-y-2">
                  <p className="text-gray-500 text-sm">✓ Works with any application</p>
                  <p className="text-gray-500 text-sm">✓ No pre-configuration needed</p>
                  <p className="text-gray-500 text-sm">✓ Adapts to UI changes</p>
                </div>
              </div>
            </GlowCard>
            
            <GlowCard glowColor="green" customSize className="p-8">
              <div>
                <div className="flex items-center gap-3 mb-4">
                  <Monitor className="w-8 h-8 text-green-400" />
                  <h3 className="text-white font-semibold text-xl">Direct Mode</h3>
                </div>
                <p className="text-gray-400 mb-4">Windows UI Automation for known applications</p>
                <div className="space-y-2">
                  <p className="text-gray-500 text-sm">✓ Faster execution</p>
                  <p className="text-gray-500 text-sm">✓ More reliable</p>
                  <p className="text-gray-500 text-sm">✓ Direct element access</p>
                </div>
              </div>
            </GlowCard>
          </div>
        </div>
      </section>

      {/* JSON Output Example */}
      <section className="py-24 px-6 md:px-8 bg-gradient-to-b from-black to-neutral-950">
        <div className="container mx-auto max-w-4xl">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">Planner Output Format</h2>
            <p className="text-gray-400 max-w-2xl mx-auto">
              Structured JSON execution plans
            </p>
          </div>
          
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="bg-[#171717] border border-[#737373] rounded-lg p-6 overflow-x-auto font-mono"
          >
            <div className="flex items-center gap-2 mb-4 pb-2 border-b border-green-500/20">
              <div className="w-3 h-3 rounded-full bg-red-500"></div>
              <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
              <div className="w-3 h-3 rounded-full bg-green-500"></div>
              <span className="text-green-400 text-sm ml-2">planner_output.json</span>
            </div>
<pre className="text-sm font-mono">
              <span className="text-green-500">$</span> <span className="text-white">cat planner_output.json</span>
              {"\n"}
{`{
  `}<span className="text-cyan-400">"mode"</span>{`: `}<span className="text-yellow-300">"general"</span>{`,
  `}<span className="text-cyan-400">"sequence"</span>{`: [
    {
      `}<span className="text-cyan-400">"order"</span>{`: `}<span className="text-purple-400">1</span>{`, `}<span className="text-cyan-400">"type"</span>{`: `}<span className="text-yellow-300">"keyboard"</span>{`, `}<span className="text-cyan-400">"value"</span>{`: `}<span className="text-yellow-300">"win"</span>{`, `}<span className="text-cyan-400">"desc"</span>{`: `}<span className="text-yellow-300">"Open Start menu"</span>{`
    },
    {
      `}<span className="text-cyan-400">"order"</span>{`: `}<span className="text-purple-400">2</span>{`, `}<span className="text-cyan-400">"type"</span>{`: `}<span className="text-yellow-300">"keyboard"</span>{`, `}<span className="text-cyan-400">"value"</span>{`: `}<span className="text-yellow-300">"chrome"</span>{`, `}<span className="text-cyan-400">"desc"</span>{`: `}<span className="text-yellow-300">"Type app name"</span>{`
    },
    {
      `}<span className="text-cyan-400">"order"</span>{`: `}<span className="text-purple-400">3</span>{`, `}<span className="text-cyan-400">"type"</span>{`: `}<span className="text-yellow-300">"keyboard"</span>{`, `}<span className="text-cyan-400">"value"</span>{`: `}<span className="text-yellow-300">"enter"</span>{`, `}<span className="text-cyan-400">"desc"</span>{`: `}<span className="text-yellow-300">"Launch"</span>{`
    },
    {
      `}<span className="text-cyan-400">"order"</span>{`: `}<span className="text-purple-400">4</span>{`, `}<span className="text-cyan-400">"type"</span>{`: `}<span className="text-yellow-300">"visual_click"</span>{`, `}<span className="text-cyan-400">"target_name"</span>{`: `}<span className="text-yellow-300">"address_bar"</span>{`, `}<span className="text-cyan-400">"desc"</span>{`: `}<span className="text-yellow-300">"Click URL bar"</span>{`
    }
  ]
}`}
            </pre>
          </motion.div>
        </div>
      </section>

      <FooterSection />
    </main>
  );
}
