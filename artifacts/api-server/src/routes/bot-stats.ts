import { Router } from "express";
import Database from "better-sqlite3";
import path from "path";
import { fileURLToPath } from "url";
import { getBotStatus } from "../lib/bot-manager";

const router = Router();

const dbPath = path.resolve(
  fileURLToPath(import.meta.url),
  "../../../../../alya.db"
);

function readDb() {
  try {
    const db = new Database(dbPath, { readonly: true, fileMustExist: true });
    const guilds = (db.prepare("SELECT COUNT(DISTINCT guild_id) as c FROM guilds").get() as { c: number }).c;
    const users = (db.prepare("SELECT COUNT(*) as c FROM users").get() as { c: number }).c;
    const tickets = (db.prepare("SELECT COUNT(*) as c FROM tickets").get() as { c: number }).c;
    const giveaways = (db.prepare("SELECT COUNT(*) as c FROM giveaways").get() as { c: number }).c;
    const warnings = (db.prepare("SELECT COUNT(*) as c FROM warnings").get() as { c: number }).c;
    const levels = (db.prepare("SELECT COUNT(*) as c FROM levels").get() as { c: number }).c;
    db.close();
    return { guilds, users, tickets, giveaways, warnings, levels };
  } catch {
    return { guilds: 0, users: 0, tickets: 0, giveaways: 0, warnings: 0, levels: 0 };
  }
}

router.get("/bot-stats", (_req, res) => {
  const db = readDb();
  const bot = getBotStatus();
  res.json({
    ...db,
    commands: 68,
    systems: 11,
    serverUptime: process.uptime(),
    botProcess: bot,
  });
});

export default router;
