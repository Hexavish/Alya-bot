import { useState } from "react";
import { Search } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const commandCategories = [
  {
    name: "Moderation",
    color: "text-red-400",
    bg: "bg-red-400/10",
    commands: ["ban", "kick", "mute", "timeout", "warn", "clear", "slowmode", "lock", "role"]
  },
  {
    name: "Fun",
    color: "text-pink-400",
    bg: "bg-pink-400/10",
    commands: ["8ball", "coinflip", "dice", "rps", "meme", "joke", "cat", "dog", "hug", "slap", "ship", "rate", "avatar"]
  },
  {
    name: "Utility",
    color: "text-blue-400",
    bg: "bg-blue-400/10",
    commands: ["ping", "help", "remind", "poll", "embed", "calc", "timer"]
  },
  {
    name: "Economy",
    color: "text-yellow-400",
    bg: "bg-yellow-400/10",
    commands: ["balance", "daily", "work", "beg", "deposit", "withdraw", "pay", "shop", "inventory"]
  },
  {
    name: "Music",
    color: "text-purple-400",
    bg: "bg-purple-400/10",
    commands: ["play", "pause", "resume", "stop", "skip", "queue", "nowplaying", "volume", "loop"]
  },
  {
    name: "Leveling",
    color: "text-indigo-400",
    bg: "bg-indigo-400/10",
    commands: ["rank", "leaderboard", "setxp"]
  },
  {
    name: "Tickets",
    color: "text-cyan-400",
    bg: "bg-cyan-400/10",
    commands: ["ticket", "closeticket"]
  },
  {
    name: "Giveaway",
    color: "text-orange-400",
    bg: "bg-orange-400/10",
    commands: ["gcreate", "gend", "greroll"]
  },
  {
    name: "Suggestions",
    color: "text-emerald-400",
    bg: "bg-emerald-400/10",
    commands: ["suggest", "approve", "deny"]
  },
  {
    name: "Welcome",
    color: "text-teal-400",
    bg: "bg-teal-400/10",
    commands: ["setwelcome", "setgoodbye", "setautorole"]
  },
  {
    name: "Logging",
    color: "text-slate-400",
    bg: "bg-slate-400/10",
    commands: ["setlog"]
  }
];

export default function Commands() {
  const [search, setSearch] = useState("");

  const filteredCategories = commandCategories.map(cat => ({
    ...cat,
    commands: cat.commands.filter(cmd => cmd.toLowerCase().includes(search.toLowerCase()))
  })).filter(cat => cat.commands.length > 0);

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-white mb-2">Bot Commands</h1>
          <p className="text-muted-foreground">Browse all 68 slash commands available in Alya.</p>
        </div>
        <div className="relative w-full md:w-72">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input 
            placeholder="Search commands..." 
            className="pl-9 bg-card/50 border-white/10 text-white placeholder:text-muted-foreground/50 focus-visible:ring-primary"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
        {filteredCategories.map((category) => (
          <Card key={category.name} className="border-white/5 bg-card/30 card-glow h-full">
            <CardHeader className="pb-3 border-b border-white/5">
              <CardTitle className="text-lg flex items-center gap-2">
                <div className={`w-3 h-3 rounded-full ${category.bg} border border-current ${category.color}`} />
                <span className="text-white">{category.name}</span>
                <Badge variant="secondary" className="ml-auto bg-white/5 text-muted-foreground">
                  {category.commands.length}
                </Badge>
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-4">
              <div className="flex flex-wrap gap-2">
                {category.commands.map(cmd => (
                  <div key={cmd} className="px-2.5 py-1 rounded bg-black/40 border border-white/5 font-mono text-sm text-muted-foreground hover:text-white hover:border-white/20 transition-colors cursor-default">
                    /{cmd}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        ))}
        {filteredCategories.length === 0 && (
          <div className="col-span-full py-12 text-center text-muted-foreground">
            No commands found matching "{search}"
          </div>
        )}
      </div>
    </div>
  );
}
