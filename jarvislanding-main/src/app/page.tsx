import NavbarDemo from "@/components/resizable-navbar-demo";
import { Hero } from "@/components/ui/hero-1";
import { AboutSection } from "@/components/about-section";
import { CollaborationSection } from "@/components/collaboration-section";
import { FooterSection } from "@/components/footer-section";
import { Highlighter } from "@/components/ui/highlighter";

export default function Home() {
  return (
    <main className="relative min-h-screen">
      <NavbarDemo />
      <Hero
        title={
          <>
            Your{" "}
            <Highlighter action="highlight" color="#404040" isView>
              AI Computer
            </Highlighter>{" "}
            <Highlighter action="underline" color="#18181b" isView>
              Automation Assistant
            </Highlighter>
          </>
        }
        subtitle="Control your computer with natural language. Just say what you want, and JARVIS handles the clicks, keystrokes, and navigation for you."
        eyebrow="AI-Powered Automation"
        ctaLabel="Test Drive JARVIS"
        ctaHref="/demo"
      />
      <AboutSection />
      <CollaborationSection />
      <FooterSection />
    </main>
  );
}
