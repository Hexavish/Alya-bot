import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { 
  Server, Users, Terminal, Bot, Zap, Ticket, Gift, AlertTriangle, Shield,
  Activity, Clock, RefreshCw, Cpu
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";

interface BotProcess {
  status: "running" | "starting" | "restarting" | "stopped";
  restartCount: number;
  lastStarted: string | null;
  pid: number | null;
}

interface BotStats {
  guilds: number;
  users: number;
  tickets: number;
  giveaways: number;
  warnings: number;
  levels: number;
  commands: number;
  systems: number;
  serverUptime: number;
  botProcess: BotProcess;
}

const formatUptime = (seconds: number) => {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);
  
  if (h > 0) return `${h}h ${m}m ${s}s`;
  if (m > 0) return `${m}m ${s}s`;
  return `${s}s`;
};

const getStatusColor = (status: string) => {
  switch (status) {
    case "running": return "text-green-500 bg-green-500/10 border-green-500/20";
    case "starting":
    case "restarting": return "text-yellow-500 bg-yellow-500/10 border-yellow-500/20";
    case "stopped": return "text-red-500 bg-red-500/10 border-red-500/20";
    default: return "text-muted-foreground bg-muted border-border";
  }
};

const AnimatedNumber = ({ value }: { value: number }) => {
  return (
    <motion.span
      key={value}
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="inline-block"
    >
      {value.toLocaleString()}
    </motion.span>
  );
};

export default function Dashboard() {
  const [stats, setStats] = useState<BotStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await fetch('/api/bot-stats');
        if (res.ok) {
          const data = await res.json();
          setStats(data);
        }
      } catch (e) {
        console.error("Failed to fetch stats", e);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
    const interval = setInterval(fetchStats, 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-white mb-2">Bot Dashboard</h1>
          <p className="text-muted-foreground flex items-center gap-2">
            <Activity className="w-4 h-4 text-primary" /> 
            Bot is running inside this server natively.
          </p>
        </div>

        {loading ? (
          <Skeleton className="w-48 h-10 rounded-full" />
        ) : stats ? (
          <div className={`flex items-center gap-3 px-4 py-2 rounded-full border ${getStatusColor(stats.botProcess.status)}`}>
            <div className={`w-3 h-3 rounded-full ${stats.botProcess.status === 'running' ? 'bg-green-500 animate-pulse' : stats.botProcess.status === 'stopped' ? 'bg-red-500' : 'bg-yellow-500 animate-pulse'}`} />
            <span className="font-mono font-semibold uppercase tracking-wider text-sm">
              {stats.botProcess.status}
            </span>
          </div>
        ) : null}
      </div>

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[1,2,3].map(i => <Skeleton key={i} className="h-32 rounded-xl" />)}
        </div>
      ) : stats ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          <Card className="card-glow border-white/5 bg-card/50">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Servers</CardTitle>
              <Server className="w-4 h-4 text-primary" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-white"><AnimatedNumber value={stats.guilds} /></div>
            </CardContent>
          </Card>
          <Card className="card-glow border-white/5 bg-card/50">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Users</CardTitle>
              <Users className="w-4 h-4 text-secondary" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-white"><AnimatedNumber value={stats.users} /></div>
            </CardContent>
          </Card>
          <Card className="card-glow border-white/5 bg-card/50">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Commands Run</CardTitle>
              <Terminal className="w-4 h-4 text-blue-400" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-white"><AnimatedNumber value={stats.commands} /></div>
            </CardContent>
          </Card>
          <Card className="card-glow border-white/5 bg-card/50">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Total Tickets</CardTitle>
              <Ticket className="w-4 h-4 text-amber-400" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-white"><AnimatedNumber value={stats.tickets} /></div>
            </CardContent>
          </Card>
          <Card className="card-glow border-white/5 bg-card/50">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Giveaways</CardTitle>
              <Gift className="w-4 h-4 text-pink-400" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-white"><AnimatedNumber value={stats.giveaways} /></div>
            </CardContent>
          </Card>
          <Card className="card-glow border-white/5 bg-card/50">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Warnings Issued</CardTitle>
              <AlertTriangle className="w-4 h-4 text-red-400" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-white"><AnimatedNumber value={stats.warnings} /></div>
            </CardContent>
          </Card>
        </div>
      ) : null}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <Card className="border-white/5 bg-card/30">
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <Cpu className="w-5 h-5 text-primary" /> Process Information
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {loading ? (
              <div className="space-y-4">
                <Skeleton className="h-6 w-3/4" />
                <Skeleton className="h-6 w-1/2" />
                <Skeleton className="h-6 w-2/3" />
              </div>
            ) : stats ? (
              <>
                <div className="flex justify-between items-center py-2 border-b border-white/5">
                  <div className="flex items-center gap-2 text-muted-foreground">
                    <Clock className="w-4 h-4" /> Server Uptime
                  </div>
                  <div className="font-mono text-white">{formatUptime(stats.serverUptime)}</div>
                </div>
                <div className="flex justify-between items-center py-2 border-b border-white/5">
                  <div className="flex items-center gap-2 text-muted-foreground">
                    <RefreshCw className="w-4 h-4" /> Restarts
                  </div>
                  <div className="font-mono text-white">{stats.botProcess.restartCount}</div>
                </div>
                <div className="flex justify-between items-center py-2 border-b border-white/5">
                  <div className="flex items-center gap-2 text-muted-foreground">
                    <Terminal className="w-4 h-4" /> Process ID
                  </div>
                  <div className="font-mono text-white">{stats.botProcess.pid || 'N/A'}</div>
                </div>
              </>
            ) : null}
          </CardContent>
        </Card>

        <Card className="border-white/5 bg-card/30">
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <Bot className="w-5 h-5 text-secondary" /> Active Systems
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {['Moderation', 'Fun', 'Utility', 'Economy', 'Music', 'Leveling', 'Tickets', 'Giveaway', 'Suggestions', 'Welcome', 'Logging'].map((sys, i) => (
                <Badge key={sys} variant="secondary" className="bg-secondary/10 text-secondary hover:bg-secondary/20 transition-colors px-3 py-1 text-sm font-medium border-secondary/20">
                  {sys}
                </Badge>
              ))}
            </div>
            <p className="text-muted-foreground text-sm mt-6">
              Alya supports {stats?.systems || 11} modular systems. They are initialized and running inside the Discord child process.
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
