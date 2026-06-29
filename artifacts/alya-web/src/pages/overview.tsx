import { useEffect, useState } from "react";
import { Server, Users, Terminal, AlertTriangle, Ticket, Gift, Activity, Clock, Cpu, RotateCcw, Medal, Coins } from "lucide-react";
import { PageTransition } from "@/components/page-transition";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

function formatUptime(seconds: number) {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);
  return `${h}h ${m}m ${s}s`;
}

function truncateId(id: string) {
  if (!id) return "";
  return id.length > 6 ? id.substring(0, 6) + "..." : id;
}

export default function Overview() {
  const [stats, setStats] = useState<any>(null);
  const [economy, setEconomy] = useState<any[]>([]);
  const [leveling, setLeveling] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await fetch("/api/bot-stats");
        const data = await res.json();
        setStats(data);
        setLoading(false);
      } catch (err) {
        console.error(err);
      }
    };

    fetchStats();
    const int = setInterval(fetchStats, 10000);

    // Fetch top users
    fetch("/api/economy/leaderboard").then(r => r.json()).then(d => setEconomy(d.slice(0, 3))).catch(() => {});
    fetch("/api/leveling/leaderboard").then(r => r.json()).then(d => setLeveling(d.slice(0, 3))).catch(() => {});

    return () => clearInterval(int);
  }, []);

  const botStatus = stats?.botProcess?.status || "offline";
  const isOnline = botStatus === "running";

  return (
    <PageTransition className="space-y-8">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-white mb-2">System Overview</h1>
          <p className="text-muted-foreground">Real-time statistics and status of Alya.</p>
        </div>

        {loading ? (
          <Skeleton className="h-12 w-48 rounded-lg bg-card" />
        ) : (
          <div className="flex items-center gap-4 bg-card border border-white/5 p-3 rounded-lg shadow-lg">
            <div className="flex flex-col">
              <span className="text-xs font-semibold text-muted-foreground uppercase">Bot Status</span>
              <div className="flex items-center gap-2">
                <div className={`w-3 h-3 rounded-full ${isOnline ? "bg-green-500 shadow-[0_0_10px_#22c55e]" : "bg-red-500 shadow-[0_0_10px_#ef4444]"} animate-pulse`} />
                <span className="font-bold uppercase tracking-wider text-white">
                  {isOnline ? "ONLINE" : botStatus.toUpperCase()}
                </span>
              </div>
            </div>
            <div className="w-px h-8 bg-white/10" />
            <div className="flex flex-col">
              <span className="text-xs font-semibold text-muted-foreground uppercase">Uptime</span>
              <span className="font-mono text-sm text-white">{formatUptime(stats?.serverUptime || 0)}</span>
            </div>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        {[
          { label: "Guilds", value: stats?.guilds, icon: Server, color: "text-blue-400" },
          { label: "Users", value: stats?.users, icon: Users, color: "text-indigo-400" },
          { label: "Commands", value: stats?.commands, icon: Terminal, color: "text-primary" },
          { label: "Warnings", value: stats?.warnings, icon: AlertTriangle, color: "text-yellow-400" },
          { label: "Tickets", value: stats?.tickets, icon: Ticket, color: "text-emerald-400" },
          { label: "Giveaways", value: stats?.giveaways, icon: Gift, color: "text-purple-400" },
        ].map((stat, i) => (
          <Card key={i} className="card-glow border-white/5 bg-card">
            <CardContent className="p-6 flex flex-col items-center text-center">
              <stat.icon className={`w-8 h-8 mb-4 ${stat.color} opacity-80`} />
              <h3 className="text-3xl font-bold text-white mb-1 font-mono tracking-tight">
                {loading ? <Skeleton className="h-8 w-16 mx-auto bg-white/10" /> : stat.value?.toLocaleString() || "0"}
              </h3>
              <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">{stat.label}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="card-glow border-white/5 bg-card lg:col-span-1">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-white">
              <Activity className="w-5 h-5 text-primary" /> Process Info
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {loading ? (
              <div className="space-y-3"><Skeleton className="h-4 w-full" /><Skeleton className="h-4 w-full" /></div>
            ) : (
              <>
                <div className="flex justify-between items-center py-2 border-b border-white/5">
                  <span className="text-muted-foreground text-sm flex items-center gap-2"><Cpu className="w-4 h-4"/> PID</span>
                  <span className="font-mono text-white text-sm">{stats?.botProcess?.pid || "N/A"}</span>
                </div>
                <div className="flex justify-between items-center py-2 border-b border-white/5">
                  <span className="text-muted-foreground text-sm flex items-center gap-2"><RotateCcw className="w-4 h-4"/> Restarts</span>
                  <span className="font-mono text-white text-sm">{stats?.botProcess?.restartCount || 0}</span>
                </div>
                <div className="flex justify-between items-center py-2 border-b border-white/5">
                  <span className="text-muted-foreground text-sm flex items-center gap-2"><Clock className="w-4 h-4"/> Last Started</span>
                  <span className="font-mono text-white text-sm">
                    {stats?.botProcess?.lastStarted ? new Date(stats.botProcess.lastStarted).toLocaleTimeString() : "N/A"}
                  </span>
                </div>
                <div className="flex justify-between items-center py-2">
                  <span className="text-muted-foreground text-sm flex items-center gap-2"><Server className="w-4 h-4"/> Active Systems</span>
                  <span className="font-mono text-primary font-bold">{stats?.systems || 0}</span>
                </div>
              </>
            )}
          </CardContent>
        </Card>

        <Card className="card-glow border-white/5 bg-card lg:col-span-1">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-white">
              <Medal className="w-5 h-5 text-yellow-400" /> Top Ranked
            </CardTitle>
          </CardHeader>
          <CardContent>
             {leveling.length === 0 ? (
               <div className="text-sm text-muted-foreground">No leveling data available.</div>
             ) : (
               <div className="space-y-4">
                 {leveling.map((u, i) => (
                   <div key={i} className="flex items-center justify-between p-3 rounded-md bg-white/5 border border-white/5">
                     <div className="flex items-center gap-3">
                       <div className="w-8 h-8 rounded-full bg-yellow-400/20 text-yellow-400 flex items-center justify-center font-bold text-sm">
                         #{i + 1}
                       </div>
                       <div>
                         <p className="font-mono text-sm text-white">{truncateId(u.user_id)}</p>
                         <p className="text-xs text-muted-foreground">Lvl {u.level}</p>
                       </div>
                     </div>
                     <div className="text-right">
                       <p className="font-mono text-sm font-bold text-yellow-400">{u.xp.toLocaleString()} XP</p>
                     </div>
                   </div>
                 ))}
               </div>
             )}
          </CardContent>
        </Card>

        <Card className="card-glow border-white/5 bg-card lg:col-span-1">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-white">
              <Coins className="w-5 h-5 text-green-400" /> Top Wealthy
            </CardTitle>
          </CardHeader>
          <CardContent>
             {economy.length === 0 ? (
               <div className="text-sm text-muted-foreground">No economy data available.</div>
             ) : (
               <div className="space-y-4">
                 {economy.map((u, i) => (
                   <div key={i} className="flex items-center justify-between p-3 rounded-md bg-white/5 border border-white/5">
                     <div className="flex items-center gap-3">
                       <div className="w-8 h-8 rounded-full bg-green-400/20 text-green-400 flex items-center justify-center font-bold text-sm">
                         #{i + 1}
                       </div>
                       <div>
                         <p className="font-mono text-sm text-white">{truncateId(u.user_id)}</p>
                         <p className="text-xs text-muted-foreground">Wallet: {u.balance}</p>
                       </div>
                     </div>
                     <div className="text-right">
                       <p className="font-mono text-sm font-bold text-green-400">{(u.total || 0).toLocaleString()} 🪙</p>
                     </div>
                   </div>
                 ))}
               </div>
             )}
          </CardContent>
        </Card>

      </div>
    </PageTransition>
  );
}
