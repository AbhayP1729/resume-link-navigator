
import React, { useState } from 'react';
import ResumeUploader from './ResumeUploader';
import JobMatchResults from './JobMatchResults';

interface ParsedData {
  skills: string[];
  role: string;
  location: string;
}

const ResumeParser: React.FC = () => {
  const [parsedData, setParsedData] = useState<ParsedData | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleParseSuccess = (data: ParsedData) => {
    setParsedData(data);
  };

  return (
    <div className="space-y-6 w-full max-w-md mx-auto">
      {!parsedData && (
        <ResumeUploader 
          onParseSuccess={handleParseSuccess} 
          isLoading={isLoading} 
          setIsLoading={setIsLoading} 
        />
      )}
      
      {parsedData && (
        <>
          <JobMatchResults 
            skills={parsedData.skills}
            role={parsedData.role}
            location={parsedData.location}
          />
          <button 
            onClick={() => setParsedData(null)} 
            className="text-sm text-blue-500 hover:text-blue-700 mx-auto block"
          >
            Upload a different resume
          </button>
        </>
      )}
    </div>
  );
};

export default ResumeParser;
