"use client";

import { ArrowUpRight } from "lucide-react";
import { BackgroundBeams } from "@/components/ui/background-beams";

export function FooterSection() {
  return (
    <footer className="relative bg-black text-white py-24 overflow-hidden">
      {/* Background Beams */}
      <div className="absolute inset-0 w-full h-full">
        <BackgroundBeams className="opacity-40 w-full h-full" />
      </div>
      <div className="relative z-10 container mx-auto px-6 md:px-8">
        {/* Big Brand Name */}
        <div className="text-center mb-5">
          <h2 className="text-7xl md:text-9xl lg:text-[12rem] font-bold tracking-tighter bg-gradient-to-b from-white to-gray-600 bg-clip-text text-transparent leading-none">
            J A R V I S
          </h2>
          <p className="text-gray-400 mt-6 text-lg max-w-xl mx-auto">
            Your AI-powered computer automation assistant. Control any application with natural language.
          </p>
        </div>

        {/* CTA Section */}
        <div className="text-center mb-20">
          <h3 className="text-2xl md:text-4xl font-bold mb-4">Ready to automate your workflow?</h3>

          <a
            href="/demo"
            className="inline-flex items-center gap-2 bg-white text-black px-8 py-4 rounded-full font-bold hover:bg-gray-200 transition-colors"
          >
            Test Drive JARVIS
            <ArrowUpRight className="w-5 h-5" />
          </a>
        </div>

        {/* Use Cases */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-16 text-center">
          <div className="p-4">
            <p className="text-gray-400 text-sm">General Automation</p>
            <p className="text-white text-xs mt-1">&quot;Open Notepad and write an essay&quot;</p>
          </div>
          <div className="p-4">
            <p className="text-gray-400 text-sm">Web Browsing</p>
            <p className="text-white text-xs mt-1">&quot;Go to youtube.com&quot;</p>
          </div>
          <div className="p-4">
            <p className="text-gray-400 text-sm">File Operations</p>
            <p className="text-white text-xs mt-1">&quot;Create a new folder on Desktop&quot;</p>
          </div>
          <div className="p-4">
            <p className="text-gray-400 text-sm">Professional Tasks</p>
            <p className="text-white text-xs mt-1">&quot;Design a number plate&quot;</p>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="border-t border-gray-800 pt-8 flex flex-col md:flex-row justify-between items-center gap-4">
          <p className="text-gray-500 text-sm">
            © 2025 JARVIS. Built for the future of automation.
          </p>
          <div className="flex gap-6 text-sm text-gray-500">
            <a href="#" className="hover:text-white transition-colors">Privacy Policy</a>
            <a href="#" className="hover:text-white transition-colors">Terms of Service</a>
            <a href="#" className="hover:text-white transition-colors">Documentation</a>
          </div>
        </div>
      </div>
    </footer>
  );
}
