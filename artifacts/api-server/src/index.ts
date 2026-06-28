import app from "./app";
import { logger } from "./lib/logger";
import { startBot, stopBot } from "./lib/bot-manager";

const rawPort = process.env["PORT"];

if (!rawPort) {
  throw new Error(
    "PORT environment variable is required but was not provided.",
  );
}

const port = Number(rawPort);

if (Number.isNaN(port) || port <= 0) {
  throw new Error(`Invalid PORT value: "${rawPort}"`);
}

app.listen(port, (err) => {
  if (err) {
    logger.error({ err }, "Error listening on port");
    process.exit(1);
  }

  logger.info({ port }, "Server listening");

  // Only manage the bot process when MANAGE_BOT=true (set in production).
  // In development the "Alya Bot" workflow runs the bot separately.
  if (process.env["MANAGE_BOT"] === "true") {
    startBot();
  } else {
    logger.info("MANAGE_BOT not set — bot managed externally (dev mode)");
  }
});

process.on("SIGTERM", () => {
  logger.info("SIGTERM received, stopping bot");
  stopBot();
  process.exit(0);
});

process.on("SIGINT", () => {
  logger.info("SIGINT received, stopping bot");
  stopBot();
  process.exit(0);
});
