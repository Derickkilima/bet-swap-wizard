
import { BetSlipConverter } from "@/components/BetSlipConverter";

const Index = () => {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-betting-primary to-betting-secondary p-4">
      <div className="max-w-4xl w-full mx-auto">
        <BetSlipConverter />
      </div>
    </div>
  );
};

export default Index;
