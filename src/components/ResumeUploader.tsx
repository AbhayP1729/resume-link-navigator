import React, { useState } from 'react';
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Loader2, Upload, FileText, ArrowDown, FileCode } from 'lucide-react';
import { useToast } from "@/hooks/use-toast";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";

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

interface SkillsData {
  technical: string[];
  soft: string[];
  outdated: string[];
  balance_score: number;
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
  const [jobDescription, setJobDescription] = useState<string>('');
  const [activeTab, setActiveTab] = useState<string>('upload');
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

      // If job description is provided, we'll analyze it against the resume
      let endpoint = jobDescription 
        ? 'http://localhost:5000/api/analyze-job-match'
        : 'http://localhost:5000/api/parse-resume';
        
      let response;
      
      if (jobDescription) {
        // First parse the resume normally
        const resumeResponse = await fetch('http://localhost:5000/api/parse-resume', {
          method: 'POST',
          body: formData,
        });
        
        if (!resumeResponse.ok) {
          throw new Error('Server responded with an error when parsing resume');
        }
        
        const resumeData = await resumeResponse.json();
        
        // Then get text from file to send with job description
        const text = await file.text();
        
        // Now analyze job match
        const jobMatchResponse = await fetch(endpoint, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            resume_text: text,
            job_description: jobDescription
          }),
        });
        
        if (!jobMatchResponse.ok) {
          throw new Error('Server responded with an error when analyzing job match');
        }
        
        const jobMatchData = await jobMatchResponse.json();
        
        // Combine the data
        response = {
          ...resumeData,
          job_match: jobMatchData
        };
      } else {
        // Just parse the resume normally
        response = await fetch('http://localhost:5000/api/parse-resume', {
          method: 'POST',
          body: formData,
        });
        
        if (!response.ok) {
          throw new Error('Server responded with an error');
        }
        
        response = await response.json();
      }

      onParseSuccess(response);
      toast({
        title: "Resume analyzed successfully",
        description: "Check out your detailed profile and suggestions!",
      });
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
        <h3 className="text-xl font-semibold text-white mb-1">ATS Resume Analyzer</h3>
        <p className="text-sm text-gray-400">Get intelligent insights & suggestions</p>
      </div>
      
      <Tabs 
        defaultValue="upload" 
        value={activeTab} 
        onValueChange={setActiveTab}
        className="w-full mb-4"
      >
        <TabsList className="grid w-full grid-cols-2 mb-5">
          <TabsTrigger value="upload">Upload Resume</TabsTrigger>
          <TabsTrigger value="job-desc">Job Description</TabsTrigger>
        </TabsList>
        
        <TabsContent value="upload">
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
                {file ? 'File selected' : 'or click to browse'}
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
          
          <div className="text-center text-xs text-blue-300 mb-5 flex justify-center items-center">
            <ArrowDown className="h-4 w-4 mr-2" />
            <span>Optionally add a job description to compare match</span>
          </div>
          
          <Button 
            variant="secondary"
            className="w-full text-sm mb-4"
            onClick={() => setActiveTab('job-desc')}
          >
            <FileCode className="mr-2 h-4 w-4" />
            Add Job Description
          </Button>
        </TabsContent>
        
        <TabsContent value="job-desc">
          <div className="space-y-4">
            <div className="space-y-2">
              <label htmlFor="job-description" className="text-sm font-medium text-white block">
                Paste Job Description (Optional)
              </label>
              <Textarea 
                id="job-description" 
                placeholder="Paste job description here to analyze its match with your resume..." 
                className="min-h-[200px] bg-zinc-800/50 border-zinc-700"
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
              />
              <p className="text-xs text-zinc-400">
                This allows us to analyze your resume's compatibility with specific job requirements.
              </p>
            </div>
            
            <Button 
              variant="secondary"
              className="w-full text-sm mb-4"
              onClick={() => setActiveTab('upload')}
            >
              <Upload className="mr-2 h-4 w-4" />
              Back to Resume Upload
            </Button>
          </div>
        </TabsContent>
      </Tabs>
      
      <Button 
        onClick={uploadResume} 
        className="w-full bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white py-2.5 shadow-lg shadow-blue-900/20 animate-fade-in" 
        disabled={!file || isLoading}
        style={{ animationDelay: "0.3s" }}
      >
        {isLoading ? (
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            Analyzing Resume...
          </>
        ) : "Analyze & Get ATS Insights"}
      </Button>
    </Card>
  );
};

export default ResumeUploader;
