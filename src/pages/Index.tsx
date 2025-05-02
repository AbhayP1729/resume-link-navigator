
import { Card, CardContent } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import ResumeParser from "@/components/ResumeParser";

const Index = () => {
  return (
    <div className="min-h-screen bg-gradient-to-b from-black via-zinc-900 to-[#0c1120]">
      <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPjxkZWZzPjxwYXR0ZXJuIGlkPSJncmlkIiB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHBhdHRlcm5Vbml0cz0idXNlclNwYWNlT25Vc2UiPjxwYXRoIGQ9Ik0gNDAgMCBMIDAgMCAwIDQwIiBmaWxsPSJub25lIiBzdHJva2U9IiMzMTM1NDQiIHN0cm9rZS13aWR0aD0iMC41Ii8+PC9wYXR0ZXJuPjwvZGVmcz48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSJ1cmwoI2dyaWQpIiBvcGFjaXR5PSIwLjEiLz48L3N2Zz4=')] opacity-40 pointer-events-none"></div>
      
      <div className="container relative z-10 mx-auto py-16 px-4">
        <div className="text-center mb-12 animate-fade-in">
          <div className="inline-block mb-6 relative">
            <div className="absolute -inset-1 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg blur opacity-20"></div>
            <h1 className="relative px-7 py-2 bg-black/50 rounded-lg text-4xl md:text-5xl font-extrabold text-gradient mb-2">
              Hire-AI: Resume Analyzer
            </h1>
          </div>
          <p className="text-lg text-blue-100/80 max-w-2xl mx-auto animate-fade-in" style={{ animationDelay: "0.2s" }}>
            Upload your resume to find matching LinkedIn jobs tailored to your skills and experience
          </p>
          
          <div className="flex items-center justify-center mt-6" style={{ animationDelay: "0.3s" }}>
            <span className="h-px w-8 bg-blue-700/50"></span>
            <span className="px-3 text-blue-400/70 text-sm">AI-POWERED MATCHING</span>
            <span className="h-px w-8 bg-blue-700/50"></span>
          </div>
        </div>

        <Card className="max-w-3xl mx-auto glass-morphism border-none card-hover animate-fade-in" style={{ animationDelay: "0.4s" }}>
          <CardContent className="p-8">
            <ResumeParser />
          </CardContent>
        </Card>

        <div className="mt-12 text-center animate-fade-in" style={{ animationDelay: "0.6s" }}>
          <Separator className="mb-6 max-w-md mx-auto bg-blue-900/30" />
          <p className="text-sm text-blue-300/50">Your data is processed locally and is not stored in any database.</p>
          <p className="mt-1 text-sm text-blue-300/50">© 2025 Hire-AI. All rights reserved.</p>
        </div>
      </div>
    </div>
  );
};

export default Index;
