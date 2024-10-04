import React, { useContext, useEffect } from 'react';
import { ConfigContext } from '../contexts/ConfigContext';

function ConfigDisplay() {
  const { config, fetchConfig } = useContext(ConfigContext);

  useEffect(() => {
    fetchConfig();
  }, [fetchConfig]);

  return (
    <div className="p-4 overflow-auto h-full">
      <h2 className="text-lg font-bold mb-2">Configuration</h2>
      {Object.entries(config).map(([key, value]) => (
        <div
          key={key}
          className={`mb-1 ${value ? 'text-green-600' : 'text-red-600'}`}
        >
          {key}: {value || 'Not set'}
        </div>
      ))}
    </div>
  );
}

export default ConfigDisplay;
