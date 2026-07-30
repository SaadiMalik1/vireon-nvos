'use client';

import React, { useState, useEffect, useRef } from 'react';
import { useWebSocket } from '@/hooks/useWebSocket';

// -------------------------------------------------------------
// UI Sub-components
// -------------------------------------------------------------

function FilterToggle({ label, desc, enabled, onChange, isOffline }: { label: string, desc: string, enabled: boolean, onChange: (val: boolean) => void, isOffline?: boolean }) {
  return (
    <div className="flex items-start space-x-3 p-3 bg-card border rounded-md mb-2">
      <div className="flex-1">
        <div className="flex items-center space-x-2">
          <div className="text-sm font-medium text-foreground">{label}</div>
          {isOffline && <span className="px-1.5 py-0.5 rounded text-[10px] bg-amber-500/10 text-amber-500 font-mono">OFFLINE</span>}
        </div>
        <div className="text-xs text-muted-foreground">{desc}</div>
      </div>
      <button 
        type="button"
        onClick={() => onChange(!enabled)}
        className={`relative inline-flex h-5 w-9 shrink-0 cursor-pointer items-center justify-center rounded-full transition-colors duration-200 ease-in-out focus:outline-none ${enabled ? 'bg-primary' : 'bg-secondary'}`}
      >
        <span
          className={`pointer-events-none inline-block h-4 w-4 transform rounded-full bg-background shadow ring-0 transition duration-200 ease-in-out ${enabled ? 'translate-x-2' : '-translate-x-2'}`}
        />
      </button>
    </div>
  );
}

// -------------------------------------------------------------
// Canvas Drawers
// -------------------------------------------------------------
function drawSpectrum(canvas: HTMLCanvasElement, freqs: number[], psd: number[]) {
  const ctx = canvas.getContext('2d');
  if (!ctx) return;
  
  const width = canvas.width;
  const height = canvas.height;
  
  ctx.clearRect(0, 0, width, height);
  if (!freqs || freqs.length === 0) return;
  
  const maxFreq = 60.0; 
  const maxPsd = Math.max(...psd) * 1.1; 
  
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
  ctx.lineWidth = 1;
  ctx.beginPath();
  for (let f = 0; f <= maxFreq; f += 10) {
    const x = (f / maxFreq) * width;
    ctx.moveTo(x, 0);
    ctx.lineTo(x, height);
  }
  ctx.stroke();

  ctx.beginPath();
  ctx.strokeStyle = '#22c55e'; // Green
  ctx.lineWidth = 2;
  
  let started = false;
  for (let i = 0; i < freqs.length; i++) {
    const f = freqs[i];
    if (f > maxFreq) break;
    
    const p = psd[i];
    const x = (f / maxFreq) * width;
    const y = height - ((p / maxPsd) * height);
    
    if (!started) {
      ctx.moveTo(x, y);
      started = true;
    } else {
      ctx.lineTo(x, y);
    }
  }
  ctx.stroke();
  
  ctx.lineTo(width, height);
  ctx.lineTo(0, height);
  ctx.closePath();
  ctx.fillStyle = 'rgba(34, 197, 94, 0.1)';
  ctx.fill();
}

function drawWaveform(canvas: HTMLCanvasElement, raw: number[][], processed: number[][], mode: 'RAW' | 'PROCESSED' | 'DIFFERENCE') {
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    const width = canvas.width;
    const height = canvas.height;
    
    ctx.clearRect(0, 0, width, height);
    if (!raw || raw.length === 0 || !raw[0]) return;
    
    const channelToDraw = 0; // We just draw channel 1 for visualization
    const raw_ch = raw[channelToDraw];
    const proc_ch = (processed && processed[channelToDraw]) ? processed[channelToDraw] : raw_ch;
    
    let targetData: number[] = [];
    if (mode === 'RAW') targetData = raw_ch;
    else if (mode === 'PROCESSED') targetData = proc_ch;
    else if (mode === 'DIFFERENCE') {
        targetData = raw_ch.map((v, i) => v - proc_ch[i]);
    }
    
    const yCenter = height / 2;
    const yScale = 0.5; // Scale to fit
    
    ctx.beginPath();
    ctx.strokeStyle = mode === 'DIFFERENCE' ? '#ef4444' : '#3b82f6';
    ctx.lineWidth = 2;
    
    for (let i = 0; i < targetData.length; i++) {
        const x = (i / targetData.length) * width;
        const y = yCenter - (targetData[i] * yScale);
        
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
    }
    ctx.stroke();
}


// -------------------------------------------------------------
// Main Component
// -------------------------------------------------------------
export function SignalProcessingPanel() {
  const { data: spectralData } = useWebSocket('spectral');
  const { data: rawData } = useWebSocket('eeg_raw');
  const { data: processedData } = useWebSocket('eeg_processed');
  
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const waveCanvasRef = useRef<HTMLCanvasElement>(null);
  
  const [viewMode, setViewMode] = useState<'RAW' | 'PROCESSED' | 'DIFFERENCE'>('PROCESSED');
  
  const [config, setConfig] = useState<any>({
    notch: { enabled: false },
    bandpass: { enabled: false },
    artifact: { method: "none" },
    spectral: { method: "welch" }
  });
  
  const [provenance, setProvenance] = useState<any>(null);

  useEffect(() => {
    fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'}/processing/config`)
      .then(res => res.json())
      .then(data => setConfig(data))
      .catch(err => console.error("Failed to load processing config", err));
  }, []);

  const updateConfig = (section: string, key: string, value: any) => {
    const newConfig = { ...config, [section]: { ...config[section], [key]: value } };
    setConfig(newConfig);
    
    fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'}/processing/config`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(newConfig)
    }).catch(err => console.error("Failed to update config", err));
  };

  useEffect(() => {
    if (spectralData && spectralData.freqs && spectralData.psd && canvasRef.current) {
      drawSpectrum(canvasRef.current, spectralData.freqs, spectralData.psd);
      if (spectralData.provenance) setProvenance(spectralData.provenance);
    }
  }, [spectralData]);

  useEffect(() => {
    if (rawData && rawData.waveform && processedData && processedData.waveform && waveCanvasRef.current) {
        drawWaveform(waveCanvasRef.current, rawData.waveform, processedData.waveform, viewMode);
    }
  }, [rawData, processedData, viewMode]);

  const bandPowers = spectralData?.band_powers || { Delta: 0, Theta: 0, Alpha: 0, Beta: 0, Gamma: 0 };

  return (
    <div className="flex w-full h-full bg-background overflow-hidden">
      
      {/* Left Sidebar: Filter Controls */}
      <div className="w-80 border-r flex flex-col bg-sidebar">
        <div className="p-4 border-b">
          <h2 className="text-sm font-semibold uppercase tracking-wider text-sidebar-foreground">Digital Filters</h2>
        </div>
        <div className="p-4 flex-1 overflow-y-auto space-y-4">
          <FilterToggle 
            label="50/60 Hz Notch Filter" 
            desc="Suppresses AC mains powerline interference." 
            enabled={config.notch.enabled} 
            onChange={(v) => updateConfig("notch", "enabled", v)} 
          />
          <FilterToggle 
            label="1-50 Hz Bandpass" 
            desc="Removes DC offset and high-frequency noise." 
            enabled={config.bandpass.enabled} 
            onChange={(v) => updateConfig("bandpass", "enabled", v)} 
          />
          <FilterToggle 
            label="ICA Artifact Removal" 
            desc="Automated eye blink (EOG) and muscle (EMG) suppression." 
            enabled={config.artifact.method === "ica"} 
            onChange={(v) => updateConfig("artifact", "method", v ? "ica" : "none")} 
            isOffline={true}
          />
          
          {/* Provenance Readout */}
          <div className="mt-8 pt-4 border-t">
            <h3 className="text-xs font-semibold text-muted-foreground mb-2">DSP Engine Status (Provenance)</h3>
            <div className="space-y-1 text-xs font-mono">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Backend:</span>
                <span className="text-foreground text-green-400">SciPy.Signal</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">PSD Method:</span>
                <span className="text-foreground">Welch's Method</span>
              </div>
              {provenance && (
                <>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Mode:</span>
                  <span className="text-foreground uppercase">{provenance.processing_mode}</span>
                </div>
                <div className="flex justify-between mt-2 pt-2 border-t border-border/50">
                  <span className="text-muted-foreground">Rev Hash:</span>
                  <span className="text-muted-foreground truncate w-24 text-right" title={provenance.config_hash}>
                    {provenance.config_hash.substring(0, 8)}
                  </span>
                </div>
                </>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Main Area: Split Viewer */}
      <div className="flex-1 flex flex-col p-8 space-y-6">
          
        {/* Top: Waveform Viewer */}
        <div className="flex flex-col h-1/3">
            <div className="mb-2 flex justify-between items-center">
                <h2 className="text-lg font-bold tracking-tight">Signal Inspection</h2>
                <div className="flex space-x-1 bg-secondary rounded-lg p-1">
                    <button onClick={() => setViewMode('RAW')} className={`px-3 py-1 text-xs font-semibold rounded-md ${viewMode === 'RAW' ? 'bg-background shadow' : 'text-muted-foreground'}`}>RAW</button>
                    <button onClick={() => setViewMode('PROCESSED')} className={`px-3 py-1 text-xs font-semibold rounded-md ${viewMode === 'PROCESSED' ? 'bg-background shadow' : 'text-muted-foreground'}`}>PROCESSED</button>
                    <button onClick={() => setViewMode('DIFFERENCE')} className={`px-3 py-1 text-xs font-semibold rounded-md ${viewMode === 'DIFFERENCE' ? 'bg-background shadow text-red-500' : 'text-muted-foreground'}`}>DIFFERENCE</button>
                </div>
            </div>
            <div className="flex-1 bg-black border rounded-lg p-4 relative">
                <div className="absolute top-4 right-6 flex items-center space-x-2 z-10 text-xs font-mono">
                    <span className={viewMode === 'DIFFERENCE' ? 'text-red-500' : 'text-blue-500'}>■</span>
                    <span className="text-muted-foreground">Ch 1 (uV)</span>
                </div>
                <canvas ref={waveCanvasRef} width={800} height={200} className="w-full h-full" style={{ width: '100%', height: '100%' }} />
            </div>
        </div>
          
        {/* Bottom: Spectrum Analyzer */}
        <div className="flex flex-col flex-1">
            <div className="mb-2 flex justify-between items-end">
                <div>
                    <h1 className="text-lg font-bold tracking-tight">Spectral Analysis (PSD)</h1>
                </div>
                <div className="flex space-x-4">
                    {Object.entries(bandPowers).map(([band, pwr]: [string, any]) => (
                        <div key={band} className="bg-card border px-3 py-1 rounded-md flex flex-col items-center">
                        <span className="text-[10px] text-muted-foreground uppercase">{band}</span>
                        <span className="font-mono text-sm">{Number(pwr).toFixed(1)}</span>
                        </div>
                    ))}
                </div>
            </div>
            
            <div className="flex-1 bg-black border rounded-lg p-4 relative flex flex-col">
                <div className="absolute top-4 right-6 flex items-center space-x-2 z-10 text-xs font-mono">
                    <span className="text-green-500">■</span>
                    <span className="text-muted-foreground">Power Spectral Density (uV^2/Hz)</span>
                </div>
                <div className="flex-1 w-full relative">
                    <canvas ref={canvasRef} width={800} height={300} className="w-full h-full" style={{ width: '100%', height: '100%' }} />
                    <div className="absolute bottom-0 left-0 w-full flex justify-between text-[10px] text-muted-foreground font-mono pointer-events-none px-1">
                        <span>0 Hz</span><span>10 Hz</span><span>20 Hz</span><span>30 Hz</span><span>40 Hz</span><span>50 Hz</span><span>60 Hz</span>
                    </div>
                </div>
            </div>
        </div>
        
      </div>

    </div>
  );
}
