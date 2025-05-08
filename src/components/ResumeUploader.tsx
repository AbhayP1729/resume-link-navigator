
import React, { useState } from 'react';
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Loader2, Upload, FileText } from 'lucide-react';
import { useToast } from "@/hooks/use-toast";

interface Interest {
  skill: string;
  score: number;
}

interface GrowthPotential {
  score: number;
  indicators: string[];
}

interface ContactInfo {
  name: string | null;
  email: string | null;
  phone: string | null;
  linkedin: string | null;
}

interface ExperienceData {
  years: number | null;
  positions: string[];
}

interface EducationItem {
  text: string;
  quality_score: number;
}

interface ProjectItem {
  title: string;
  description: string;
  complexity_score: number;
}

interface WritingQuality {
  score: number;
  weak_phrases_found: number;
  action_verbs_found: number;
  quantifiable_achievements: number;
  generic_terms_found: number;
}

interface ATSScoring {
  overall: number;
  components: {
    contact_info: number;
    skills_match: number;
    experience: number;
    education: number;
    projects: number;
    writing_quality: number;
  };
}

interface ResumeSuggestion {
  type: string;
  severity: 'high' | 'medium' | 'low';
  text: string;
}

interface ParsedData {
  contact_info: ContactInfo;
  skills: string[];
  role: string;
  location: string;
  experience: ExperienceData;
  experience_years: number | null;
  education: EducationItem[];
  projects: ProjectItem[];
  interests: Interest[];
  growth_potential: GrowthPotential;
  writing_quality: WritingQuality;
  resume_suggestions: ResumeSuggestion[];
  ats_score: ATSScoring;
}

interface ResumeUploaderProps {
  onParseSuccess: (data: ParsedData) => void;
  onExtractRawText?: (text: string) => void;
  isLoading: boolean;
  setIsLoading: (loading: boolean) => void;
}

const ResumeUploader: React.FC<ResumeUploaderProps> = ({
  onParseSuccess,
  onExtractRawText,
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

      // Extract raw text from file for potential analysis
      if (onExtractRawText) {
        try {
          const reader = new FileReader();
          reader.onload = async (e) => {
            const text = e.target?.result as string;
            if (text) {
              onExtractRawText(text);
            }
          };
          reader.readAsText(file);
        } catch (error) {
          console.log("Could not extract text from file");
        }
      }
        
      // Parse the resume
      const response = await fetch('http://localhost:5000/api/parse-resume', {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        throw new Error('Server responded with an error');
      }
      
      const parsedData = await response.json();

      // Validate the response before passing it to parent
      if (parsedData && typeof parsedData === 'object') {
        onParseSuccess(parsedData);
        toast({
          title: "Resume analyzed successfully",
          description: "Check out your insights based on your resume",
        });
      } else {
        throw new Error('Invalid response format from server');
      }
    } catch (error) {
      console.error('Upload failed:', error);
      toast({
        title: "Upload failed",
        description: "There was an error processing your resume. Make sure the backend server is running.",
        variant: "destructive"
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card className="p-6 w-full bg-gradient-to-br from-zinc-900 to-black/60 border border-zinc-800/50 shadow-lg">
      <div className="text-center mb-5 animate-fade-in">
        <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-blue-900/20 mb-4 backdrop-blur-sm">
          <FileText className="h-6 w-6 text-blue-400" />
        </div>
        <h3 className="text-xl font-semibold text-white mb-1">Professional Resume Analyzer</h3>
        <p className="text-sm text-gray-400">Get intelligent insights to improve your resume and application success</p>
      </div>
      
      <div 
        className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer mb-5 transition-all duration-300 animate-fade-in
          ${dragActive 
            ? 'border-blue-500 bg-blue-900/20 scale-[1.01]' 
            : 'border-zinc-700 hover:border-zinc-500 hover:bg-blue-900/10'
          }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        style={{ animationDelay: "0.2s" }}
      >
        <label htmlFor="file-upload" className="cursor-pointer flex flex-col items-center">
          <Upload className={`h-12 w-12 mb-3 transition-colors duration-300 ${file ? 'text-blue-400' : 'text-zinc-500'}`} />
          <span className="text-sm font-medium text-gray-300 mb-1">
            {file ? file.name : 'Drag & drop your resume here'}
          </span>
          <span className="text-xs text-gray-500">
            {file ? `${Math.round(file.size / 1024)} KB` : 'Upload PDF or DOCX file'}
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
        className="w-full bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white py-2.5 shadow-lg shadow-blue-900/20 animate-fade-in" 
        disabled={!file || isLoading}
        style={{ animationDelay: "0.3s" }}
      >
        {isLoading ? (
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            Analyzing Your Resume...
          </>
        ) : "Analyze & Get Professional Insights"}
      </Button>
      
      <p className="mt-4 text-xs text-center text-zinc-500">
        Your resume is analyzed locally through our advanced NLP system.
        No data is stored or shared with third parties.
      </p>
    </Card>
  );
};

export default ResumeUploader;
