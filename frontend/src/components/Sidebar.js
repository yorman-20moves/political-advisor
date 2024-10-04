import React from 'react';

function Sidebar({ children }) {
  return (
    <div className="w-64 bg-gray-200 overflow-auto">
      {children}
    </div>
  );
}

export default Sidebar;
