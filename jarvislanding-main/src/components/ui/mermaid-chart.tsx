"use client";

import { useEffect, useRef, useState } from "react";
import mermaid from "mermaid";

interface MermaidChartProps {
  chart: string;
  className?: string;
}

export function MermaidChart({ chart, className = "" }: MermaidChartProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [svg, setSvg] = useState<string>("");

  useEffect(() => {
    mermaid.initialize({
      startOnLoad: false,
      theme: "dark",
      themeVariables: {
        primaryColor: "#171717",
        primaryTextColor: "#ffffff",
        primaryBorderColor: "#525252",
        lineColor: "#525252",
        secondaryColor: "#171717",
        tertiaryColor: "#262626",
        background: "#000000",
        mainBkg: "#171717",
        secondBkg: "#171717",
        nodeBorder: "#525252",
        clusterBkg: "#171717",
        clusterBorder: "#525252",
        titleColor: "#ffffff",
        edgeLabelBackground: "#171717",
        nodeTextColor: "#ffffff",
      },
      flowchart: {
        htmlLabels: true,
        curve: "basis",
        nodeSpacing: 50,
        rankSpacing: 50,
        padding: 15,
      },
      sequence: {
        actorMargin: 50,
        boxMargin: 10,
        boxTextMargin: 5,
        noteMargin: 10,
        messageMargin: 35,
      },
    });

    const renderChart = async () => {
      if (containerRef.current) {
        try {
          const id = `mermaid-${Math.random().toString(36).substr(2, 9)}`;
          const { svg } = await mermaid.render(id, chart);
          setSvg(svg);
        } catch (error) {
          console.error("Mermaid rendering error:", error);
        }
      }
    };

    renderChart();
  }, [chart]);

  return (
    <div
      ref={containerRef}
      className={`mermaid-container ${className}`}
      dangerouslySetInnerHTML={{ __html: svg }}
    />
  );
}
