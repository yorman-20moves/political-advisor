import React, { useState } from 'react';

function SearchInterface() {
  const [searchTerm, setSearchTerm] = useState('');
  const [isContextual, setIsContextual] = useState(false);

  const handleSearch = async () => {
    // Dispatch search action to backend API
    try {
      const response = await fetch('/api/start_search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ searchTerm, isContextual }),
      });
      if (response.ok) {
        // Handle successful initiation
        console.log('Search initiated successfully');
      } else {
        // Handle errors
        console.error('Failed to initiate search');
      }
    } catch (error) {
      console.error('Error initiating search:', error);
    }
  };

  return (
    <div className="flex items-center space-x-4 p-4 bg-gray-100">
      <input
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        placeholder="Enter search terms..."
        className="flex-grow p-2 border rounded"
      />
      <label className="flex items-center">
        <input
          type="checkbox"
          checked={isContextual}
          onChange={(e) => setIsContextual(e.target.checked)}
          className="mr-2"
        />
        Contextual Search
      </label>
      <button
        onClick={handleSearch}
        className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
      >
        Start Search
      </button>
    </div>
  );
}

export default SearchInterface;
