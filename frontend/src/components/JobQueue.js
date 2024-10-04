import React, { useEffect, useState } from 'react';

function JobQueue() {
  const [jobs, setJobs] = useState([]);

  useEffect(() => {
    // Fetch job queue from backend API
    const fetchJobs = async () => {
      try {
        const response = await fetch('/api/job_queue');
        if (response.ok) {
          const data = await response.json();
          setJobs(data.jobs);
        }
      } catch (error) {
        console.error('Error fetching job queue:', error);
      }
    };

    fetchJobs();
    const interval = setInterval(fetchJobs, 5000); // Poll every 5 seconds
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="p-4 overflow-auto h-full">
      <h2 className="text-lg font-bold mb-2">Job Queue</h2>
      <ul>
        {jobs.map((job) => (
          <li key={job.id} className="mb-4">
            <div className="font-semibold">{job.name}</div>
            <div className="w-full bg-gray-300 rounded h-2 mt-1">
              <div
                className="bg-green-500 h-2 rounded"
                style={{ width: `${job.progress}%` }}
              ></div>
            </div>
            <div className="text-sm text-gray-600 mt-1">{job.status}</div>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default JobQueue;
