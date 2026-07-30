import { create } from 'zustand';

interface WorkspaceState {
  activeSubsystemId: string | null;
  setActiveSubsystem: (id: string) => void;
  isSidebarOpen: boolean;
  toggleSidebar: () => void;
}

export const useWorkspaceStore = create<WorkspaceState>((set) => ({
  activeSubsystemId: null,
  setActiveSubsystem: (id) => set({ activeSubsystemId: id }),
  isSidebarOpen: true,
  toggleSidebar: () => set((state) => ({ isSidebarOpen: !state.isSidebarOpen })),
}));
