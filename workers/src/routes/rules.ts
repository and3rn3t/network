/**
 * Alert rules endpoints
 */

import { Hono } from 'hono';
import { zValidator } from '@hono/zod-validator';
import { z } from 'zod';
import type { Env } from '../index';
import { verifyToken } from './auth';

const rules = new Hono<{ Bindings: Env }>();

// Auth middleware
const authMiddleware = async (c: any, next: any) => {
  const authHeader = c.req.header('Authorization');
  if (!authHeader?.startsWith('Bearer ')) {
    return c.json({ error: 'Unauthorized' }, 401);
  }
  
  const token = authHeader.substring(7);
  const payload = await verifyToken(token, c.env.JWT_SECRET);
  
  if (!payload) {
    return c.json({ error: 'Invalid token' }, 401);
  }
  
  c.set('user', payload);
  await next();
};

rules.use('*', authMiddleware);

// Validation schema
const ruleSchema = z.object({
  name: z.string().min(1),
  rule_type: z.enum(['threshold', 'status_change', 'anomaly']),
  condition: z.string(),
  threshold: z.number().optional(),
  severity: z.enum(['info', 'warning', 'critical']),
  enabled: z.boolean().default(true),
  cooldown_minutes: z.number().default(15),
});

// List rules
rules.get('/', async (c) => {
  const enabled = c.req.query('enabled');
  
  let query = 'SELECT * FROM alert_rules WHERE 1=1';
  const bindings: any[] = [];
  
  if (enabled !== undefined) {
    query += ' AND enabled = ?';
    bindings.push(enabled === 'true' ? 1 : 0);
  }
  
  query += ' ORDER BY created_at DESC';
  
  try {
    const result = await c.env.DB.prepare(query).bind(...bindings).all();
    return c.json(result.results || []);
  } catch (error) {
    return c.json({ error: 'Failed to fetch rules' }, 500);
  }
});

// Get rule by ID
rules.get('/:id', async (c) => {
  const id = c.req.param('id');
  
  try {
    const rule = await c.env.DB.prepare(
      'SELECT * FROM alert_rules WHERE id = ?'
    ).bind(id).first();
    
    if (!rule) {
      return c.json({ error: 'Rule not found' }, 404);
    }
    
    return c.json(rule);
  } catch (error) {
    return c.json({ error: 'Failed to fetch rule' }, 500);
  }
});

// Create rule
rules.post('/', zValidator('json', ruleSchema), async (c) => {
  const data = c.req.valid('json');
  
  try {
    const result = await c.env.DB.prepare(
      `INSERT INTO alert_rules (name, rule_type, condition, threshold, severity, enabled, cooldown_minutes)
       VALUES (?, ?, ?, ?, ?, ?, ?)`
    ).bind(
      data.name,
      data.rule_type,
      data.condition,
      data.threshold || null,
      data.severity,
      data.enabled ? 1 : 0,
      data.cooldown_minutes
    ).run();
    
    const rule = await c.env.DB.prepare(
      'SELECT * FROM alert_rules WHERE id = ?'
    ).bind(result.meta.last_row_id).first();
    
    return c.json(rule, 201);
  } catch (error) {
    return c.json({ error: 'Failed to create rule' }, 500);
  }
});

// Update rule
rules.put('/:id', zValidator('json', ruleSchema.partial()), async (c) => {
  const id = c.req.param('id');
  const data = c.req.valid('json');
  
  try {
    const updates: string[] = [];
    const bindings: any[] = [];
    
    if (data.name !== undefined) {
      updates.push('name = ?');
      bindings.push(data.name);
    }
    if (data.rule_type !== undefined) {
      updates.push('rule_type = ?');
      bindings.push(data.rule_type);
    }
    if (data.condition !== undefined) {
      updates.push('condition = ?');
      bindings.push(data.condition);
    }
    if (data.threshold !== undefined) {
      updates.push('threshold = ?');
      bindings.push(data.threshold);
    }
    if (data.severity !== undefined) {
      updates.push('severity = ?');
      bindings.push(data.severity);
    }
    if (data.enabled !== undefined) {
      updates.push('enabled = ?');
      bindings.push(data.enabled ? 1 : 0);
    }
    if (data.cooldown_minutes !== undefined) {
      updates.push('cooldown_minutes = ?');
      bindings.push(data.cooldown_minutes);
    }
    
    if (updates.length === 0) {
      return c.json({ error: 'No updates provided' }, 400);
    }
    
    bindings.push(id);
    
    await c.env.DB.prepare(
      `UPDATE alert_rules SET ${updates.join(', ')} WHERE id = ?`
    ).bind(...bindings).run();
    
    const rule = await c.env.DB.prepare(
      'SELECT * FROM alert_rules WHERE id = ?'
    ).bind(id).first();
    
    return c.json(rule);
  } catch (error) {
    return c.json({ error: 'Failed to update rule' }, 500);
  }
});

// Delete rule
rules.delete('/:id', async (c) => {
  const id = c.req.param('id');
  
  try {
    await c.env.DB.prepare('DELETE FROM alert_rules WHERE id = ?').bind(id).run();
    return c.json({ message: 'Rule deleted successfully' });
  } catch (error) {
    return c.json({ error: 'Failed to delete rule' }, 500);
  }
});

export default rules;
