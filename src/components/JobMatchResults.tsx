
import React, { useState } from 'react';
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { 
  ExternalLink, Briefcase, MapPin, Award, BookOpen, Sparkles, 
  TrendingUp, Lightbulb, Clock, Mail, Phone, Linkedin, 
  User, File, FileCheck, AlertTriangle, BarChart
} from 'lucide-react';
import { Separator } from "@/components/ui/separator";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

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

interface JobMatch {
  match_percentage: number;
  matching_skills: string[];
  missing_skills: string[];
  job_skills: string[];
}

interface JobMatchResultsProps {
  contactInfo: ContactInfo;
  skills: string[];
  role: string;
  location: string;
  experienceData: ExperienceData;
  experienceYears: number | null;
  education: EducationItem[];
  projects: ProjectItem[];
  interests: Interest[];
  growthPotential: GrowthPotential;
  writingQuality: WritingQuality;
  resumeSuggestions: ResumeSuggestion[];
  atsScore: ATSScoring;
  jobMatch?: JobMatch;
}

const JobMatchResults: React.FC<JobMatchResultsProps> = ({ 
  contactInfo,
  skills, 
  role, 
  location,
  experienceData,
  experienceYears,
  education,
  projects,
  interests,
  growthPotential,
  writingQuality,
  resumeSuggestions,
  atsScore,
  jobMatch
}) => {
  const generateLinkedInUrl = () => {
    const baseUrl = "https://www.linkedin.com/jobs/search/?";
    const params = new URLSearchParams();
    
    if (role) {
      params.append("keywords", role);
    }
    
    if (location && location !== "Remote") {
      params.append("location", location);
    }
    
    if (skills && skills.length > 0) {
      // Add top 3 skills as keywords
      const skillsParam = skills.slice(0, 3).join(" ");
      const currentKeywords = params.get("keywords") || "";
      params.set("keywords", `${currentKeywords} ${skillsParam}`.trim());
    }
    
    // Add experience level if available
    const years = experienceYears || experienceData?.years;
    if (years) {
      if (years < 2) {
        params.append("f_E", "1"); // Entry level
      } else if (years < 5) {
        params.append("f_E", "2"); // Associate
      } else if (years < 10) {
        params.append("f_E", "3"); // Mid-Senior level
      } else {
        params.append("f_E", "4"); // Director
      }
    }
    
    return `${baseUrl}${params.toString()}`;
  };

  const linkedInUrl = generateLinkedInUrl();

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high':
        return 'bg-red-900/20 border-red-800/30 text-red-200';
      case 'medium':
        return 'bg-amber-900/20 border-amber-800/30 text-amber-200';
      case 'low':
        return 'bg-blue-900/20 border-blue-800/30 text-blue-200';
      default:
        return 'bg-amber-900/20 border-amber-800/30 text-amber-200';
    }
  };

  return (
    <Card className="p-6 w-full mx-auto bg-gradient-to-br from-zinc-900 to-black/60 border border-zinc-800/50 shadow-lg animate-fade-in">
      <Tabs defaultValue="ats" className="w-full">
        <TabsList className="grid w-full grid-cols-5 mb-4">
          <TabsTrigger value="ats">ATS Score</TabsTrigger>
          <TabsTrigger value="profile">Profile</TabsTrigger>
          <TabsTrigger value="personality">Insights</TabsTrigger>
          <TabsTrigger value="suggestions">Improve</TabsTrigger>
          {jobMatch && <TabsTrigger value="job-match">Job Match</TabsTrigger>}
        </TabsList>
        
        {/* ATS Score Tab */}
        <TabsContent value="ats" className="space-y-6">
          <div className="text-center mb-4">
            <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-blue-900/20 mb-4 backdrop-blur-sm">
              <FileCheck className="h-6 w-6 text-blue-400" />
            </div>
            <h3 className="text-xl font-semibold text-gradient mb-1">ATS Compatibility</h3>
            <p className="text-sm text-zinc-400">How well your resume will perform in ATS systems</p>
          </div>
          
          <div className="flex flex-col items-center gap-4 mb-6">
            <div className="relative w-32 h-32 flex items-center justify-center">
              <svg className="w-full h-full" viewBox="0 0 100 100">
                <circle 
                  cx="50" cy="50" r="45" 
                  fill="none" 
                  stroke="#334155" 
                  strokeWidth="8" 
                />
                <circle 
                  cx="50" cy="50" r="45" 
                  fill="none" 
                  stroke={atsScore.overall >= 7 ? "#059669" : atsScore.overall >= 5 ? "#d97706" : "#dc2626"} 
                  strokeWidth="8" 
                  strokeDasharray="282.7"
                  strokeDashoffset={282.7 - ((atsScore.overall / 10) * 282.7)}
                  strokeLinecap="round"
                  transform="rotate(-90 50 50)"
                />
              </svg>
              <div className="absolute flex flex-col items-center">
                <span className="text-3xl font-bold">{atsScore.overall}</span>
                <span className="text-xs text-zinc-400">out of 10</span>
              </div>
            </div>
            <div className={`text-sm font-medium ${
              atsScore.overall >= 7 ? 'text-green-500' : 
              atsScore.overall >= 5 ? 'text-amber-500' : 
              'text-red-500'
            }`}>
              {atsScore.overall >= 7 ? 'Strong ATS Compatibility' : 
               atsScore.overall >= 5 ? 'Moderate ATS Compatibility' : 
               'Poor ATS Compatibility'}
            </div>
          </div>
          
          <Separator className="bg-zinc-800/50" />
          
          <div className="space-y-4 animate-fade-in" style={{ animationDelay: "0.1s" }}>
            <h4 className="text-sm font-medium text-zinc-400">Score Breakdown</h4>
            
            <div className="space-y-3">
              <div className="space-y-1">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-white">Contact Information</span>
                  <span className="text-xs text-zinc-500">{atsScore.components.contact_info}/10</span>
                </div>
                <Progress value={atsScore.components.contact_info * 10} className="h-2 bg-zinc-800" />
              </div>
              
              <div className="space-y-1">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-white">Skills Match</span>
                  <span className="text-xs text-zinc-500">{atsScore.components.skills_match}/10</span>
                </div>
                <Progress value={atsScore.components.skills_match * 10} className="h-2 bg-zinc-800" />
              </div>
              
              <div className="space-y-1">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-white">Experience</span>
                  <span className="text-xs text-zinc-500">{atsScore.components.experience}/10</span>
                </div>
                <Progress value={atsScore.components.experience * 10} className="h-2 bg-zinc-800" />
              </div>
              
              <div className="space-y-1">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-white">Education</span>
                  <span className="text-xs text-zinc-500">{atsScore.components.education}/10</span>
                </div>
                <Progress value={atsScore.components.education * 10} className="h-2 bg-zinc-800" />
              </div>
              
              <div className="space-y-1">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-white">Projects</span>
                  <span className="text-xs text-zinc-500">{atsScore.components.projects}/10</span>
                </div>
                <Progress value={atsScore.components.projects * 10} className="h-2 bg-zinc-800" />
              </div>
              
              <div className="space-y-1">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-white">Writing Quality</span>
                  <span className="text-xs text-zinc-500">{atsScore.components.writing_quality}/10</span>
                </div>
                <Progress value={atsScore.components.writing_quality * 10} className="h-2 bg-zinc-800" />
              </div>
            </div>
          </div>
          
          <Separator className="bg-zinc-800/50" />
          
          <div className="p-4 rounded-lg bg-blue-900/10 border border-blue-900/20 text-sm text-blue-100">
            <h5 className="font-medium mb-2 flex items-center">
              <AlertTriangle className="h-4 w-4 mr-2 text-blue-400" />
              ATS Insight
            </h5>
            <p>
              {atsScore.overall >= 8 ? 
                "Your resume is highly ATS-compatible. It has a strong balance of skills, experience details, and proper formatting that will help it get past screening algorithms." : 
                atsScore.overall >= 6 ?
                "Your resume is moderately ATS-compatible. Consider improving the weaker areas highlighted in your score breakdown to enhance visibility to recruiters." :
                "Your resume needs improvement to pass ATS systems effectively. Focus on the low-scoring areas and follow the suggestions provided to increase your chances."
              }
            </p>
          </div>
        </TabsContent>
        
        {/* Profile Tab */}
        <TabsContent value="profile" className="space-y-6">
          <div className="text-center mb-4">
            <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-blue-900/20 mb-4 backdrop-blur-sm">
              <User className="h-6 w-6 text-blue-400" />
            </div>
            <h3 className="text-xl font-semibold text-gradient mb-1">Professional Profile</h3>
            <p className="text-sm text-zinc-400">Based on your resume analysis</p>
          </div>
          
          {contactInfo && (
            <div className="animate-fade-in" style={{ animationDelay: "0.05s" }}>
              <div className="flex items-center gap-2 mb-2">
                <User className="h-4 w-4 text-blue-400" />
                <h4 className="font-medium text-sm text-zinc-400">Contact Information</h4>
              </div>
              <div className="pl-6 space-y-2">
                {contactInfo.name && (
                  <p className="text-white">{contactInfo.name}</p>
                )}
                <div className="flex flex-wrap gap-4">
                  {contactInfo.email && (
                    <div className="flex items-center text-zinc-300 text-sm">
                      <Mail className="h-3.5 w-3.5 mr-1 text-blue-400" />
                      {contactInfo.email}
                    </div>
                  )}
                  {contactInfo.phone && (
                    <div className="flex items-center text-zinc-300 text-sm">
                      <Phone className="h-3.5 w-3.5 mr-1 text-blue-400" />
                      {contactInfo.phone}
                    </div>
                  )}
                  {contactInfo.linkedin && (
                    <div className="flex items-center text-zinc-300 text-sm">
                      <Linkedin className="h-3.5 w-3.5 mr-1 text-blue-400" />
                      {contactInfo.linkedin}
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
          
          {contactInfo && <Separator className="bg-zinc-800/50" />}
          
          <div className="animate-fade-in" style={{ animationDelay: "0.1s" }}>
            <div className="flex items-center gap-2 mb-2">
              <Briefcase className="h-4 w-4 text-blue-400" />
              <h4 className="font-medium text-sm text-zinc-400">Detected Role</h4>
            </div>
            <p className="text-lg capitalize text-white pl-6">
              {role || "Not found"}
            </p>
          </div>
          
          <Separator className="bg-zinc-800/50" />
          
          <div className="animate-fade-in" style={{ animationDelay: "0.15s" }}>
            <div className="flex items-center gap-2 mb-2">
              <Clock className="h-4 w-4 text-blue-400" />
              <h4 className="font-medium text-sm text-zinc-400">Experience</h4>
            </div>
            <div className="pl-6">
              <p className="text-lg text-white">
                {experienceYears || experienceData?.years ? `${experienceYears || experienceData.years} years` : "Not specified"}
              </p>
              
              {experienceData?.positions && experienceData.positions.length > 0 && (
                <div className="mt-2">
                  <h5 className="text-sm text-zinc-400 mb-1">Previous Positions</h5>
                  <ul className="list-disc pl-4 space-y-1">
                    {experienceData.positions.map((position, index) => (
                      <li key={index} className="text-sm text-zinc-300">{position}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
          
          <Separator className="bg-zinc-800/50" />
          
          <div className="animate-fade-in" style={{ animationDelay: "0.2s" }}>
            <div className="flex items-center gap-2 mb-2">
              <MapPin className="h-4 w-4 text-blue-400" />
              <h4 className="font-medium text-sm text-zinc-400">Location</h4>
            </div>
            <p className="text-lg text-white pl-6">
              {location || "Remote"}
            </p>
          </div>
          
          <Separator className="bg-zinc-800/50" />
          
          <div className="animate-fade-in" style={{ animationDelay: "0.25s" }}>
            <div className="flex items-center gap-2 mb-2">
              <BookOpen className="h-4 w-4 text-blue-400" />
              <h4 className="font-medium text-sm text-zinc-400">Education</h4>
            </div>
            <div className="pl-6">
              {education && education.length > 0 ? (
                <div className="space-y-3">
                  {education.map((edu, index) => (
                    <div key={index} className="space-y-1">
                      <p className="text-sm text-white">{edu.text}</p>
                      <div className="flex items-center gap-2">
                        <span className="text-xs text-zinc-400">Quality Score:</span>
                        <div className="flex-1">
                          <Progress value={edu.quality_score * 10} className="h-1.5 bg-zinc-800" />
                        </div>
                        <span className="text-xs text-zinc-400">{edu.quality_score}/10</span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-zinc-500">No education details found</p>
              )}
            </div>
          </div>
          
          <Separator className="bg-zinc-800/50" />
          
          <div className="animate-fade-in" style={{ animationDelay: "0.3s" }}>
            <div className="flex items-center gap-2 mb-3">
              <Award className="h-4 w-4 text-blue-400" />
              <h4 className="font-medium text-sm text-zinc-400">Top Skills</h4>
            </div>
            <div className="flex flex-wrap gap-2 pl-6">
              {skills && skills.length > 0 ? (
                skills.map((skill, index) => (
                  <Badge 
                    key={index} 
                    variant="secondary" 
                    className="capitalize py-1.5 px-3 bg-blue-900/40 text-blue-100 border border-blue-800/30 hover:bg-blue-800/50 transition-colors"
                  >
                    {skill}
                  </Badge>
                ))
              ) : (
                <p className="text-sm text-zinc-500">No skills detected</p>
              )}
            </div>
          </div>
          
          {projects && projects.length > 0 && (
            <>
              <Separator className="bg-zinc-800/50" />
              
              <div className="animate-fade-in" style={{ animationDelay: "0.35s" }}>
                <div className="flex items-center gap-2 mb-3">
                  <File className="h-4 w-4 text-blue-400" />
                  <h4 className="font-medium text-sm text-zinc-400">Projects</h4>
                </div>
                <div className="pl-6 space-y-4">
                  {projects.map((project, index) => (
                    <div key={index} className="space-y-2">
                      <div className="flex justify-between items-center">
                        <h5 className="font-medium text-white">{project.title}</h5>
                        <Badge variant="outline" className="text-xs bg-blue-900/20 border-blue-800/30 text-blue-100">
                          Complexity: {project.complexity_score}/10
                        </Badge>
                      </div>
                      <p className="text-sm text-zinc-300">{project.description}</p>
                    </div>
                  ))}
                </div>
              </div>
            </>
          )}
        </TabsContent>
        
        {/* Personality Tab */}
        <TabsContent value="personality" className="space-y-6">
          <div className="text-center mb-4">
            <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-purple-900/20 mb-4 backdrop-blur-sm">
              <Sparkles className="h-6 w-6 text-purple-400" />
            </div>
            <h3 className="text-xl font-semibold text-gradient mb-1">Professional Insights</h3>
            <p className="text-sm text-zinc-400">Understanding your strengths & potential</p>
          </div>
          
          <div className="animate-fade-in" style={{ animationDelay: "0.1s" }}>
            <div className="flex items-center gap-2 mb-3">
              <Sparkles className="h-4 w-4 text-purple-400" />
              <h4 className="font-medium text-sm text-zinc-400">Areas of Interest</h4>
            </div>
            <div className="space-y-3 pl-6">
              {interests && interests.length > 0 ? (
                interests.map((interest, index) => (
                  <div key={index} className="space-y-1">
                    <div className="flex justify-between items-center">
                      <span className="text-sm capitalize text-white">{interest.skill}</span>
                      <span className="text-xs text-zinc-500">Interest level</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <Progress value={interest.score * 10} className="h-2 bg-zinc-800" />
                      <span className="text-xs text-zinc-400 min-w-[40px]">{interest.score}/10</span>
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-sm text-zinc-500">No specific interests detected</p>
              )}
            </div>
          </div>
          
          <Separator className="bg-zinc-800/50" />
          
          <div className="animate-fade-in" style={{ animationDelay: "0.2s" }}>
            <div className="flex items-center gap-2 mb-3">
              <BarChart className="h-4 w-4 text-purple-400" />
              <h4 className="font-medium text-sm text-zinc-400">Writing Quality</h4>
            </div>
            <div className="space-y-3 pl-6">
              <div className="space-y-1">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-white">Overall Writing Quality</span>
                  <span className="text-xs text-zinc-500">Score</span>
                </div>
                <div className="flex items-center gap-3">
                  <Progress value={writingQuality.score * 10} className="h-2 bg-zinc-800" />
                  <span className="text-xs text-zinc-400">{writingQuality.score}/10</span>
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-2 mt-3">
                <div className="p-2 rounded-md bg-zinc-800/30 border border-zinc-700/30">
                  <div className="text-xs text-zinc-400 mb-1">Action Verbs</div>
                  <div className="text-sm text-white">{writingQuality.action_verbs_found} found</div>
                </div>
                <div className="p-2 rounded-md bg-zinc-800/30 border border-zinc-700/30">
                  <div className="text-xs text-zinc-400 mb-1">Quantifiable Results</div>
                  <div className="text-sm text-white">{writingQuality.quantifiable_achievements} found</div>
                </div>
                <div className="p-2 rounded-md bg-zinc-800/30 border border-zinc-700/30">
                  <div className="text-xs text-zinc-400 mb-1">Weak Phrases</div>
                  <div className="text-sm text-white">{writingQuality.weak_phrases_found} found</div>
                </div>
                <div className="p-2 rounded-md bg-zinc-800/30 border border-zinc-700/30">
                  <div className="text-xs text-zinc-400 mb-1">Generic Terms</div>
                  <div className="text-sm text-white">{writingQuality.generic_terms_found} found</div>
                </div>
              </div>
            </div>
          </div>
          
          <Separator className="bg-zinc-800/50" />
          
          <div className="animate-fade-in" style={{ animationDelay: "0.2s" }}>
            <div className="flex items-center gap-2 mb-3">
              <TrendingUp className="h-4 w-4 text-green-400" />
              <h4 className="font-medium text-sm text-zinc-400">Growth Potential</h4>
            </div>
            <div className="space-y-3 pl-6">
              <div className="space-y-1">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-white">Growth Mindset</span>
                  <span className="text-xs text-zinc-500">Score</span>
                </div>
                <div className="flex items-center gap-3">
                  <Progress value={growthPotential.score * 10} className="h-2 bg-zinc-800" />
                  <span className="text-xs text-zinc-400">{growthPotential.score}/10</span>
                </div>
              </div>
              
              {growthPotential.indicators && growthPotential.indicators.length > 0 ? (
                <div className="mt-2">
                  <h5 className="text-xs text-zinc-500 mb-2">Growth Indicators</h5>
                  <div className="flex flex-wrap gap-2">
                    {growthPotential.indicators.map((indicator, index) => (
                      <Badge 
                        key={index} 
                        variant="secondary" 
                        className="capitalize py-1 px-2 bg-green-900/20 text-green-100 border border-green-800/30"
                      >
                        {indicator}
                      </Badge>
                    ))}
                  </div>
                </div>
              ) : null}
            </div>
          </div>
          
          <Separator className="bg-zinc-800/50" />
          
          <div className="animate-fade-in" style={{ animationDelay: "0.3s" }}>
            <div className="flex items-center gap-2 mb-3">
              <Lightbulb className="h-4 w-4 text-yellow-400" />
              <h4 className="font-medium text-sm text-zinc-400">Professional Fit</h4>
            </div>
            <div className="pl-6 space-y-3">
              <p className="text-sm text-zinc-300">
                Based on your experience, skills, and interests, you appear to be a good fit for <span className="text-white font-medium capitalize">{role}</span> positions.
              </p>
              {(interests && interests.length > 0) && (
                <p className="text-sm text-zinc-300">
                  Your resume shows the strongest passion for <span className="text-white font-medium capitalize">{interests[0]?.skill}</span>, which suggests you would thrive in roles focused on this technology.
                </p>
              )}
              {(growthPotential.score > 5) && (
                <p className="text-sm text-zinc-300">
                  Your growth mindset indicates you're likely to excel in dynamic environments that offer professional development opportunities.
                </p>
              )}
            </div>
          </div>
        </TabsContent>
        
        {/* Suggestions Tab */}
        <TabsContent value="suggestions" className="space-y-6">
          <div className="text-center mb-4">
            <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-amber-900/20 mb-4 backdrop-blur-sm">
              <Lightbulb className="h-6 w-6 text-amber-400" />
            </div>
            <h3 className="text-xl font-semibold text-gradient mb-1">Resume Improvements</h3>
            <p className="text-sm text-zinc-400">Actionable suggestions to enhance your profile</p>
          </div>
          
          <div className="animate-fade-in" style={{ animationDelay: "0.1s" }}>
            <div className="space-y-4 pl-2">
              {resumeSuggestions && resumeSuggestions.length > 0 ? (
                resumeSuggestions.map((suggestion, index) => (
                  <div 
                    key={index} 
                    className={`flex gap-3 items-start p-3 rounded-lg border ${getSeverityColor(suggestion.severity)}`}
                  >
                    {suggestion.severity === 'high' ? (
                      <AlertTriangle className="h-5 w-5 text-red-400 flex-shrink-0 mt-0.5" />
                    ) : (
                      <Lightbulb className="h-5 w-5 text-amber-400 flex-shrink-0 mt-0.5" />
                    )}
                    <div>
                      <div className="flex items-center mb-1">
                        <Badge variant="outline" className={`text-xs border-none bg-white/10 mr-2`}>
                          {suggestion.type}
                        </Badge>
                        <span className="text-xs">
                          {suggestion.severity === 'high' ? 'High Priority' : 
                           suggestion.severity === 'medium' ? 'Medium Priority' : 
                           'Low Priority'}
                        </span>
                      </div>
                      <p className="text-sm">{suggestion.text}</p>
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-sm text-zinc-500 text-center">No specific suggestions available</p>
              )}
            </div>
          </div>
          
          <Separator className="bg-zinc-800/50" />
          
          <div className="animate-fade-in" style={{ animationDelay: "0.2s" }}>
            <div className="flex items-center gap-2 mb-3">
              <TrendingUp className="h-4 w-4 text-blue-400" />
              <h4 className="font-medium text-sm text-zinc-400">How to Stand Out</h4>
            </div>
            <div className="space-y-3 pl-6">
              <p className="text-sm text-zinc-300">
                For <span className="text-white font-medium capitalize">{role}</span> roles, consider highlighting:
              </p>
              <ul className="list-disc pl-5 space-y-2 text-sm text-zinc-300">
                <li>Specific metrics and achievements that demonstrate your impact</li>
                <li>Collaborative projects that showcase your teamwork abilities</li>
                <li>Problem-solving examples that illustrate your approach to challenges</li>
                <li>Continuous learning efforts such as certifications or courses</li>
              </ul>
            </div>
          </div>
        </TabsContent>
        
        {/* Job Match Tab (Only shown if job description was provided) */}
        {jobMatch && (
          <TabsContent value="job-match" className="space-y-6">
            <div className="text-center mb-4">
              <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-green-900/20 mb-4 backdrop-blur-sm">
                <Briefcase className="h-6 w-6 text-green-400" />
              </div>
              <h3 className="text-xl font-semibold text-gradient mb-1">Job Match Analysis</h3>
              <p className="text-sm text-zinc-400">How your resume matches the job description</p>
            </div>
            
            <div className="flex flex-col items-center gap-4 mb-6">
              <div className="relative w-32 h-32 flex items-center justify-center">
                <svg className="w-full h-full" viewBox="0 0 100 100">
                  <circle 
                    cx="50" cy="50" r="45" 
                    fill="none" 
                    stroke="#334155" 
                    strokeWidth="8" 
                  />
                  <circle 
                    cx="50" cy="50" r="45" 
                    fill="none" 
                    stroke={jobMatch.match_percentage >= 70 ? "#059669" : jobMatch.match_percentage >= 50 ? "#d97706" : "#dc2626"} 
                    strokeWidth="8" 
                    strokeDasharray="282.7"
                    strokeDashoffset={282.7 - ((jobMatch.match_percentage / 100) * 282.7)}
                    strokeLinecap="round"
                    transform="rotate(-90 50 50)"
                  />
                </svg>
                <div className="absolute flex flex-col items-center">
                  <span className="text-3xl font-bold">{jobMatch.match_percentage}%</span>
                  <span className="text-xs text-zinc-400">match</span>
                </div>
              </div>
              <div className={`text-sm font-medium ${
                jobMatch.match_percentage >= 70 ? 'text-green-500' : 
                jobMatch.match_percentage >= 50 ? 'text-amber-500' : 
                'text-red-500'
              }`}>
                {jobMatch.match_percentage >= 70 ? 'Strong Match' : 
                 jobMatch.match_percentage >= 50 ? 'Moderate Match' : 
                 'Low Match'}
              </div>
            </div>
            
            <Separator className="bg-zinc-800/50" />
            
            <div className="animate-fade-in" style={{ animationDelay: "0.1s" }}>
              <div className="flex items-center gap-2 mb-3">
                <Award className="h-4 w-4 text-green-400" />
                <h4 className="font-medium text-sm text-zinc-400">Matching Skills</h4>
              </div>
              <div className="flex flex-wrap gap-2 pl-6">
                {jobMatch.matching_skills && jobMatch.matching_skills.length > 0 ? (
                  jobMatch.matching_skills.map((skill, index) => (
                    <Badge 
                      key={index} 
                      variant="secondary" 
                      className="capitalize py-1.5 px-3 bg-green-900/30 text-green-100 border border-green-800/30"
                    >
                      {skill}
                    </Badge>
                  ))
                ) : (
                  <p className="text-sm text-zinc-500">No matching skills found</p>
                )}
              </div>
            </div>
            
            <Separator className="bg-zinc-800/50" />
            
            <div className="animate-fade-in" style={{ animationDelay: "0.2s" }}>
              <div className="flex items-center gap-2 mb-3">
                <AlertTriangle className="h-4 w-4 text-red-400" />
                <h4 className="font-medium text-sm text-zinc-400">Missing Skills</h4>
              </div>
              <div className="flex flex-wrap gap-2 pl-6">
                {jobMatch.missing_skills && jobMatch.missing_skills.length > 0 ? (
                  jobMatch.missing_skills.map((skill, index) => (
                    <Badge 
                      key={index} 
                      variant="secondary" 
                      className="capitalize py-1.5 px-3 bg-red-900/30 text-red-100 border border-red-800/30"
                    >
                      {skill}
                    </Badge>
                  ))
                ) : (
                  <p className="text-sm text-green-400">No missing skills - great job!</p>
                )}
              </div>
              
              {jobMatch.missing_skills && jobMatch.missing_skills.length > 0 && (
                <div className="mt-4 p-4 rounded-lg bg-blue-900/10 border border-blue-900/20 text-sm text-blue-100">
                  <h5 className="font-medium mb-2">How to address skill gaps:</h5>
                  <ul className="list-disc pl-5 space-y-1 text-sm">
                    <li>Consider online courses to learn these skills</li>
                    <li>Showcase related skills or transferable knowledge</li>
                    <li>Highlight your ability to learn quickly</li>
                    <li>Mention any current learning efforts in these areas</li>
                  </ul>
                </div>
              )}
            </div>
          </TabsContent>
        )}
      </Tabs>
      
      <div className="mt-8 animate-fade-in" style={{ animationDelay: "0.4s" }}>
        <Button 
          className="w-full bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white py-2.5 shadow-lg shadow-blue-900/20 group transition-all"
          onClick={() => window.open(linkedInUrl, "_blank")}
        >
          <ExternalLink className="mr-2 h-4 w-4 transition-transform group-hover:translate-x-1" />
          Find Matching Jobs on LinkedIn
        </Button>
      </div>
    </Card>
  );
};

export default JobMatchResults;
