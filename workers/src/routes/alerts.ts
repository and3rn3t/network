/**
 * Alert endpoints
 */

import { zValidator } from "@hono/zod-validator";
import { Hono } from "hono";
import { z } from "zod";
import type { Env } from "../index";
import { verifyToken } from "./auth";

const alerts = new Hono<{ Bindings: Env }>();

// Middleware to verify auth
const authMiddleware = async (c: any, next: any) => {
  const authHeader = c.req.header("Authorization");
  if (!authHeader?.startsWith("Bearer ")) {
    return c.json({ error: "Unauthorized" }, 401);
  }

  const token = authHeader.substring(7);
  const payload = await verifyToken(token, c.env.JWT_SECRET);

  if (!payload) {
    return c.json({ error: "Invalid token" }, 401);
  }

  c.set("user", payload);
  await next();
};

// Apply auth middleware to all routes
alerts.use("*", authMiddleware);

// List alerts
alerts.get("/", async (c) => {
  const status = c.req.query("status");
  const severity = c.req.query("severity");
  const limit = parseInt(c.req.query("limit") || "100");
  const offset = parseInt(c.req.query("offset") || "0");

  let query = "SELECT * FROM alerts WHERE 1=1";
  const bindings: any[] = [];

  if (status) {
    query += " AND status = ?";
    bindings.push(status);
  }

  if (severity) {
    query += " AND severity = ?";
    bindings.push(severity);
  }

  query += " ORDER BY triggered_at DESC LIMIT ? OFFSET ?";
  bindings.push(limit, offset);

  try {
    const result = await c.env.DB.prepare(query)
      .bind(...bindings)
      .all();

    return c.json({
      alerts: result.results || [],
      total: result.results?.length || 0,
      limit,
      offset,
    });
  } catch (error) {
    return c.json({ error: "Failed to fetch alerts" }, 500);
  }
});

// Get alert by ID
alerts.get("/:id", async (c) => {
  const id = c.req.param("id");

  try {
    const alert = await c.env.DB.prepare("SELECT * FROM alerts WHERE id = ?")
      .bind(id)
      .first();

    if (!alert) {
      return c.json({ error: "Alert not found" }, 404);
    }

    return c.json(alert);
  } catch (error) {
    return c.json({ error: "Failed to fetch alert" }, 500);
  }
});

// Acknowledge alert
const acknowledgeSchema = z.object({
  notes: z.string().optional(),
});

alerts.post(
  "/:id/acknowledge",
  zValidator("json", acknowledgeSchema),
  async (c) => {
    const id = c.req.param("id");
    const { notes } = c.req.valid("json");
    const user = c.get("user");

    try {
      await c.env.DB.prepare(
        `UPDATE alerts
       SET status = 'acknowledged',
           acknowledged_at = CURRENT_TIMESTAMP,
           acknowledged_by = ?,
           notes = ?
       WHERE id = ?`
      )
        .bind(user.username, notes || null, id)
        .run();

      const alert = await c.env.DB.prepare("SELECT * FROM alerts WHERE id = ?")
        .bind(id)
        .first();

      return c.json(alert);
    } catch (error) {
      return c.json({ error: "Failed to acknowledge alert" }, 500);
    }
  }
);

// Resolve alert
alerts.post(
  "/:id/resolve",
  zValidator("json", acknowledgeSchema),
  async (c) => {
    const id = c.req.param("id");
    const { notes } = c.req.valid("json");
    const user = c.get("user");

    try {
      await c.env.DB.prepare(
        `UPDATE alerts
       SET status = 'resolved',
           resolved_at = CURRENT_TIMESTAMP,
           resolved_by = ?,
           notes = COALESCE(notes || ' | ', '') || ?
       WHERE id = ?`
      )
        .bind(user.username, notes || "", id)
        .run();

      const alert = await c.env.DB.prepare("SELECT * FROM alerts WHERE id = ?")
        .bind(id)
        .first();

      return c.json(alert);
    } catch (error) {
      return c.json({ error: "Failed to resolve alert" }, 500);
    }
  }
);

// Get alert statistics
alerts.get("/stats/summary", async (c) => {
  try {
    const stats = await c.env.DB.prepare(
      `
      SELECT
        COUNT(*) as total,
        SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active,
        SUM(CASE WHEN status = 'acknowledged' THEN 1 ELSE 0 END) as acknowledged,
        SUM(CASE WHEN severity = 'critical' AND status = 'active' THEN 1 ELSE 0 END) as critical
      FROM alerts
    `
    ).first();

    return c.json(stats);
  } catch (error) {
    return c.json({ error: "Failed to fetch stats" }, 500);
  }
});

export default alerts;
