import React, { useEffect, useState } from 'react';

function LogConsole() {
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    // Fetch logs from backend API
    const fetchLogs = async () => {
      try {
        const response = await fetch('/api/logs');
        if (response.ok) {
          const data = await response.json();
          setLogs(data.logs);
        }
      } catch (error) {
        console.error('Error fetching logs:', error);
      }
    };

    fetchLogs();
    const interval = setInterval(fetchLogs, 2000); // Poll every 2 seconds
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex-grow p-4 overflow-auto bg-black text-white">
      <h2 className="text-lg font-bold mb-2">Logs</h2>
      <div className="space-y-1">
        {logs.map((log, index) => (
          <div key={index} className="text-sm font-mono">
            {log}
          </div>
        ))}
      </div>
    </div>
  );
}

export default LogConsole;
