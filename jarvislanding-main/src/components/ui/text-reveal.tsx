"use client";

import React, { useRef } from "react";
import { motion, useScroll, useTransform } from "motion/react";
import { cn } from "@/lib/utils";

interface TextRevealProps {
  children: string;
  className?: string;
}

export function TextReveal({ children, className }: TextRevealProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start end", "end start"],
  });

  const words = children.split(" ");

  return (
    <div ref={containerRef} className={cn("relative z-0 min-h-[50vh]", className)}>
      <div className="sticky top-1/3 mx-auto flex max-w-4xl items-center px-4 py-20 justify-start">
        <p className="flex flex-wrap text-lg font-bold text-white/20 md:text-xl lg:text-2xl xl:text-3xl text-left">
          {words.map((word, i) => {
            const start = i / words.length;
            const end = start + 1 / words.length;
            return (
              <Word key={i} progress={scrollYProgress} range={[start * 0.5, end * 0.5 + 0.1]}>
                {word}
              </Word>
            );
          })}
        </p>
      </div>
    </div>
  );
}

interface WordProps {
  children: string;
  progress: any;
  range: [number, number];
}

function Word({ children, progress, range }: WordProps) {
  const opacity = useTransform(progress, range, [0, 1]);

  return (
    <span className="relative mx-1 lg:mx-2.5">
      <span className="absolute opacity-30">{children}</span>
      <motion.span style={{ opacity }} className="text-white">
        {children}
      </motion.span>
    </span>
  );
}
