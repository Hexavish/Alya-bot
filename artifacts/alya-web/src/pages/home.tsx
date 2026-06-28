import { useEffect, useState } from "react";

const INVITE_LINK = import.meta.env.VITE_INVITE_LINK || "#invite";
const SUPPORT_LINK = import.meta.env.VITE_SUPPORT_SERVER || "#support";
import { motion, useScroll, useTransform } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { 
  Heart, Sparkles, Shield, Music, Gamepad2, Wrench, 
  Coins, Ticket, Gift, MessageSquare, ArrowUpCircle, 
  ScrollText, Bot, Users, Terminal, Server, Star, Zap
} from "lucide-react";
import mascotImg from "@/assets/alya-mascot.png";
import bgImg from "@/assets/dreamy-bg.png";

// Sakura Petals Effect
const SakuraPetals = () => {
  const [petals, setPetals] = useState<Array<{id: number, left: string, size: number, duration: number, delay: number}>>([]);

  useEffect(() => {
    const newPetals = Array.from({ length: 30 }).map((_, i) => ({
      id: i,
      left: `${Math.random() * 100}%`,
      size: Math.random() * 10 + 5,
      duration: Math.random() * 5 + 5,
      delay: Math.random() * 10
    }));
    setPetals(newPetals);
  }, []);

  return (
    <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
      {petals.map(petal => (
        <div
          key={petal.id}
          className="sakura-petal"
          style={{
            left: petal.left,
            width: `${petal.size}px`,
            height: `${petal.size}px`,
            animationDuration: `${petal.duration}s, ${petal.duration / 2}s`,
            animationDelay: `${petal.delay}s, ${petal.delay}s`
          }}
        />
      ))}
    </div>
  );
};

// Animated Counter component
const AnimatedCounter = ({ value, duration = 2 }: { value: number, duration?: number }) => {
  const [count, setCount] = useState(0);
  
  useEffect(() => {
    let startTime: number;
    let animationFrame: number;
    
    const animate = (timestamp: number) => {
      if (!startTime) startTime = timestamp;
      const progress = timestamp - startTime;
      const percentage = Math.min(progress / (duration * 1000), 1);
      
      // easeOutExpo
      const easeProgress = percentage === 1 ? 1 : 1 - Math.pow(2, -10 * percentage);
      
      setCount(Math.floor(easeProgress * value));
      
      if (percentage < 1) {
        animationFrame = requestAnimationFrame(animate);
      }
    };
    
    animationFrame = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(animationFrame);
  }, [value, duration]);
  
  return <>{count.toLocaleString()}</>;
};

// Features Data
const features = [
  { icon: Heart, title: "Welcome/Goodbye", desc: "Greet new friends with cute customized cards." },
  { icon: Shield, title: "Moderation", desc: "Keep your server safe with powerful tools." },
  { icon: Gamepad2, title: "Fun & Games", desc: "Minigames, reactions, and adorable interactions." },
  { icon: Wrench, title: "Utility", desc: "Helpful commands to manage everything." },
  { icon: Coins, title: "Economy", desc: "Global currency, shops, and daily rewards." },
  { icon: Music, title: "Music", desc: "High quality tunes for your late night calls." },
  { icon: Ticket, title: "Tickets", desc: "Beautiful support channels for your members." },
  { icon: Gift, title: "Giveaways", desc: "Host amazing events effortlessly." },
  { icon: MessageSquare, title: "Suggestions", desc: "Let your community share their ideas." },
  { icon: ArrowUpCircle, title: "Leveling & XP", desc: "Reward active members with cute roles." },
  { icon: ScrollText, title: "Logging", desc: "Track everything that happens silently." },
];

export default function Home() {
  const [stats, setStats] = useState({ status: 'Online', guilds: 0, users: 0, commands: 68, systems: 11 });
  const { scrollYProgress } = useScroll();
  const y = useTransform(scrollYProgress, [0, 1], [0, 200]);

  useEffect(() => {
    fetch('/api/bot-stats')
      .then(res => res.json())
      .then(data => {
        if (data) setStats(data);
      })
      .catch(() => {
        // Fallback already in state
      });
  }, []);

  // Force dark mode for the dreamy vibe
  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  return (
    <div className="min-h-screen bg-background relative overflow-hidden font-sans">
      <SakuraPetals />
      
      {/* Background Image with Overlay */}
      <div 
        className="fixed inset-0 z-[-1] bg-cover bg-center bg-no-repeat opacity-40 mix-blend-screen"
        style={{ backgroundImage: `url(${bgImg})` }}
      />
      <div className="fixed inset-0 z-[-1] bg-dreamy" />

      {/* 1. Navbar */}
      <nav className="fixed top-0 left-0 right-0 z-50 px-6 py-4 flex items-center justify-between backdrop-blur-md bg-background/50 border-b border-white/5">
        <div className="flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-primary" />
          <span className="font-serif font-bold text-xl tracking-wide text-primary">Alya</span>
        </div>
        <div className="flex gap-4">
          <Button variant="ghost" className="text-foreground/80 hover:text-primary hidden sm:inline-flex" asChild>
            <a href={SUPPORT_LINK}>Support</a>
          </Button>
          <Button className="bg-primary hover:bg-primary/90 text-primary-foreground rounded-full px-6 shadow-lg shadow-primary/20" asChild>
            <a href={INVITE_LINK}>Add to Discord</a>
          </Button>
        </div>
      </nav>

      {/* 2. Hero Section */}
      <section className="relative pt-32 pb-20 px-4 min-h-[90vh] flex flex-col items-center justify-center z-10">
        <div className="max-w-5xl mx-auto flex flex-col md:flex-row items-center gap-12">
          <motion.div 
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8, ease: "easeOut" }}
            className="flex-1 text-center md:text-left"
          >
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 border border-primary/20 text-primary text-sm font-medium mb-6">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-primary"></span>
              </span>
              v2.0 is live
            </div>
            <h1 className="text-5xl md:text-7xl font-extrabold mb-6 leading-tight text-glow text-white">
              Your server's <br/>
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-secondary">new best friend.</span>
            </h1>
            <p className="text-lg md:text-xl text-muted-foreground mb-8 max-w-lg mx-auto md:mx-0 font-medium">
              Alya is a cute, powerful, and fully-featured Discord bot designed to make your server feel like home. Moderation, music, economy, and more—all wrapped in a dreamy aesthetic.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center md:justify-start">
              <Button size="lg" className="bg-primary hover:bg-primary/90 text-primary-foreground rounded-full px-8 text-lg shadow-[0_0_20px_rgba(244,114,182,0.3)] transition-all hover:scale-105" asChild>
                <a href={INVITE_LINK}>Invite Alya</a>
              </Button>
              <Button size="lg" variant="outline" className="rounded-full px-8 text-lg border-primary/20 hover:bg-primary/10 hover:border-primary/40 transition-all" asChild>
                <a href="#features">See Features</a>
              </Button>
            </div>
          </motion.div>
          
          <motion.div 
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            style={{ y }}
            className="flex-1 relative max-w-md w-full"
          >
            <div className="absolute inset-0 bg-gradient-to-tr from-primary/20 to-secondary/20 rounded-full blur-3xl opacity-50 animate-pulse" />
            <img 
              src={mascotImg} 
              alt="Alya Mascot" 
              className="relative z-10 w-full h-auto drop-shadow-2xl animate-[sway_6s_ease-in-out_infinite_alternate]"
            />
          </motion.div>
        </div>
      </section>

      {/* 3. Stats Section */}
      <section className="py-12 border-y border-white/5 bg-black/20 backdrop-blur-sm relative z-10">
        <div className="max-w-6xl mx-auto px-4 grid grid-cols-2 md:grid-cols-4 gap-8">
          {[
            { label: "Servers", value: stats.guilds, icon: Server },
            { label: "Users", value: stats.users, icon: Users },
            { label: "Commands", value: stats.commands, icon: Terminal },
            { label: "Systems", value: stats.systems, icon: Bot }
          ].map((stat, i) => (
            <motion.div 
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
              className="text-center"
            >
              <div className="mx-auto w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center mb-3">
                <stat.icon className="w-6 h-6 text-primary" />
              </div>
              <h3 className="text-3xl font-bold text-white mb-1 font-serif">
                {stat.value > 0 ? <AnimatedCounter value={stat.value} /> : stat.value}
              </h3>
              <p className="text-sm text-muted-foreground uppercase tracking-wider font-semibold">{stat.label}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* 4. Features Grid */}
      <section id="features" className="py-24 px-4 relative z-10">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-5xl font-bold text-white mb-4 text-glow font-serif">Cute but Powerful</h2>
            <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
              Don't let the soft exterior fool you. Alya packs 11 distinct systems to manage, entertain, and grow your community.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {features.map((feature, i) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, scale: 0.9 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.05 }}
              >
                <Card className="bg-card/40 backdrop-blur-sm border-white/10 hover:border-primary/50 transition-all duration-300 card-glow h-full group">
                  <CardContent className="p-6">
                    <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center mb-4 group-hover:bg-primary/20 transition-colors">
                      <feature.icon className="w-5 h-5 text-primary" />
                    </div>
                    <h3 className="text-xl font-bold text-white mb-2">{feature.title}</h3>
                    <p className="text-muted-foreground text-sm leading-relaxed">{feature.desc}</p>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
            
            {/* CTA Card in Grid */}
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ delay: features.length * 0.05 }}
            >
              <Card className="bg-gradient-to-br from-primary/20 to-secondary/20 backdrop-blur-sm border-primary/30 h-full flex items-center justify-center text-center">
                <CardContent className="p-6">
                  <h3 className="text-xl font-bold text-white mb-2">And much more!</h3>
                  <Button variant="link" className="text-primary hover:text-primary/80">
                    View Documentation &rarr;
                  </Button>
                </CardContent>
              </Card>
            </motion.div>
          </div>
        </div>
      </section>

      {/* 5. Music Showcase */}
      <section className="py-24 px-4 relative z-10 bg-black/30 backdrop-blur-md border-y border-white/5">
        <div className="max-w-5xl mx-auto flex flex-col md:flex-row items-center gap-12">
          <motion.div 
            initial={{ opacity: 0, x: -30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            className="flex-1"
          >
            <div className="inline-flex items-center gap-2 text-primary font-medium mb-4">
              <Music className="w-5 h-5" /> <span>High Quality Audio</span>
            </div>
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4 font-serif">Late night study sessions, <br/>made perfect.</h2>
            <p className="text-muted-foreground text-lg mb-6">
              Alya comes with a fully-featured music system. Play your favorite lofi playlists, control playback with intuitive buttons, and enjoy crystal clear audio in your voice channels.
            </p>
            <ul className="space-y-3 mb-8">
              {['Supports Spotify, YouTube, Soundcloud', '24/7 Mode for premium servers', 'Audio filters (Bassboost, Nightcore, Vaporwave)'].map((item, i) => (
                <li key={i} className="flex items-center gap-3 text-muted-foreground">
                  <div className="w-1.5 h-1.5 rounded-full bg-secondary" />
                  {item}
                </li>
              ))}
            </ul>
          </motion.div>
          <motion.div 
            initial={{ opacity: 0, x: 30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            className="flex-1 w-full"
          >
            {/* Mock Discord Message */}
            <div className="bg-[#313338] rounded-xl p-4 shadow-2xl border border-white/5 max-w-md mx-auto">
              <div className="flex gap-4">
                <div className="w-10 h-10 rounded-full bg-primary/20 overflow-hidden flex-shrink-0">
                  <img src={mascotImg} alt="Alya" className="w-full h-full object-cover" />
                </div>
                <div className="flex-1">
                  <div className="flex items-baseline gap-2 mb-1">
                    <span className="font-medium text-white">Alya</span>
                    <span className="text-[10px] bg-[#5865F2] text-white px-1 rounded flex items-center gap-1"><Heart className="w-3 h-3"/> BOT</span>
                    <span className="text-xs text-[#949BA4]">Today at 2:00 AM</span>
                  </div>
                  <div className="bg-[#2B2D31] rounded-lg border border-l-4 border-l-primary border-transparent p-4 mt-2">
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <p className="text-xs font-bold text-primary mb-1">NOW PLAYING</p>
                        <p className="text-[#DBDEE1] font-medium leading-snug">Lofi Girl - chill beats to relax/study to</p>
                      </div>
                      <div className="w-12 h-12 rounded overflow-hidden">
                        <img src={bgImg} alt="Thumbnail" className="w-full h-full object-cover opacity-80" />
                      </div>
                    </div>
                    <div className="w-full bg-[#404249] h-1.5 rounded-full mt-4 mb-2 overflow-hidden">
                      <div className="bg-primary h-full w-1/3 rounded-full relative">
                        <div className="absolute right-0 top-1/2 -translate-y-1/2 w-2.5 h-2.5 bg-white rounded-full shadow" />
                      </div>
                    </div>
                    <div className="flex justify-between text-[10px] text-[#949BA4]">
                      <span>1:23:45</span>
                      <span>LIVE</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* 6. Leveling & Economy Showcase */}
      <section className="py-24 px-4 relative z-10">
        <div className="max-w-5xl mx-auto flex flex-col md:flex-row-reverse items-center gap-12">
          <motion.div 
            initial={{ opacity: 0, x: 30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            className="flex-1"
          >
            <div className="inline-flex items-center gap-2 text-primary font-medium mb-4">
              <Star className="w-5 h-5" /> <span>Engage Your Community</span>
            </div>
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4 font-serif">Level up, earn coins, <br/>and buy cute roles.</h2>
            <p className="text-muted-foreground text-lg mb-6">
              Keep your members active with a comprehensive global economy and leveling system. Daily rewards, mini-games, and custom rank cards make chatting rewarding.
            </p>
            <ul className="space-y-3 mb-8">
              {['Customizable rank cards and backgrounds', 'Global currency to buy roles and items', 'Coinflips, slots, and interactive games'].map((item, i) => (
                <li key={i} className="flex items-center gap-3 text-muted-foreground">
                  <div className="w-1.5 h-1.5 rounded-full bg-secondary" />
                  {item}
                </li>
              ))}
            </ul>
          </motion.div>
          <motion.div 
            initial={{ opacity: 0, x: -30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            className="flex-1 w-full"
          >
             {/* Mock Rank Card */}
             <div className="bg-[#2B2D31] rounded-2xl p-6 shadow-2xl border border-white/5 max-w-md mx-auto relative overflow-hidden">
                <div className="absolute top-0 right-0 w-32 h-32 bg-primary/20 rounded-full blur-3xl" />
                <div className="flex gap-6 items-center relative z-10">
                  <div className="w-24 h-24 rounded-full bg-[#1E1F22] border-4 border-[#2B2D31] overflow-hidden shadow-lg">
                    <img src={mascotImg} alt="User Avatar" className="w-full h-full object-cover scale-150 origin-top" />
                  </div>
                  <div className="flex-1">
                    <div className="flex justify-between items-baseline mb-2">
                      <h4 className="text-white text-xl font-bold">Dreamer</h4>
                      <div className="text-sm font-medium">
                        <span className="text-primary">LVL</span> <span className="text-white text-lg">15</span>
                      </div>
                    </div>
                    <div className="w-full bg-[#404249] h-3 rounded-full overflow-hidden mb-2">
                      <div className="bg-gradient-to-r from-primary to-secondary h-full w-3/4 rounded-full" />
                    </div>
                    <div className="flex justify-between text-xs text-[#949BA4] font-medium">
                      <span>15,340 XP</span>
                      <span>20,000 XP</span>
                    </div>
                  </div>
                </div>
             </div>
          </motion.div>
        </div>
      </section>

      {/* 7. Moderation / Security */}
      <section className="py-24 px-4 relative z-10 bg-black/20 backdrop-blur-sm border-t border-white/5">
        <div className="max-w-4xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <Shield className="w-12 h-12 text-primary mx-auto mb-6" />
            <h2 className="text-3xl md:text-5xl font-bold text-white mb-6 font-serif">Safe & Secure</h2>
            <p className="text-lg text-muted-foreground mb-10 max-w-2xl mx-auto">
              Behind the cute exterior is a powerful moderation engine. Auto-mod, detailed logging, anti-spam, and easily configurable permissions to keep your community safe while you sleep.
            </p>
            <div className="flex justify-center gap-4 flex-wrap">
              {['Auto-Moderation', 'Detailed Audit Logs', 'Raid Protection', 'Warning System'].map((tag) => (
                <div key={tag} className="px-4 py-2 rounded-full border border-white/10 bg-white/5 text-sm font-medium text-white flex items-center gap-2">
                  <Zap className="w-4 h-4 text-primary" /> {tag}
                </div>
              ))}
            </div>
          </motion.div>
        </div>
      </section>

      {/* 8. Bottom CTA */}
      <section className="py-32 px-4 relative z-10 text-center">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="max-w-2xl mx-auto"
        >
          <Sparkles className="w-12 h-12 text-primary mx-auto mb-6 animate-pulse" />
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-6 font-serif">Ready to meet Alya?</h2>
          <p className="text-xl text-muted-foreground mb-10">
            Join thousands of servers already using Alya to create magical, engaging communities.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button size="lg" className="bg-primary hover:bg-primary/90 text-primary-foreground rounded-full px-10 text-lg h-14 shadow-lg shadow-primary/20" asChild>
              <a href={INVITE_LINK}>Add to Discord</a>
            </Button>
            <Button size="lg" variant="secondary" className="rounded-full px-10 text-lg h-14 bg-secondary/10 hover:bg-secondary/20 text-secondary border border-secondary/20" asChild>
              <a href={SUPPORT_LINK}>Support Server</a>
            </Button>
          </div>
        </motion.div>
      </section>

      {/* 9. Footer */}
      <footer className="py-8 border-t border-white/5 bg-background relative z-10 text-center">
        <div className="flex items-center justify-center gap-2 mb-4">
          <Sparkles className="w-4 h-4 text-primary" />
          <span className="font-serif font-bold text-lg text-primary">Alya</span>
        </div>
        <p className="text-muted-foreground text-sm font-medium">
          Alya • Cute but powerful 🌸
        </p>
        <p className="text-muted-foreground/50 text-xs mt-2">
          Not affiliated with Discord.
        </p>
      </footer>
    </div>
  );
}
