
import React, { useState } from 'react';
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Loader2, Upload } from 'lucide-react';
import { useToast } from "@/hooks/use-toast";

interface ResumeUploaderProps {
  onParseSuccess: (data: {
    skills: string[];
    role: string;
    location: string;
  }) => void;
  isLoading: boolean;
  setIsLoading: (loading: boolean) => void;
}

const ResumeUploader: React.FC<ResumeUploaderProps> = ({
  onParseSuccess,
  isLoading,
  setIsLoading
}) => {
  const [dragActive, setDragActive] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const { toast } = useToast();

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFiles(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      handleFiles(e.target.files[0]);
    }
  };

  const handleFiles = (file: File) => {
    const validTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
    if (validTypes.includes(file.type)) {
      setFile(file);
    } else {
      toast({
        title: "Invalid file type",
        description: "Please upload a PDF or DOCX file",
        variant: "destructive"
      });
    }
  };

  const uploadResume = async () => {
    if (!file) {
      toast({
        title: "No file selected",
        description: "Please select a file to upload",
        variant: "destructive"
      });
      return;
    }

    try {
      setIsLoading(true);
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('http://localhost:5000/api/parse-resume', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Server responded with an error');
      }

      const data = await response.json();
      onParseSuccess(data);
      toast({
        title: "Resume parsed successfully",
        description: "Check out your LinkedIn job matches!",
      });
    } catch (error) {
      console.error('Upload failed:', error);
      toast({
        title: "Upload failed",
        description: "There was an error processing your resume",
        variant: "destructive"
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card className="p-6 w-full max-w-md mx-auto bg-secondary/30 border-zinc-800">
      <div className="text-center mb-4">
        <h3 className="text-lg font-medium text-gray-200">Upload Your Resume</h3>
        <p className="text-sm text-gray-400">PDF or DOCX format only</p>
      </div>
      
      <div 
        className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer mb-4 transition-colors
          ${dragActive ? 'border-blue-500 bg-blue-900/20' : 'border-gray-700 hover:border-gray-500'}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <label htmlFor="file-upload" className="cursor-pointer flex flex-col items-center">
          <Upload className="h-10 w-10 text-gray-400 mb-2" />
          <span className="text-sm font-medium text-gray-300">
            {file ? file.name : 'Drag & drop your resume or click to browse'}
          </span>
          <input 
            id="file-upload" 
            type="file" 
            accept=".pdf,.docx"
            className="hidden" 
            onChange={handleChange}
          />
        </label>
      </div>
      
      <Button 
        onClick={uploadResume} 
        className="w-full bg-blue-600 hover:bg-blue-700" 
        disabled={!file || isLoading}
      >
        {isLoading ? (
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            Processing
          </>
        ) : "Analyze Resume"}
      </Button>
    </Card>
  );
};

export default ResumeUploader;
