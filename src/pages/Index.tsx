
import { Card, CardContent } from "@/components/ui/card";
import ResumeParser from "@/components/ResumeParser";

const Index = () => {
  return (
    <div className="min-h-screen bg-gradient-to-b from-black to-zinc-900">
      <div className="container mx-auto py-12 px-4">
        <div className="text-center mb-12">
          <h1 className="text-3xl md:text-4xl font-bold text-gradient mb-2">
            Hire-AI: Resume Analyzer
          </h1>
          <p className="text-lg text-gray-400 max-w-2xl mx-auto">
            Upload your resume to find matching LinkedIn jobs tailored to your skills and experience
          </p>
        </div>

        <Card className="max-w-3xl mx-auto glass-morphism border-none">
          <CardContent className="p-6">
            <ResumeParser />
          </CardContent>
        </Card>

        <div className="mt-12 text-center text-sm text-gray-500">
          <p>Your data is processed locally and is not stored in any database.</p>
          <p className="mt-1">© 2025 Hire-AI. All rights reserved.</p>
        </div>
      </div>
    </div>
  );
};

export default Index;
