import React, { createContext, useState, useCallback } from 'react';

export const ConfigContext = createContext();

function ConfigContextProvider({ children }) {
  const [config, setConfig] = useState({});

  const fetchConfig = useCallback(async () => {
    try {
      const response = await fetch('/api/config');
      if (response.ok) {
        const data = await response.json();
        setConfig(data.config);
      }
    } catch (error) {
      console.error('Error fetching configuration:', error);
    }
  }, []);

  return (
    <ConfigContext.Provider value={{ config, fetchConfig }}>
      {children}
    </ConfigContext.Provider>
  );
}

export default ConfigContextProvider;
