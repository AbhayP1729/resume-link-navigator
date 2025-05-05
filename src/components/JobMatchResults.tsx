
import React, { useState } from 'react';
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ExternalLink, Briefcase, MapPin, Award, BookOpen, Sparkles, TrendingUp, Lightbulb, ChevronDown, ChevronUp, Clock } from 'lucide-react';
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

interface JobMatchResultsProps {
  skills: string[];
  role: string;
  location: string;
  experienceYears: number | null;
  education: string[];
  interests: Interest[];
  growthPotential: GrowthPotential;
  resumeSuggestions: string[];
}

const JobMatchResults: React.FC<JobMatchResultsProps> = ({ 
  skills, 
  role, 
  location,
  experienceYears,
  education,
  interests,
  growthPotential,
  resumeSuggestions
}) => {
  const [showSuggestions, setShowSuggestions] = useState(false);
  
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
    if (experienceYears) {
      if (experienceYears < 2) {
        params.append("f_E", "1"); // Entry level
      } else if (experienceYears < 5) {
        params.append("f_E", "2"); // Associate
      } else if (experienceYears < 10) {
        params.append("f_E", "3"); // Mid-Senior level
      } else {
        params.append("f_E", "4"); // Director
      }
    }
    
    return `${baseUrl}${params.toString()}`;
  };

  const linkedInUrl = generateLinkedInUrl();

  return (
    <Card className="p-6 w-full max-w-md mx-auto bg-gradient-to-br from-zinc-900 to-black/60 border border-zinc-800/50 shadow-lg animate-fade-in">
      <Tabs defaultValue="profile" className="w-full">
        <TabsList className="grid w-full grid-cols-3 mb-4">
          <TabsTrigger value="profile">Profile</TabsTrigger>
          <TabsTrigger value="personality">Insights</TabsTrigger>
          <TabsTrigger value="suggestions">Improve</TabsTrigger>
        </TabsList>
        
        <TabsContent value="profile" className="space-y-6">
          <div className="text-center mb-4">
            <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-blue-900/20 mb-4 backdrop-blur-sm">
              <Briefcase className="h-6 w-6 text-blue-400" />
            </div>
            <h3 className="text-xl font-semibold text-gradient mb-1">Professional Profile</h3>
            <p className="text-sm text-zinc-400">Based on your resume analysis</p>
          </div>
          
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
            <p className="text-lg text-white pl-6">
              {experienceYears ? `${experienceYears} years` : "Not specified"}
            </p>
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
                <ul className="space-y-1 text-white">
                  {education.map((edu, index) => (
                    <li key={index} className="text-sm">{edu}</li>
                  ))}
                </ul>
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
        </TabsContent>
        
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
        
        <TabsContent value="suggestions" className="space-y-6">
          <div className="text-center mb-4">
            <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-amber-900/20 mb-4 backdrop-blur-sm">
              <Lightbulb className="h-6 w-6 text-amber-400" />
            </div>
            <h3 className="text-xl font-semibold text-gradient mb-1">Resume Improvements</h3>
            <p className="text-sm text-zinc-400">Suggestions to enhance your profile</p>
          </div>
          
          <div className="animate-fade-in" style={{ animationDelay: "0.1s" }}>
            <div className="space-y-4 pl-2">
              {resumeSuggestions && resumeSuggestions.length > 0 ? (
                resumeSuggestions.map((suggestion, index) => (
                  <div key={index} className="flex gap-3 items-start p-3 rounded-lg bg-zinc-800/30 border border-zinc-700/30">
                    <div className="min-w-[24px] h-6 flex items-center justify-center rounded-full bg-amber-900/30 text-amber-400">
                      {index + 1}
                    </div>
                    <p className="text-sm text-zinc-300">{suggestion}</p>
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
