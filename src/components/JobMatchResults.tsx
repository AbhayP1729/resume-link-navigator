
import React from 'react';
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ExternalLink, Briefcase, MapPin, Award } from 'lucide-react';
import { Separator } from "@/components/ui/separator";

interface JobMatchResultsProps {
  skills: string[];
  role: string;
  location: string;
}

const JobMatchResults: React.FC<JobMatchResultsProps> = ({ skills, role, location }) => {
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
    
    return `${baseUrl}${params.toString()}`;
  };

  const linkedInUrl = generateLinkedInUrl();

  return (
    <Card className="p-8 w-full max-w-md mx-auto bg-gradient-to-br from-zinc-900 to-black/60 border border-zinc-800/50 shadow-lg animate-fade-in">
      <div className="text-center mb-6">
        <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-blue-900/20 mb-4 backdrop-blur-sm">
          <Briefcase className="h-6 w-6 text-blue-400" />
        </div>
        <h3 className="text-xl font-semibold text-gradient mb-1">Your Profile Match</h3>
        <p className="text-sm text-zinc-400">Based on your resume analysis</p>
      </div>
      
      <div className="space-y-6">
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
      </div>
      
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
