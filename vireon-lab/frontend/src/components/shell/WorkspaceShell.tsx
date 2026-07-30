'use client';

import React, { useState } from 'react';
import { useWorkspaceStore } from '@/stores/workspaceStore';
import { Subsystem } from '@/lib/plugin-interface';

// We will inject the actual subsystems dynamically later
const mockSubsystems: Subsystem[] = [
  { id: 'validation', title: 'Validation Studio' },
  { id: 'dataset', title: 'Dataset Manager' },
  { id: 'telemetry', title: 'Live Telemetry' },
  { id: 'processing', title: 'Signal Processing' },
  { id: 'timeline', title: 'Timeline' },
  { id: 'attack', title: 'Attack Studio' },
];

export function WorkspaceShell({ children }: { children: React.ReactNode }) {
  const { activeSubsystemId, setActiveSubsystem, isSidebarOpen, toggleSidebar } = useWorkspaceStore();

  return (
    <div className="flex h-screen w-full bg-background text-foreground overflow-hidden">
      {/* Sidebar */}
      {isSidebarOpen && (
        <aside className="w-64 border-r bg-muted/40 p-4 flex flex-col gap-2">
          <div className="font-bold text-lg mb-4 tracking-tight">VIREON-Lab</div>
          <div className="space-y-1">
            {mockSubsystems.map(sub => (
              <button
                key={sub.id}
                onClick={() => setActiveSubsystem(sub.id)}
                className={`w-full text-left px-3 py-2 rounded-md transition-colors ${
                  activeSubsystemId === sub.id 
                    ? 'bg-primary text-primary-foreground' 
                    : 'hover:bg-accent hover:text-accent-foreground'
                }`}
              >
                {sub.title}
              </button>
            ))}
          </div>
        </aside>
      )}

      {/* Main Content Area (Docking System Placeholder) */}
      <main className="flex-1 flex flex-col overflow-hidden relative">
        <header className="h-12 border-b flex items-center px-4 justify-between bg-card">
          <button onClick={toggleSidebar} className="p-2 hover:bg-accent rounded-md">
            ☰
          </button>
          <div className="font-medium">
            {mockSubsystems.find(s => s.id === activeSubsystemId)?.title || 'Workspace'}
          </div>
        </header>
        
        <div className="flex-1 overflow-auto p-4 bg-background">
          {children}
        </div>
      </main>
    </div>
  );
}
