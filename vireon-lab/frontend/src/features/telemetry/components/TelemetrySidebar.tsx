'use client';

import React from 'react';

interface ChannelStat {
  name: string;
  rms_uv: number;
  ptp_uv: number;
}

interface TelemetrySidebarProps {
  channels: string[];
  visibleChannels: boolean[];
  onToggleChannel: (index: number) => void;
  channelStats: ChannelStat[];
  verticalScale: number;
  onVerticalScaleChange: (scale: number) => void;
  activeDataset: string;
}

const SCALE_OPTIONS = [10, 25, 50, 100, 200, 500];

export function TelemetrySidebar({
  channels,
  visibleChannels,
  onToggleChannel,
  channelStats,
  verticalScale,
  onVerticalScaleChange,
  activeDataset
}: TelemetrySidebarProps) {
  return (
    <div className="w-64 border-l bg-card flex flex-col h-full overflow-hidden text-sm">
      <div className="p-4 border-b">
        <h3 className="font-semibold text-foreground mb-1 uppercase tracking-wider text-xs">Provider</h3>
        <div className="text-muted-foreground truncate">{activeDataset || 'Unknown'}</div>
      </div>

      <div className="p-4 border-b">
        <h3 className="font-semibold text-foreground mb-3 uppercase tracking-wider text-xs">Vertical Scale (µV)</h3>
        <select 
          className="w-full bg-background border rounded-md p-1.5 text-sm"
          value={verticalScale}
          onChange={(e) => onVerticalScaleChange(Number(e.target.value))}
        >
          {SCALE_OPTIONS.map(opt => (
            <option key={opt} value={opt}>{opt} µV / div</option>
          ))}
        </select>
      </div>

      <div className="flex-1 overflow-auto p-4">
        <div className="flex items-center justify-between mb-3">
          <h3 className="font-semibold text-foreground uppercase tracking-wider text-xs">Channels</h3>
          <span className="text-xs text-muted-foreground">{channels.length} Total</span>
        </div>
        
        <div className="space-y-2">
          {channels.map((ch, i) => {
            const stat = channelStats.find(s => s.name === ch);
            return (
              <div key={ch} className="flex flex-col gap-1 p-2 rounded-md border bg-background/50 hover:bg-accent transition-colors">
                <div className="flex items-center justify-between">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input 
                      type="checkbox"
                      checked={visibleChannels[i]}
                      onChange={() => onToggleChannel(i)}
                      className="rounded border-gray-600 text-primary focus:ring-primary"
                    />
                    <span className="font-mono font-bold text-foreground">{ch}</span>
                  </label>
                  {/* Fake impedance indicator */}
                  <div className={`w-2 h-2 rounded-full ${visibleChannels[i] ? 'bg-green-500' : 'bg-gray-600'}`} title="Impedance OK" />
                </div>
                
                {stat && (
                  <div className="flex justify-between text-xs text-muted-foreground mt-1">
                    <span>RMS: {stat.rms_uv.toFixed(1)}</span>
                    <span>PtP: {stat.ptp_uv.toFixed(1)}</span>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
