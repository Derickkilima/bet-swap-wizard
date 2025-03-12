
import { useState } from 'react';
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useToast } from "@/components/ui/use-toast";

const BETTING_COMPANIES = [
  { id: 'betway', name: 'Betway' },
  { id: '1xbet', name: '1xBet' },
  { id: 'sportybet', name: 'SportyBet' },
  { id: 'sportpesa', name: 'SportPesa' },
  { id: 'betpawa', name: 'BetPawa' },
  { id: 'paripesa', name: 'PariPesa' },
];

export const BetSlipConverter = () => {
  const { toast } = useToast();
  const [betSlipCode, setBetSlipCode] = useState('');
  const [targetCompany, setTargetCompany] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!betSlipCode || !targetCompany) {
      toast({
        title: "Missing Information",
        description: "Please enter both a bet slip code and select a target company.",
        variant: "destructive",
      });
      return;
    }

    setIsLoading(true);
    // Simulate API call
    setTimeout(() => {
      toast({
        title: "Coming Soon",
        description: "The conversion feature will be available soon!",
      });
      setIsLoading(false);
    }, 1500);
  };

  return (
    <Card className="w-full max-w-md p-6 space-y-6 bg-white/80 backdrop-blur-sm shadow-lg border border-gray-200 rounded-xl animate-fadeIn">
      <div className="space-y-2 text-center">
        <h1 className="text-2xl font-bold text-betting-primary tracking-tight">
          Bet Slip Converter
        </h1>
        <p className="text-sm text-gray-500">
          Enter your bet slip code and select your target platform
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="betSlipCode">Bet Slip Code</Label>
          <Input
            id="betSlipCode"
            placeholder="Enter your bet slip code"
            value={betSlipCode}
            onChange={(e) => setBetSlipCode(e.target.value)}
            className="w-full transition-all duration-200"
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="targetCompany">Target Company</Label>
          <Select onValueChange={setTargetCompany}>
            <SelectTrigger className="w-full">
              <SelectValue placeholder="Select target betting company" />
            </SelectTrigger>
            <SelectContent>
              {BETTING_COMPANIES.map((company) => (
                <SelectItem key={company.id} value={company.id}>
                  {company.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <Button 
          type="submit" 
          className="w-full bg-betting-primary hover:bg-betting-secondary transition-colors duration-200"
          disabled={isLoading}
        >
          {isLoading ? "Converting..." : "Convert Bet Slip"}
        </Button>
      </form>
    </Card>
  );
};
