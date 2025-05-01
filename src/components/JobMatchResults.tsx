
import React from 'react';
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ExternalLink } from 'lucide-react';

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
    <Card className="p-6 w-full max-w-md mx-auto bg-secondary/30 border-zinc-800">
      <div className="text-center mb-4">
        <h3 className="text-lg font-medium text-gray-200">Your Profile Match</h3>
        <p className="text-sm text-gray-400">Based on your resume</p>
      </div>
      
      <div className="space-y-4">
        <div>
          <h4 className="font-medium text-sm mb-2 text-gray-400">Role</h4>
          <p className="text-base capitalize text-gray-200">{role || "Not found"}</p>
        </div>
        
        <div>
          <h4 className="font-medium text-sm mb-2 text-gray-400">Location</h4>
          <p className="text-base text-gray-200">{location || "Remote"}</p>
        </div>
        
        <div>
          <h4 className="font-medium text-sm mb-2 text-gray-400">Top Skills</h4>
          <div className="flex flex-wrap gap-2">
            {skills && skills.length > 0 ? (
              skills.map((skill, index) => (
                <Badge key={index} variant="secondary" className="capitalize bg-blue-900/40 text-blue-100">
                  {skill}
                </Badge>
              ))
            ) : (
              <p className="text-sm text-gray-400">No skills detected</p>
            )}
          </div>
        </div>
      </div>
      
      <div className="mt-6">
        <Button 
          className="w-full bg-blue-600 hover:bg-blue-700"
          onClick={() => window.open(linkedInUrl, "_blank")}
        >
          <ExternalLink className="mr-2 h-4 w-4" />
          Find Matching Jobs on LinkedIn
        </Button>
      </div>
    </Card>
  );
};

export default JobMatchResults;
