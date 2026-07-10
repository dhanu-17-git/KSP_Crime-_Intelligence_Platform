import React, { createContext, useContext, useState } from 'react';
import type { ReactNode } from 'react';
import type { FIR, Suspect, Vehicle } from '../services/mockDb';

export interface ToastMessage {
  id: string;
  message: string;
  type: 'success' | 'info' | 'error' | 'warn';
}

interface AppContextType {
  language: 'en' | 'kn';
  setLanguage: (lang: 'en' | 'kn') => void;
  sidebarCollapsed: boolean;
  setSidebarCollapsed: (collapsed: boolean) => void;
  aiQuery: string;
  setAiQuery: (query: string) => void;
  selectedFir: FIR | null;
  setSelectedFir: (fir: FIR | null) => void;
  selectedSuspect: Suspect | null;
  setSelectedSuspect: (suspect: Suspect | null) => void;
  selectedVehicle: Vehicle | null;
  setSelectedVehicle: (vehicle: Vehicle | null) => void;
  
  // Refined Global Filters & Alerts
  selectedDistrictId: string;
  setSelectedDistrictId: (id: string) => void;
  toasts: ToastMessage[];
  addToast: (message: string, type?: 'success' | 'info' | 'error' | 'warn') => void;
  removeToast: (id: string) => void;

  // Authentication states
  isAuthenticated: boolean;
  setIsAuthenticated: (auth: boolean) => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export const AppProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [language, setLanguage] = useState<'en' | 'kn'>('en');
  const [sidebarCollapsed, setSidebarCollapsed] = useState<boolean>(false);
  const [aiQuery, setAiQuery] = useState<string>('');
  const [selectedFir, setSelectedFir] = useState<FIR | null>(null);
  const [selectedSuspect, setSelectedSuspect] = useState<Suspect | null>(null);
  const [selectedVehicle, setSelectedVehicle] = useState<Vehicle | null>(null);
  
  // Refinements
  const [selectedDistrictId, setSelectedDistrictId] = useState<string>('all');
  const [toasts, setToasts] = useState<ToastMessage[]>([]);
  
  // Auth state defaults to false for security clearance enforcement
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);

  const addToast = (message: string, type: 'success' | 'info' | 'error' | 'warn' = 'success') => {
    const id = Math.random().toString(36).substring(2, 9);
    setToasts((prev) => [...prev, { id, message, type }]);
    
    // Auto-remove toasts after 4 seconds
    setTimeout(() => {
      removeToast(id);
    }, 4500);
  };

  const removeToast = (id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  return (
    <AppContext.Provider
      value={{
        language,
        setLanguage,
        sidebarCollapsed,
        setSidebarCollapsed,
        aiQuery,
        setAiQuery,
        selectedFir,
        setSelectedFir,
        selectedSuspect,
        setSelectedSuspect,
        selectedVehicle,
        setSelectedVehicle,
        selectedDistrictId,
        setSelectedDistrictId,
        toasts,
        addToast,
        removeToast,
        isAuthenticated,
        setIsAuthenticated,
      }}
    >
      {children}
    </AppContext.Provider>
  );
};

export const useApp = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
};
