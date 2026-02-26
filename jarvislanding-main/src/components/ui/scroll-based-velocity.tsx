"use client";

import React, { useRef } from "react";
import { motion, useAnimationFrame, useMotionValue } from "motion/react";
import { cn } from "@/lib/utils";

interface ScrollVelocityContainerProps {
  children: React.ReactNode;
  className?: string;
}

export function ScrollVelocityContainer({
  children,
  className,
}: ScrollVelocityContainerProps) {
  return (
    <div className={cn("flex flex-col gap-4 overflow-hidden", className)}>
      {children}
    </div>
  );
}

interface ScrollVelocityRowProps {
  children: React.ReactNode;
  baseVelocity?: number;
  direction?: 1 | -1;
  className?: string;
}

function wrap(min: number, max: number, v: number) {
  const rangeSize = max - min;
  return ((((v - min) % rangeSize) + rangeSize) % rangeSize) + min;
}

export function ScrollVelocityRow({
  children,
  baseVelocity = 5,
  direction = 1,
  className,
}: ScrollVelocityRowProps) {
  const baseX = useMotionValue(0);

  const directionFactor = useRef<number>(direction);

  useAnimationFrame((t, delta) => {
    const moveBy = directionFactor.current * baseVelocity * (delta / 1000);
    baseX.set(baseX.get() + moveBy);
  });

  return (
    <div className="overflow-hidden whitespace-nowrap flex flex-nowrap">
      <motion.div
        className={cn("flex whitespace-nowrap flex-nowrap gap-8", className)}
        style={{ x: useMotionValue(0) }}
        animate={{ x: direction === 1 ? [0, -1000] : [-1000, 0] }}
        transition={{
          x: {
            repeat: Infinity,
            repeatType: "loop",
            duration: 20,
            ease: "linear",
          },
        }}
      >
        {[...Array(8)].map((_, i) => (
          <span key={i} className="block">
            {children}
          </span>
        ))}
      </motion.div>
    </div>
  );
}
