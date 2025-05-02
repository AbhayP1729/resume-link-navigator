
import React, { useState } from 'react';
import ResumeUploader from './ResumeUploader';
import JobMatchResults from './JobMatchResults';
import { Button } from '@/components/ui/button';
import { ArrowLeft } from 'lucide-react';

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
    <div className="w-full max-w-md mx-auto">
      {!parsedData && (
        <ResumeUploader 
          onParseSuccess={handleParseSuccess} 
          isLoading={isLoading} 
          setIsLoading={setIsLoading} 
        />
      )}
      
      {parsedData && (
        <div className="space-y-4">
          <JobMatchResults 
            skills={parsedData.skills}
            role={parsedData.role}
            location={parsedData.location}
          />
          <Button 
            variant="ghost" 
            className="text-sm text-blue-400 hover:text-blue-300 mx-auto flex items-center transition-all"
            onClick={() => setParsedData(null)}
          >
            <ArrowLeft className="mr-2 h-4 w-4" />
            Upload a different resume
          </Button>
        </div>
      )}
    </div>
  );
};

export default ResumeParser;
