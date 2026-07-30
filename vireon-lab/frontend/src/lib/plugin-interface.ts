import React from 'react';

export interface Command {
  id: string;
  label: string;
  action: () => void;
  shortcut?: string[];
}

export interface DockablePanel {
  id: string;
  title: string;
  component: React.ComponentType<any>;
  defaultPosition?: 'left' | 'right' | 'bottom' | 'main';
}

export interface Subsystem {
  id: string;
  title: string;
  icon?: React.ComponentType<any>;
  routes?: string[];
  commands?: Command[];
  websocketChannels?: string[];
  permissions?: string[];
  dockablePanels?: DockablePanel[];
}
