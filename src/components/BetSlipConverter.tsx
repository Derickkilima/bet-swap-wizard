
import { useState } from 'react';
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { useToast } from "@/components/ui/use-toast";

export const BetSlipConverter = () => {
  const { toast } = useToast();
  const [betSlipCode, setBetSlipCode] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [convertedCode, setConvertedCode] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!betSlipCode) {
      toast({
        title: "Missing Information",
        description: "Please enter a SportyBet slip code.",
        variant: "destructive",
      });
      return;
    }

    setIsLoading(true);
    // Simulate API call
    setTimeout(() => {
      // For demonstration, we'll just modify the input code slightly
      setConvertedCode(`BETPAWA-${betSlipCode}-converted`);
      toast({
        title: "Conversion Complete",
        description: "Your SportyBet slip has been converted to BetPawa format!",
      });
      setIsLoading(false);
    }, 1500);
  };

  return (
    <Card className="w-full max-w-md p-6 space-y-6 bg-white/80 backdrop-blur-sm shadow-lg border border-gray-200 rounded-xl animate-fadeIn">
      <div className="space-y-2 text-center">
        <h1 className="text-2xl font-bold text-betting-primary tracking-tight">
          SportyBet to BetPawa Converter
        </h1>
        <p className="text-sm text-gray-500">
          Convert your SportyBet slip code to BetPawa format
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="betSlipCode">SportyBet Slip Code</Label>
          <Input
            id="betSlipCode"
            placeholder="Enter your SportyBet slip code"
            value={betSlipCode}
            onChange={(e) => setBetSlipCode(e.target.value)}
            className="w-full transition-all duration-200"
          />
        </div>

        <Button 
          type="submit" 
          className="w-full bg-betting-primary hover:bg-betting-secondary transition-colors duration-200"
          disabled={isLoading}
        >
          {isLoading ? "Converting..." : "Convert to BetPawa"}
        </Button>
      </form>

      {convertedCode && (
        <div className="mt-6 space-y-2">
          <Label>BetPawa Slip Code</Label>
          <div className="p-4 bg-betting-primary/5 rounded-lg border border-betting-primary/10">
            <p className="text-betting-primary font-mono text-sm break-all">{convertedCode}</p>
          </div>
          <Button
            type="button"
            variant="outline"
            className="w-full mt-2"
            onClick={() => {
              navigator.clipboard.writeText(convertedCode);
              toast({
                title: "Copied!",
                description: "The BetPawa code has been copied to your clipboard.",
              });
            }}
          >
            Copy to Clipboard
          </Button>
        </div>
      )}
    </Card>
  );
};
