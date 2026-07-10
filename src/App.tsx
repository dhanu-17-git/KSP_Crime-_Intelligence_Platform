import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AppProvider } from './context/AppContext';
import { AuthGuard } from './components/AuthGuard';
import { Login } from './pages/Login/Login';
import { DashboardLayout } from './layouts/DashboardLayout';
import { Dashboard } from './pages/Dashboard/Dashboard';
import { AIWorkspace } from './pages/AIWorkspace/AIWorkspace';
import { Cases } from './pages/Cases/Cases';
import { Suspects } from './pages/Suspects/Suspects';
import { Vehicles } from './pages/Vehicles/Vehicles';
import { CrimeMap } from './pages/CrimeMap/CrimeMap';
import { Analytics } from './pages/Analytics/Analytics';
import { CriminalNetwork } from './pages/CriminalNetwork/CriminalNetwork';
import { Reports } from './pages/Reports/Reports';
import { ReportPreview } from './pages/ReportPreview/ReportPreview';
import { SettingsPage } from './pages/Settings/Settings';
import { Profile } from './pages/Profile/Profile';
import './App.css';

function App() {
  return (
    <AppProvider>
      <BrowserRouter>
        <Routes>
          {/* Public Authentication Gate */}
          <Route path="/login" element={<Login />} />

          {/* Official Report Preview — standalone, no app shell */}
          <Route path="/reports/preview" element={<ReportPreview />} />

          {/* Secure Private Channels wrapped under AuthGuard */}
          <Route element={<AuthGuard />}>
            <Route path="/" element={<DashboardLayout />}>
              <Route index element={<Dashboard />} />
              <Route path="ai-workspace" element={<AIWorkspace />} />
              <Route path="cases" element={<Cases />} />
              <Route path="suspects" element={<Suspects />} />
              <Route path="vehicles" element={<Vehicles />} />
              <Route path="map" element={<CrimeMap />} />
              <Route path="analytics" element={<Analytics />} />
              <Route path="network" element={<CriminalNetwork />} />
              <Route path="reports" element={<Reports />} />
              <Route path="settings" element={<SettingsPage />} />
              <Route path="profile" element={<Profile />} />
            </Route>
          </Route>
        </Routes>
      </BrowserRouter>
    </AppProvider>
  );
}

export default App;
