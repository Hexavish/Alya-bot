import { Switch, Route, Router as WouterRouter } from "wouter";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { Layout } from "@/components/layout";

import Overview from "@/pages/overview";
import Guilds from "@/pages/guilds";
import Commands from "@/pages/commands";
import Economy from "@/pages/economy";
import Leveling from "@/pages/leveling";
import Suggestions from "@/pages/suggestions";
import Moderation from "@/pages/moderation";
import Tickets from "@/pages/tickets";
import Giveaways from "@/pages/giveaways";
import NotFound from "@/pages/not-found";

const queryClient = new QueryClient();

function Router() {
  return (
    <Switch>
      <Route path="/" component={Overview} />
      <Route path="/guilds" component={Guilds} />
      <Route path="/commands" component={Commands} />
      <Route path="/economy" component={Economy} />
      <Route path="/leveling" component={Leveling} />
      <Route path="/suggestions" component={Suggestions} />
      <Route path="/moderation" component={Moderation} />
      <Route path="/tickets" component={Tickets} />
      <Route path="/giveaways" component={Giveaways} />
      <Route component={NotFound} />
    </Switch>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <WouterRouter base={import.meta.env.BASE_URL.replace(/\/$/, "")}>
          <Layout>
            <Router />
          </Layout>
        </WouterRouter>
        <Toaster />
      </TooltipProvider>
    </QueryClientProvider>
  );
}

export default App;
