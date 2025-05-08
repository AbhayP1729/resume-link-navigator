
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
  job_match?: {
    match_percentage: number;
    matching_skills: string[];
    missing_skills: string[];
    job_skills: string[];
  };
}

const ResumeParser: React.FC = () => {
  const [parsedData, setParsedData] = useState<ParsedData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [rawText, setRawText] = useState<string | null>(null);

  // Improved data validation and cleaning function
  const handleParseSuccess = (data: ParsedData) => {
    console.log("Parsed data:", data);
    
    // Enhanced data validation and cleaning
    const cleanedData = {
      ...data,
      contact_info: {
        name: data.contact_info.name || null,
        email: data.contact_info.email || null,
        phone: data.contact_info.phone || null,
        linkedin: data.contact_info.linkedin || null
      },
      skills: Array.isArray(data.skills) ? 
        // Filter out low-confidence skills and limit to most relevant ones
        data.skills.filter(skill => skill && skill.trim() !== "") : [],
      role: data.role || "Not specified",
      location: data.location || "Not specified",
      // Only include interests with meaningful scores
      interests: Array.isArray(data.interests) ? 
        data.interests.filter(interest => 
          interest.skill && 
          interest.skill.trim() !== "" && 
          interest.score >= 3
        ) : [],
      growth_potential: {
        score: data.growth_potential?.score || 0,
        indicators: Array.isArray(data.growth_potential?.indicators) ? 
          data.growth_potential.indicators.filter(indicator => indicator.trim() !== "") : []
      },
      // Only include meaningful suggestions
      resume_suggestions: Array.isArray(data.resume_suggestions) ?
        data.resume_suggestions
          .filter(suggestion => 
            suggestion.text.trim() !== "" && 
            suggestion.severity !== 'low'
          )
          .slice(0, 3) : [] // Limit to top 3 most important suggestions
    };
    
    // Validate education data
    if (cleanedData.education && Array.isArray(cleanedData.education)) {
      cleanedData.education = cleanedData.education
        .filter(edu => edu.text && edu.text.trim() !== "")
        .map(edu => ({
          ...edu,
          quality_score: typeof edu.quality_score === 'number' ? 
            Math.min(10, Math.max(1, edu.quality_score)) : 5 // Normalize between 1-10
        }));
    }
    
    // Validate project data
    if (cleanedData.projects && Array.isArray(cleanedData.projects)) {
      cleanedData.projects = cleanedData.projects
        .filter(proj => proj.title && proj.title.trim() !== "")
        .map(proj => ({
          ...proj,
          complexity_score: typeof proj.complexity_score === 'number' ? 
            Math.min(10, Math.max(1, proj.complexity_score)) : 5 // Normalize between 1-10
        }));
    }
    
    setParsedData(cleanedData);
  };

  // Store raw text content for potential analysis
  const handleRawText = (text: string) => {
    setRawText(text);
  };

  return (
    <div className="w-full max-w-3xl mx-auto">
      {!parsedData && (
        <ResumeUploader 
          onParseSuccess={handleParseSuccess} 
          onExtractRawText={handleRawText}
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
            jobMatch={parsedData.job_match}
            rawResumeText={rawText}
          />
          <Button 
            variant="ghost" 
            className="text-sm text-blue-400 hover:text-blue-300 mx-auto flex items-center transition-all"
            onClick={() => {
              setParsedData(null);
              setRawText(null);
            }}
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
