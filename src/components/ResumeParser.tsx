
import React, { useState } from 'react';
import ResumeUploader from './ResumeUploader';
import JobMatchResults from './JobMatchResults';
import { Button } from '@/components/ui/button';
import { ArrowLeft } from 'lucide-react';

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

const ResumeParser: React.FC = () => {
  const [parsedData, setParsedData] = useState<ParsedData | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleParseSuccess = (data: ParsedData) => {
    setParsedData(data);
    console.log("Parsed data:", data);
  };

  return (
    <div className="w-full max-w-3xl mx-auto">
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
            contactInfo={parsedData.contact_info}
            skills={parsedData.skills}
            role={parsedData.role}
            location={parsedData.location}
            experienceData={parsedData.experience}
            experienceYears={parsedData.experience_years}
            education={parsedData.education}
            projects={parsedData.projects}
            interests={parsedData.interests}
            growthPotential={parsedData.growth_potential}
            writingQuality={parsedData.writing_quality}
            resumeSuggestions={parsedData.resume_suggestions}
            atsScore={parsedData.ats_score}
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
