'use client';

import React, { useState } from 'react';
import { useWebSocket } from '@/hooks/useWebSocket';
import { EEGCanvas } from './EEGCanvas';
import { TelemetrySidebar } from './TelemetrySidebar';
import { TelemetryMetrics } from './TelemetryMetrics';

export function LiveTelemetryPanel() {
  const { data, isConnected } = useWebSocket('telemetry');
  
  // Local UI State
  const [verticalScale, setVerticalScale] = useState(50);
  const [visibleChannels, setVisibleChannels] = useState<boolean[]>(Array(8).fill(true)); // Assuming 8 channels

  const handleToggleChannel = (index: number) => {
    setVisibleChannels(prev => {
      const next = [...prev];
      next[index] = !next[index];
      return next;
    });
  };

  // Safe defaults if data is not yet available
  const channels = data?.channels || ['CH1', 'CH2', 'CH3', 'CH4', 'CH5', 'CH6', 'CH7', 'CH8'];
  const channelStats = data?.channel_stats || [];
  
  return (
    <div className="flex w-full h-full bg-background overflow-hidden border rounded-md">
      {/* Sidebar for Controls */}
      <TelemetrySidebar 
        channels={channels}
        visibleChannels={visibleChannels}
        onToggleChannel={handleToggleChannel}
        channelStats={channelStats}
        verticalScale={verticalScale}
        onVerticalScaleChange={setVerticalScale}
        activeDataset={data?.active_dataset || 'Waiting...'}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col h-full overflow-hidden">
        
        {/* Status Header */}
        <div className="h-10 border-b bg-card flex items-center justify-between px-4 shrink-0">
          <div className="flex items-center gap-4">
            <span className="font-semibold text-sm">Real-time Stream</span>
            <div className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`} />
              <span className="text-xs text-muted-foreground uppercase tracking-wider">{isConnected ? 'Live' : 'Offline'}</span>
            </div>
          </div>
          <div className="text-xs text-muted-foreground font-mono">
            {data ? `T=${data.timestamp.toFixed(2)}s` : 'T=0.00s'}
          </div>
        </div>

        {/* Oscilloscope Canvas */}
        <div className="flex-1 p-2 bg-black relative">
          {!isConnected && !data && (
            <div className="absolute inset-0 flex items-center justify-center z-10 text-muted-foreground text-sm uppercase tracking-widest bg-black/50">
              Connecting to Telemetry Broker...
            </div>
          )}
          <EEGCanvas 
            waveform={data?.waveform || null}
            channels={channels}
            visibleChannels={visibleChannels}
            verticalScale={verticalScale}
            timeScale={1.0}
          />
        </div>

        {/* Metrics Panel */}
        <div className="shrink-0">
          <TelemetryMetrics 
            nissScore={data?.niss_score || 815}
            status={data?.status || 'UNKNOWN'}
            activeAttack={data?.active_attack || 'none'}
            attackIntensity={data?.attack_intensity || 0}
            meanPowerUv2={data?.mean_power_uv2 || 0}
            bandPowers={data?.band_powers || {}}
          />
        </div>
      </div>
    </div>
  );
}
