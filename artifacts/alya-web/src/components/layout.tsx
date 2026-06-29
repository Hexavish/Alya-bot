import { useEffect, useState } from "react";
import { Link, useLocation } from "wouter";
import { 
  LayoutDashboard, Server, Command, 
  Coins, TrendingUp, MessageSquare, 
  AlertTriangle, Ticket, Gift,
  Activity, ExternalLink, Menu
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";

const INVITE_LINK = import.meta.env.VITE_INVITE_LINK || "#invite";

function SidebarNav({ pathname, onClick }: { pathname: string, onClick?: () => void }) {
  const navItems = [
    { title: "Overview", href: "/", icon: LayoutDashboard, section: "General" },
    { title: "Guilds", href: "/guilds", icon: Server, section: "Bot Management" },
    { title: "Commands", href: "/commands", icon: Command, section: "Bot Management" },
    { title: "Economy", href: "/economy", icon: Coins, section: "Community" },
    { title: "Leveling", href: "/leveling", icon: TrendingUp, section: "Community" },
    { title: "Suggestions", href: "/suggestions", icon: MessageSquare, section: "Community" },
    { title: "Warnings", href: "/moderation", icon: AlertTriangle, section: "Moderation" },
    { title: "Tickets", href: "/tickets", icon: Ticket, section: "Moderation" },
    { title: "Giveaways", href: "/giveaways", icon: Gift, section: "Moderation" },
  ];

  const sections = Array.from(new Set(navItems.map(i => i.section)));

  return (
    <nav className="space-y-6">
      {sections.map(section => (
        <div key={section}>
          <h4 className="px-4 text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">
            {section}
          </h4>
          <div className="space-y-1">
            {navItems.filter(i => i.section === section).map(item => {
              const active = pathname === item.href;
              return (
                <Link key={item.href} href={item.href} onClick={onClick} className={`flex items-center gap-3 px-4 py-2 text-sm font-medium rounded-md transition-colors ${active ? 'bg-primary/10 text-primary border border-primary/20' : 'text-foreground/70 hover:text-foreground hover:bg-white/5'}`}>
                  <item.icon className={`w-4 h-4 ${active ? 'text-primary' : 'text-muted-foreground'}`} />
                  {item.title}
                </Link>
              );
            })}
          </div>
        </div>
      ))}
    </nav>
  );
}

export function Layout({ children }: { children: React.ReactNode }) {
  const [location] = useLocation();
  const [ping, setPing] = useState<{ status: string, bot: any } | null>(null);

  useEffect(() => {
    const fetchPing = () => {
      fetch('/api/ping')
        .then(res => res.json())
        .then(data => setPing(data))
        .catch(() => setPing(null));
    };
    fetchPing();
    const int = setInterval(fetchPing, 10000);
    return () => clearInterval(int);
  }, []);

  const botStatus = ping?.bot?.status || "offline";
  const statusColor = botStatus === "running" ? "bg-green-500" : botStatus === "starting" || botStatus === "restarting" ? "bg-yellow-500" : "bg-red-500";

  return (
    <div className="min-h-screen bg-background flex flex-col md:flex-row">
      {/* Mobile Topbar */}
      <div className="md:hidden flex items-center justify-between p-4 border-b border-white/5 bg-card z-50 sticky top-0">
        <div className="flex items-center gap-2">
          <span className="font-bold text-xl text-primary font-mono tracking-tighter">ALYA</span>
          <div className="flex items-center gap-1.5 px-2 py-0.5 rounded bg-black/40 border border-white/5 text-[10px] uppercase font-bold tracking-wider">
            <div className={`w-1.5 h-1.5 rounded-full ${statusColor} animate-pulse`} />
            <span className="text-muted-foreground">{botStatus}</span>
          </div>
        </div>
        <Sheet>
          <SheetTrigger asChild>
            <Button variant="ghost" size="icon"><Menu className="w-5 h-5" /></Button>
          </SheetTrigger>
          <SheetContent side="left" className="w-[240px] bg-muted border-white/5 p-4 pt-12">
            <SidebarNav pathname={location} />
          </SheetContent>
        </Sheet>
      </div>

      {/* Desktop Sidebar */}
      <aside className="hidden md:flex flex-col w-64 bg-muted border-r border-white/5 h-screen sticky top-0 overflow-y-auto">
        <div className="p-6 border-b border-white/5">
          <Link href="/" className="flex items-center gap-3">
            <div className="w-8 h-8 rounded bg-gradient-to-br from-primary to-secondary flex items-center justify-center shadow-[0_0_15px_rgba(244,114,182,0.3)]">
              <Activity className="w-4 h-4 text-white" />
            </div>
            <span className="font-bold text-2xl text-white font-mono tracking-tighter">ALYA</span>
          </Link>
        </div>
        <div className="p-4 flex-1">
          <SidebarNav pathname={location} />
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col min-w-0">
        {/* Top Header */}
        <header className="hidden md:flex h-16 items-center justify-between px-8 border-b border-white/5 bg-background/50 backdrop-blur-sm sticky top-0 z-40">
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 px-3 py-1 rounded-md bg-black/40 border border-white/5 text-xs font-bold uppercase tracking-widest text-muted-foreground">
              <div className={`w-2 h-2 rounded-full ${statusColor} shadow-[0_0_8px_currentColor]`} />
              {botStatus}
            </div>
          </div>
          <Button size="sm" className="bg-primary hover:bg-primary/90 text-primary-foreground shadow-[0_0_15px_rgba(244,114,182,0.2)]" asChild>
            <a href={INVITE_LINK} target="_blank" rel="noopener noreferrer" className="flex items-center gap-2">
              Add to Discord <ExternalLink className="w-4 h-4" />
            </a>
          </Button>
        </header>

        {/* Content Area */}
        <div className="p-4 md:p-8 flex-1 overflow-x-hidden">
          {children}
        </div>
      </main>
    </div>
  );
}
