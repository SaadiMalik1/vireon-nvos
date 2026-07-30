'use client';

import React from 'react';

interface TelemetryMetricsProps {
  nissScore: number;
  status: string;
  activeAttack: string;
  attackIntensity: number;
  meanPowerUv2: number;
  bandPowers: Record<string, number>;
}

export function TelemetryMetrics({
  nissScore,
  status,
  activeAttack,
  attackIntensity,
  meanPowerUv2,
  bandPowers
}: TelemetryMetricsProps) {
  
  // Fake percentage for visual progress bars based on a max scale of ~100
  const getBandPercent = (val: number) => Math.min(100, Math.max(0, val));

  return (
    <div className="h-48 border-t bg-card flex flex-col">
      <div className="p-2 border-b bg-muted/20 flex items-center justify-between">
        <h3 className="font-semibold text-foreground uppercase tracking-wider text-xs">Runtime Metrics</h3>
      </div>
      
      <div className="flex-1 flex overflow-hidden">
        
        {/* NISS & Status */}
        <div className="w-64 border-r p-4 flex flex-col justify-center">
          <div className="text-sm text-muted-foreground uppercase tracking-wider mb-1">NISS Score</div>
          <div className="text-4xl font-mono font-bold tracking-tighter" style={{ color: nissScore < 500 ? '#ef4444' : '#22c55e'}}>
            {nissScore}
          </div>
          
          <div className="mt-4">
            <div className="text-xs text-muted-foreground uppercase tracking-wider mb-1">Status</div>
            <div className={`text-sm font-bold px-2 py-1 inline-block rounded-sm ${status === 'NOMINAL' ? 'bg-green-900/30 text-green-400' : 'bg-red-900/30 text-red-400'}`}>
              {status}
            </div>
          </div>
        </div>

        {/* Attack Info */}
        <div className="w-64 border-r p-4 flex flex-col justify-center">
          <div className="text-sm text-muted-foreground uppercase tracking-wider mb-1">Active Attack</div>
          <div className="text-lg font-bold text-foreground capitalize truncate">
            {activeAttack === 'none' ? 'None' : activeAttack.replace('_', ' ')}
          </div>
          
          <div className="mt-4">
            <div className="text-xs text-muted-foreground uppercase tracking-wider mb-1">Intensity</div>
            <div className="w-full bg-secondary h-2 rounded-full overflow-hidden">
              <div 
                className="h-full bg-red-500 transition-all duration-300"
                style={{ width: `${activeAttack === 'none' ? 0 : attackIntensity * 100}%` }}
              />
            </div>
          </div>
        </div>

        {/* Band Powers */}
        <div className="flex-1 p-4 flex flex-col justify-center">
          <div className="text-sm text-muted-foreground uppercase tracking-wider mb-3">Band Powers (Relative)</div>
          
          <div className="grid grid-cols-5 gap-4">
            {['delta', 'theta', 'alpha', 'beta', 'gamma'].map(band => (
              <div key={band} className="flex flex-col gap-1">
                <div className="flex justify-between text-xs">
                  <span className="uppercase text-muted-foreground font-semibold">{band}</span>
                  <span className="font-mono text-foreground">{bandPowers?.[band]?.toFixed(1) || '0.0'}</span>
                </div>
                <div className="w-full bg-secondary h-1.5 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-blue-500 transition-all duration-100"
                    style={{ width: `${getBandPercent(bandPowers?.[band] || 0)}%` }}
                  />
                </div>
              </div>
            ))}
          </div>

          <div className="mt-4 flex items-center justify-between">
            <div className="text-xs text-muted-foreground uppercase tracking-wider">Mean Power (µV²)</div>
            <div className="font-mono text-sm">{meanPowerUv2.toFixed(1)}</div>
          </div>
        </div>
      </div>
    </div>
  );
}
