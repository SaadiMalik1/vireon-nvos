'use client';

import React, { useEffect, useRef } from 'react';

interface EEGCanvasProps {
  waveform: number[][] | null;
  channels: string[];
  visibleChannels: boolean[];
  verticalScale: number; // e.g. 50uV per division
  timeScale: number; // e.g. 1.0 seconds across screen
}

export function EEGCanvas({ waveform, channels, visibleChannels, verticalScale, timeScale }: EEGCanvasProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const container = containerRef.current;
    if (!canvas || !container) return;

    // Handle high DPI displays
    const dpr = window.devicePixelRatio || 1;
    const rect = container.getBoundingClientRect();
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    ctx.scale(dpr, dpr);
    
    const width = rect.width;
    const height = rect.height;

    // Draw background
    ctx.fillStyle = '#09090b'; // Tailwind bg-background
    ctx.fillRect(0, 0, width, height);

    // Filter visible channels
    const activeIndices = channels
      .map((_, i) => i)
      .filter((i) => visibleChannels[i] !== false);
    
    const numVisible = activeIndices.length;
    if (numVisible === 0) {
      ctx.fillStyle = '#71717a';
      ctx.font = '14px monospace';
      ctx.fillText('No channels selected', width / 2 - 80, height / 2);
      return;
    }

    const trackHeight = height / numVisible;

    // Draw grid
    ctx.strokeStyle = '#27272a'; // Tailwind border
    ctx.lineWidth = 1;
    ctx.beginPath();
    // Horizontal track separators
    for (let i = 1; i < numVisible; i++) {
      ctx.moveTo(0, i * trackHeight);
      ctx.lineTo(width, i * trackHeight);
    }
    // Vertical time divisions (e.g. 10 divisions)
    for (let i = 1; i < 10; i++) {
      const x = (width / 10) * i;
      ctx.moveTo(x, 0);
      ctx.lineTo(x, height);
    }
    ctx.stroke();

    // Draw signals
    if (!waveform || waveform.length === 0) return;

    // Use a neon accent color
    ctx.strokeStyle = '#22c55e'; // Tailwind text-green-500
    ctx.lineWidth = 1.5;

    activeIndices.forEach((channelIdx, i) => {
      const channelData = waveform[channelIdx];
      if (!channelData || channelData.length === 0) return;

      const trackCenterY = (i * trackHeight) + (trackHeight / 2);
      
      // We want to scale the signal so that `verticalScale` (uV) maps to half a track height
      // So if signal = verticalScale, it goes up to trackHeight / 2
      const scaleFactor = (trackHeight / 2) / verticalScale;
      const stepX = width / (channelData.length - 1);

      ctx.beginPath();
      for (let j = 0; j < channelData.length; j++) {
        const val = channelData[j];
        const x = j * stepX;
        // Invert Y because canvas Y grows downwards, but positive voltage goes UP
        const y = trackCenterY - (val * scaleFactor);

        if (j === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      ctx.stroke();

      // Draw Channel Label
      ctx.fillStyle = '#a1a1aa'; // Tailwind text-muted-foreground
      ctx.font = '12px monospace';
      ctx.fillText(channels[channelIdx], 10, i * trackHeight + 20);
    });

  }, [waveform, channels, visibleChannels, verticalScale, timeScale]);

  return (
    <div ref={containerRef} className="w-full h-full relative overflow-hidden bg-background border rounded-md">
      <canvas
        ref={canvasRef}
        className="w-full h-full block"
        style={{ width: '100%', height: '100%' }}
      />
    </div>
  );
}
