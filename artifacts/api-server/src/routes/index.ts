import { Router, type IRouter } from "express";
import healthRouter from "./health";
import botStatsRouter from "./bot-stats";
import dataRouter from "./data";

const router: IRouter = Router();

router.use(healthRouter);
router.use(botStatsRouter);
router.use(dataRouter);

export default router;
