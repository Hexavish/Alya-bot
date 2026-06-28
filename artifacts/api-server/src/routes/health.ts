import { Router, type IRouter } from "express";
import { HealthCheckResponse } from "@workspace/api-zod";
import { getBotStatus } from "../lib/bot-manager";

const router: IRouter = Router();

router.get("/healthz", (_req, res) => {
  const data = HealthCheckResponse.parse({ status: "ok" });
  res.json(data);
});

router.get("/ping", (_req, res) => {
  const bot = getBotStatus();
  res.json({
    status: "ok",
    bot,
    timestamp: new Date().toISOString(),
  });
});

export default router;
