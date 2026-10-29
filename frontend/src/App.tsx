import React, { useState } from 'react';
import { Login } from './pages/Login';
import { Dashboard } from './pages/Dashboard';

export const App: React.FC = () => {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('token'));

  const handleLoginSuccess = (newToken: string) => {
    localStorage.setItem('token', newToken);
    setToken(newToken);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setToken(null);
  };

  return (
    <div>
      {!token ? (
        <Login onLoginSuccess={handleLoginSuccess} />
      ) : (
        <Dashboard onLogout={handleLogout} />
      )}
    </div>
  );
};

export default App;
