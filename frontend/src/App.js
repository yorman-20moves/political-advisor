import React from 'react';
import SearchInterface from './components/SearchInterface';
import JobQueue from './components/JobQueue';
import ConfigDisplay from './components/ConfigDisplay';
import LogConsole from './components/LogConsole';
import Sidebar from './components/Sidebar';
import ConfigContextProvider from './contexts/ConfigContext';

function App() {
  return (
    <ConfigContextProvider>
      <div className="flex h-screen">
        <Sidebar>
          <JobQueue />
        </Sidebar>
        <main className="flex-grow flex flex-col">
          <SearchInterface />
          <LogConsole />
        </main>
        <Sidebar>
          <ConfigDisplay />
        </Sidebar>
      </div>
    </ConfigContextProvider>
  );
}

export default App;
