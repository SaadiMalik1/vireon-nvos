'use client';

import React, { useEffect, useRef, useState } from 'react';
import { useWebSocket } from '@/hooks/useWebSocket';

interface TimelineEvent {
  id: string;
  timestamp: number;
  type: 'SYSTEM_STATE' | 'ATTACK_DETECTED' | 'NISS_CRITICAL' | 'NISS_NOMINAL';
  details: string;
  severity: 'info' | 'warning' | 'critical' | 'success';
}

export function TimelinePanel() {
  const { data } = useWebSocket('telemetry');
  
  const [events, setEvents] = useState<TimelineEvent[]>([]);
  const [nissHistory, setNissHistory] = useState<{t: number, niss: number}[]>([]);
  
  // Ref to track previous state to detect transitions
  const prevState = useRef({
    active_dataset: '',
    active_attack: 'none',
    status: 'UNKNOWN'
  });

  useEffect(() => {
    if (!data) return;

    const newEvents: TimelineEvent[] = [];
    const prev = prevState.current;
    
    // Dataset Transition
    if (prev.active_dataset && prev.active_dataset !== data.active_dataset) {
      newEvents.push({
        id: `evt_${Date.now()}_ds`,
        timestamp: data.timestamp,
        type: 'SYSTEM_STATE',
        details: `Active dataset changed to: ${data.active_dataset}`,
        severity: 'info'
      });
    }

    // Attack Transition
    if (prev.active_attack !== data.active_attack) {
      if (data.active_attack !== 'none') {
        newEvents.push({
          id: `evt_${Date.now()}_atk_start`,
          timestamp: data.timestamp,
          type: 'ATTACK_DETECTED',
          details: `Payload Deployed: ${data.active_attack} (Intensity: ${(data.attack_intensity * 100).toFixed(0)}%)`,
          severity: 'critical'
        });
      } else {
        newEvents.push({
          id: `evt_${Date.now()}_atk_stop`,
          timestamp: data.timestamp,
          type: 'SYSTEM_STATE',
          details: `Attack Disengaged. Restoring nominal stream.`,
          severity: 'success'
        });
      }
    }

    // Status / NISS Transition
    if (prev.status !== data.status) {
      if (data.status === 'CRITICAL') {
        newEvents.push({
          id: `evt_${Date.now()}_stat_crit`,
          timestamp: data.timestamp,
          type: 'NISS_CRITICAL',
          details: `NISS Score dropped to CRITICAL level (${data.niss_score})`,
          severity: 'critical'
        });
      } else if (data.status === 'NOMINAL' && prev.status === 'CRITICAL') {
        newEvents.push({
          id: `evt_${Date.now()}_stat_nom`,
          timestamp: data.timestamp,
          type: 'NISS_NOMINAL',
          details: `NISS Score recovered to NOMINAL level (${data.niss_score})`,
          severity: 'success'
        });
      }
    }

    // Update refs
    prevState.current = {
      active_dataset: data.active_dataset,
      active_attack: data.active_attack,
      status: data.status
    };

    if (newEvents.length > 0) {
      setEvents(curr => {
        const next = [...newEvents, ...curr];
        return next.slice(0, 1000); // Keep max 1000 events
      });
    }
    
    // Update NISS History for the chart (keep last 60 seconds roughly -> 600 points at 10Hz)
    setNissHistory(curr => {
      const next = [...curr, { t: data.timestamp, niss: data.niss_score }];
      if (next.length > 600) return next.slice(next.length - 600);
      return next;
    });

  }, [data]);

  // Initial event on load
  useEffect(() => {
    setEvents([{
      id: `evt_startup`,
      timestamp: 0.00,
      type: 'SYSTEM_STATE',
      details: 'Timeline logger initialized. Listening for event bus broadcast...',
      severity: 'info'
    }]);
  }, []);

  return (
    <div className="flex flex-col w-full h-full bg-background overflow-hidden border rounded-md">
      {/* Header Chart */}
      <div className="h-48 border-b bg-black relative p-4 flex flex-col shrink-0">
        <div className="text-xs font-mono uppercase tracking-wider text-muted-foreground mb-2 z-10">
          Global NISS Score History (60s rolling)
        </div>
        <div className="flex-1 relative">
          <svg className="w-full h-full" preserveAspectRatio="none">
            {nissHistory.length > 1 && (
              <polyline 
                points={nissHistory.map((pt, i) => {
                  const x = (i / 600) * 100; // % width
                  const y = 100 - (pt.niss / 1000) * 100; // % height (0-1000 scale)
                  return `${x}%,${y}%`;
                }).join(' ')}
                fill="none"
                stroke="#22c55e"
                strokeWidth="2"
                vectorEffect="non-scaling-stroke"
              />
            )}
          </svg>
          <div className="absolute top-0 left-0 text-[10px] text-green-500/50">1000</div>
          <div className="absolute bottom-0 left-0 text-[10px] text-red-500/50">0</div>
        </div>
      </div>

      {/* Event Log Table */}
      <div className="flex-1 overflow-auto bg-card">
        <table className="w-full text-left text-sm whitespace-nowrap">
          <thead className="sticky top-0 bg-secondary shadow-sm text-muted-foreground uppercase text-xs font-mono">
            <tr>
              <th className="px-4 py-3 w-32">Timestamp</th>
              <th className="px-4 py-3 w-48">Type</th>
              <th className="px-4 py-3">Details</th>
            </tr>
          </thead>
          <tbody className="font-mono divide-y divide-border">
            {events.length === 0 && (
              <tr>
                <td colSpan={3} className="px-4 py-8 text-center text-muted-foreground italic">
                  Waiting for events...
                </td>
              </tr>
            )}
            {events.map((evt) => {
              let colorClass = 'text-foreground';
              if (evt.severity === 'critical') colorClass = 'text-red-500 font-bold bg-red-500/10';
              if (evt.severity === 'success') colorClass = 'text-green-500';
              if (evt.severity === 'warning') colorClass = 'text-orange-500';
              
              return (
                <tr key={evt.id} className={`${colorClass} hover:bg-accent/50 transition-colors`}>
                  <td className="px-4 py-2 opacity-70 border-r">{evt.timestamp.toFixed(2)}s</td>
                  <td className="px-4 py-2 border-r">{evt.type}</td>
                  <td className="px-4 py-2 truncate max-w-2xl">{evt.details}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
