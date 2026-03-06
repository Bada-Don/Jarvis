"use client";

import JarvisDemoPortal from "@/components/JarvisDemoPortal";
import NavbarDemo from "@/components/resizable-navbar-demo";
import { FooterSection } from "@/components/footer-section";

export default function DemoPage() {
    return (
        <main className="relative min-h-screen bg-black">
            <NavbarDemo />
            <div className="pt-24 pb-12 w-full">
                <div className="mb-8 text-center">
                    <h2 className="text-3xl font-extrabold tracking-tighter sm:text-4xl md:text-5xl lg:text-6xl bg-clip-text text-transparent bg-gradient-to-b from-white to-zinc-500">
                        EXPERIENCE JARVIS
                    </h2>
                    <p className="mt-4 text-zinc-400 max-w-2xl mx-auto uppercase tracking-[0.2em] text-xs">
                        Direct interface to the EC2 Puppet Engine. Neural link established.
                    </p>
                </div>

                <JarvisDemoPortal />
            </div>
            <FooterSection />
        </main>
    );
}
