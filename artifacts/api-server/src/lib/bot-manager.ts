import { spawn, type ChildProcess } from "child_process";
import path from "path";
import { fileURLToPath } from "url";
import { logger } from "./logger";

const WORKSPACE_ROOT = path.resolve(
  fileURLToPath(import.meta.url),
  "../../../../../../"
);

let botProcess: ChildProcess | null = null;
let botStatus: "starting" | "running" | "restarting" | "stopped" = "stopped";
let restartCount = 0;
let lastStarted: Date | null = null;

export function getBotStatus() {
  return {
    status: botStatus,
    restartCount,
    lastStarted: lastStarted?.toISOString() ?? null,
    pid: botProcess?.pid ?? null,
  };
}

function scheduleRestart(delayMs: number) {
  botStatus = "restarting";
  logger.info({ delayMs }, "Scheduling bot restart");
  setTimeout(startBot, delayMs);
}

export function startBot() {
  if (botProcess && !botProcess.killed) {
    logger.warn("Bot already running, skipping start");
    return;
  }

  const token = process.env["DISCORD_TOKEN"];
  if (!token) {
    logger.error("DISCORD_TOKEN not set — bot will not start");
    botStatus = "stopped";
    return;
  }

  logger.info({ cwd: WORKSPACE_ROOT }, "Starting Discord bot");
  botStatus = "starting";
  lastStarted = new Date();

  botProcess = spawn("python", ["main.py"], {
    cwd: WORKSPACE_ROOT,
    env: { ...process.env },
    stdio: ["ignore", "pipe", "pipe"],
  });

  botProcess.stdout?.on("data", (data: Buffer) => {
    const lines = data.toString().trim().split("\n");
    for (const line of lines) {
      if (line.trim()) logger.info({ src: "bot" }, line.trim());
    }
    if (botStatus === "starting") botStatus = "running";
  });

  botProcess.stderr?.on("data", (data: Buffer) => {
    const lines = data.toString().trim().split("\n");
    for (const line of lines) {
      if (line.trim()) logger.warn({ src: "bot" }, line.trim());
    }
  });

  botProcess.on("spawn", () => {
    restartCount++;
    botStatus = "running";
    logger.info({ pid: botProcess?.pid, restartCount }, "Bot process started");
  });

  botProcess.on("exit", (code, signal) => {
    botProcess = null;
    const delay = Math.min(5000 * Math.ceil(restartCount / 3), 30000);
    logger.warn({ code, signal, nextRetryMs: delay }, "Bot exited, will restart");
    scheduleRestart(delay);
  });

  botProcess.on("error", (err) => {
    logger.error({ err }, "Failed to spawn bot process");
    botProcess = null;
    scheduleRestart(10000);
  });
}

export function stopBot() {
  if (botProcess) {
    botStatus = "stopped";
    botProcess.kill("SIGTERM");
    botProcess = null;
    logger.info("Bot process stopped");
  }
}
