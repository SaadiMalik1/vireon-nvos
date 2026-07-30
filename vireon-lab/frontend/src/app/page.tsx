'use client';

import { WorkspaceShell } from "@/components/shell/WorkspaceShell";
import { useWorkspaceStore } from "@/stores/workspaceStore";
import { LiveTelemetryPanel } from "@/features/telemetry/components/LiveTelemetryPanel";
import { DatasetManagerPanel } from "@/features/datasets/components/DatasetManagerPanel";
import { AttackStudioPanel } from "@/features/attacks/components/AttackStudioPanel";
import { TimelinePanel } from "@/features/timeline/components/TimelinePanel";
import { SignalProcessingPanel } from "@/features/processing/components/SignalProcessingPanel";
import { ValidationPanel } from "@/features/validation/components/ValidationPanel";

export default function Home() {
  const { activeSubsystemId } = useWorkspaceStore();

  return (
    <WorkspaceShell>
      {activeSubsystemId === 'validation' ? (
        <ValidationPanel />
      ) : activeSubsystemId === 'telemetry' ? (
        <LiveTelemetryPanel />
      ) : activeSubsystemId === 'dataset' ? (
        <DatasetManagerPanel />
      ) : activeSubsystemId === 'processing' ? (
        <SignalProcessingPanel />
      ) : activeSubsystemId === 'attack' ? (
        <AttackStudioPanel />
      ) : activeSubsystemId === 'timeline' ? (
        <TimelinePanel />
      ) : (
        <div className="flex h-full items-center justify-center text-muted-foreground">
          Select a subsystem from the sidebar to begin.
        </div>
      )}
    </WorkspaceShell>
  );
}
