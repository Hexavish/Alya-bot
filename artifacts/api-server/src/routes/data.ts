import { Router } from "express";
import Database from "better-sqlite3";
import path from "path";
import { fileURLToPath } from "url";

const router = Router();

const dbPath = path.resolve(
  fileURLToPath(import.meta.url),
  "../../../../../alya.db"
);

function db() {
  return new Database(dbPath, { readonly: true, fileMustExist: true });
}

function safeQuery<T>(fn: () => T, fallback: T): T {
  try { return fn(); } catch { return fallback; }
}

// GET /api/guilds - all guilds with config flags
router.get("/guilds", (_req, res) => {
  const result = safeQuery(() => {
    const conn = db();
    const guilds = conn.prepare(`
      SELECT g.guild_id,
             g.welcome_enabled, g.goodbye_enabled,
             g.log_channel IS NOT NULL AS has_logging,
             g.suggestion_channel IS NOT NULL AS has_suggestions,
             g.ticket_category IS NOT NULL AS has_tickets,
             (SELECT COUNT(*) FROM users u WHERE u.guild_id = g.guild_id) AS member_count,
             (SELECT COUNT(*) FROM warnings w WHERE w.guild_id = g.guild_id) AS warning_count,
             (SELECT COUNT(*) FROM tickets t WHERE t.guild_id = g.guild_id) AS ticket_count
      FROM guilds g
      ORDER BY member_count DESC
    `).all();
    conn.close();
    return guilds;
  }, []);
  res.json(result);
});

// GET /api/economy/leaderboard - top 10 by total balance
router.get("/economy/leaderboard", (_req, res) => {
  const result = safeQuery(() => {
    const conn = db();
    const rows = conn.prepare(`
      SELECT user_id, guild_id,
             balance, bank,
             (balance + bank) AS total
      FROM users
      ORDER BY total DESC
      LIMIT 10
    `).all();
    conn.close();
    return rows;
  }, []);
  res.json(result);
});

// GET /api/leveling/leaderboard - top 10 by XP
router.get("/leveling/leaderboard", (_req, res) => {
  const result = safeQuery(() => {
    const conn = db();
    const rows = conn.prepare(`
      SELECT user_id, guild_id, xp, level
      FROM users
      ORDER BY xp DESC
      LIMIT 10
    `).all();
    conn.close();
    return rows;
  }, []);
  res.json(result);
});

// GET /api/tickets - all tickets with counts
router.get("/tickets", (_req, res) => {
  const result = safeQuery(() => {
    const conn = db();
    const list = conn.prepare(`
      SELECT id, guild_id, user_id, status, created_at, subject
      FROM tickets
      ORDER BY created_at DESC
      LIMIT 50
    `).all();
    const open = (conn.prepare("SELECT COUNT(*) AS c FROM tickets WHERE status='open'").get() as {c:number}).c;
    const closed = (conn.prepare("SELECT COUNT(*) AS c FROM tickets WHERE status='closed'").get() as {c:number}).c;
    conn.close();
    return { list, open, closed };
  }, { list: [], open: 0, closed: 0 });
  res.json(result);
});

// GET /api/giveaways - all giveaways
router.get("/giveaways", (_req, res) => {
  const result = safeQuery(() => {
    const conn = db();
    const list = conn.prepare(`
      SELECT id, guild_id, prize, winners, ends_at, ended,
             length(entries) AS entry_bytes
      FROM giveaways
      ORDER BY ends_at DESC
      LIMIT 30
    `).all();
    const active = (conn.prepare("SELECT COUNT(*) AS c FROM giveaways WHERE ended=0").get() as {c:number}).c;
    const completed = (conn.prepare("SELECT COUNT(*) AS c FROM giveaways WHERE ended=1").get() as {c:number}).c;
    conn.close();
    return { list, active, completed };
  }, { list: [], active: 0, completed: 0 });
  res.json(result);
});

// GET /api/warnings - recent warnings
router.get("/warnings", (_req, res) => {
  const result = safeQuery(() => {
    const conn = db();
    const list = conn.prepare(`
      SELECT id, user_id, guild_id, moderator_id, reason, timestamp
      FROM warnings
      ORDER BY timestamp DESC
      LIMIT 50
    `).all();
    const total = (conn.prepare("SELECT COUNT(*) AS c FROM warnings").get() as {c:number}).c;
    conn.close();
    return { list, total };
  }, { list: [], total: 0 });
  res.json(result);
});

// GET /api/suggestions - suggestions by status
router.get("/suggestions", (_req, res) => {
  const result = safeQuery(() => {
    const conn = db();
    const list = conn.prepare(`
      SELECT id, guild_id, user_id, suggestion, status, created_at
      FROM suggestions
      ORDER BY created_at DESC
      LIMIT 30
    `).all();
    const pending = (conn.prepare("SELECT COUNT(*) AS c FROM suggestions WHERE status='pending'").get() as {c:number}).c;
    const approved = (conn.prepare("SELECT COUNT(*) AS c FROM suggestions WHERE status='approved'").get() as {c:number}).c;
    const denied = (conn.prepare("SELECT COUNT(*) AS c FROM suggestions WHERE status='denied'").get() as {c:number}).c;
    conn.close();
    return { list, pending, approved, denied };
  }, { list: [], pending: 0, approved: 0, denied: 0 });
  res.json(result);
});

// GET /api/members - overall member stats
router.get("/members", (_req, res) => {
  const result = safeQuery(() => {
    const conn = db();
    const total = (conn.prepare("SELECT COUNT(*) AS c FROM users").get() as {c:number}).c;
    const leveled = (conn.prepare("SELECT COUNT(*) AS c FROM users WHERE level > 0").get() as {c:number}).c;
    const wealthy = (conn.prepare("SELECT COUNT(*) AS c FROM users WHERE (balance + bank) > 1000").get() as {c:number}).c;
    const avgLevel = (conn.prepare("SELECT AVG(level) AS a FROM users").get() as {a:number|null}).a ?? 0;
    const avgBalance = (conn.prepare("SELECT AVG(balance + bank) AS a FROM users").get() as {a:number|null}).a ?? 0;
    conn.close();
    return { total, leveled, wealthy, avgLevel: Math.round(avgLevel * 10) / 10, avgBalance: Math.round(avgBalance) };
  }, { total: 0, leveled: 0, wealthy: 0, avgLevel: 0, avgBalance: 0 });
  res.json(result);
});

export default router;
