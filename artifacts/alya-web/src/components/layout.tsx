import { ReactNode } from "react";
import { Link, useLocation } from "wouter";
import { Sparkles, TerminalSquare, LayoutDashboard, ExternalLink } from "lucide-react";
import { Button } from "@/components/ui/button";

const INVITE_LINK = import.meta.env.VITE_INVITE_LINK || "#invite";

export function Layout({ children }: { children: ReactNode }) {
  const [location] = useLocation();

  return (
    <div className="min-h-[100dvh] bg-discord-dark flex flex-col font-sans text-foreground">
      <nav className="sticky top-0 z-50 glass-panel border-b border-white/5">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-8">
              <Link href="/" className="flex items-center gap-2 group">
                <Sparkles className="w-5 h-5 text-primary group-hover:text-glow-pink transition-all" />
                <span className="font-bold text-xl tracking-tight text-white group-hover:text-glow-pink transition-all">Alya</span>
              </Link>
              <div className="hidden md:flex items-center gap-1">
                <Link href="/">
                  <Button variant={location === "/" ? "secondary" : "ghost"} size="sm" className="gap-2 text-muted-foreground hover:text-white">
                    <LayoutDashboard className="w-4 h-4" />
                    Dashboard
                  </Button>
                </Link>
                <Link href="/commands">
                  <Button variant={location === "/commands" ? "secondary" : "ghost"} size="sm" className="gap-2 text-muted-foreground hover:text-white">
                    <TerminalSquare className="w-4 h-4" />
                    Commands
                  </Button>
                </Link>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <Button className="bg-primary hover:bg-primary/90 text-primary-foreground gap-2 rounded-md shadow-lg shadow-primary/20" asChild>
                <a href={INVITE_LINK} target="_blank" rel="noopener noreferrer">
                  Add to Discord <ExternalLink className="w-4 h-4" />
                </a>
              </Button>
            </div>
          </div>
        </div>
      </nav>
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>
    </div>
  );
}
