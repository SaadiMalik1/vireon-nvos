'use client';

import React, { useEffect, useState } from 'react';
import { useWebSocket } from '@/hooks/useWebSocket';

interface AttackMeta {
  id: string;
  name: string;
  description: string;
  default_intensity: number;
  category: string;
}

export function AttackStudioPanel() {
  const { data } = useWebSocket('telemetry'); // To track active attacks globally
  const [attacks, setAttacks] = useState<AttackMeta[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [executing, setExecuting] = useState(false);
  const [intensity, setIntensity] = useState<number>(1.0);

  useEffect(() => {
    fetch('http://localhost:8001/api/attacks')
      .then(res => res.json())
      .then(data => {
        setAttacks(data);
        if (data.length > 0) setSelectedId(data[0].id);
        setLoading(false);
      })
      .catch(err => {
        console.error("Failed to load attacks:", err);
        setLoading(false);
      });
  }, []);

  const handleSelect = (id: string) => {
    setSelectedId(id);
    const attack = attacks.find(a => a.id === id);
    if (attack) {
      setIntensity(attack.default_intensity);
    }
  };

  const handleExecute = async () => {
    if (!selectedId) return;
    setExecuting(true);
    try {
      await fetch('http://localhost:8001/api/attacks/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: selectedId, intensity }),
      });
    } catch (err) {
      console.error("Failed to execute attack:", err);
    }
    setExecuting(false);
  };

  const handleDisengage = async () => {
    setExecuting(true);
    try {
      await fetch('http://localhost:8001/api/attacks/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: "none", intensity: 0 }),
      });
    } catch (err) {
      console.error("Failed to disengage attack:", err);
    }
    setExecuting(false);
  };

  const selectedAttack = attacks.find(a => a.id === selectedId);
  const categories = Array.from(new Set(attacks.map(a => a.category)));
  const currentActiveAttack = data?.active_attack || 'none';

  if (loading) {
    return <div className="flex h-full items-center justify-center text-muted-foreground">Loading attack vectors...</div>;
  }

  return (
    <div className="flex w-full h-full bg-background overflow-hidden border rounded-md">
      {/* Sidebar List */}
      <div className="w-72 border-r bg-card flex flex-col">
        <div className="h-10 border-b flex items-center px-4 font-semibold text-sm shrink-0">
          Threat Vectors
        </div>
        <div className="flex-1 overflow-auto p-2">
          {categories.map(cat => (
            <div key={cat} className="mb-4">
              <div className="text-xs font-bold text-muted-foreground uppercase tracking-wider mb-2 px-2">
                {cat}
              </div>
              <div className="space-y-1">
                {attacks.filter(a => a.category === cat).map(a => (
                  <button
                    key={a.id}
                    onClick={() => handleSelect(a.id)}
                    className={`w-full text-left px-3 py-2 rounded-md text-sm transition-colors flex items-center justify-between ${
                      selectedId === a.id 
                        ? 'bg-primary text-primary-foreground' 
                        : 'hover:bg-accent hover:text-accent-foreground'
                    }`}
                  >
                    <span>{a.name}</span>
                    {currentActiveAttack === a.id && a.id !== 'none' && (
                      <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse"></span>
                    )}
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Main Details Panel */}
      <div className="flex-1 flex flex-col relative">
        <div className="h-10 border-b bg-card flex items-center px-4 font-semibold text-sm shrink-0 justify-between">
          <span>Attack Configuration</span>
          {currentActiveAttack !== 'none' && (
            <div className="flex items-center gap-2 text-red-500 text-xs font-bold tracking-wider uppercase">
              <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse"></span>
              Live Attack Detected: {currentActiveAttack}
            </div>
          )}
        </div>
        
        {selectedAttack ? (
          <div className="p-8 max-w-3xl">
            <h1 className="text-3xl font-bold mb-2 text-red-500">{selectedAttack.name}</h1>
            <div className="text-muted-foreground mb-8 text-lg">{selectedAttack.description}</div>
            
            {selectedAttack.id !== 'none' && (
              <div className="mb-8 p-6 border rounded-lg bg-card/50">
                <div className="flex justify-between items-center mb-4">
                  <div className="font-mono text-sm uppercase text-muted-foreground">Attack Intensity</div>
                  <div className="font-mono text-sm">{(intensity * 100).toFixed(0)}%</div>
                </div>
                <input 
                  type="range" 
                  min="0.1" 
                  max="1.0" 
                  step="0.05"
                  value={intensity}
                  onChange={(e) => setIntensity(parseFloat(e.target.value))}
                  className="w-full h-2 bg-secondary rounded-lg appearance-none cursor-pointer accent-red-500"
                />
                <div className="flex justify-between text-xs text-muted-foreground mt-2">
                  <span>Subtle (10%)</span>
                  <span>Maximum (100%)</span>
                </div>
              </div>
            )}

            <div className="pt-8 flex items-center gap-4">
              {selectedAttack.id !== 'none' ? (
                <button 
                  onClick={handleExecute}
                  disabled={executing}
                  className="bg-red-600 hover:bg-red-700 text-white px-6 py-3 rounded-md font-semibold text-lg transition-colors disabled:opacity-50"
                >
                  {executing ? 'Executing...' : 'Deploy Payload'}
                </button>
              ) : null}
              
              <button 
                onClick={handleDisengage}
                disabled={executing || currentActiveAttack === 'none'}
                className="bg-secondary hover:bg-secondary/80 text-secondary-foreground px-6 py-3 rounded-md font-semibold text-lg transition-colors disabled:opacity-50"
              >
                Disengage All
              </button>
            </div>
          </div>
        ) : (
          <div className="flex-1 flex items-center justify-center text-muted-foreground">
            Select a threat vector to configure
          </div>
        )}
      </div>
    </div>
  );
}
