/**
 * Notification channels endpoints
 */

import { Hono } from 'hono';
import { zValidator } from '@hono/zod-validator';
import { z } from 'zod';
import type { Env } from '../index';
import { verifyToken } from './auth';

const channels = new Hono<{ Bindings: Env }>();

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

channels.use('*', authMiddleware);

// Validation schema
const channelSchema = z.object({
  name: z.string().min(1),
  channel_type: z.enum(['email', 'slack', 'discord', 'webhook']),
  config: z.record(z.any()),
  enabled: z.boolean().default(true),
  min_severity: z.enum(['info', 'warning', 'critical']).default('info'),
});

// List channels
channels.get('/', async (c) => {
  try {
    const result = await c.env.DB.prepare(
      'SELECT * FROM notification_channels ORDER BY created_at DESC'
    ).all();
    
    return c.json(result.results || []);
  } catch (error) {
    return c.json({ error: 'Failed to fetch channels' }, 500);
  }
});

// Get channel by ID
channels.get('/:id', async (c) => {
  const id = c.req.param('id');
  
  try {
    const channel = await c.env.DB.prepare(
      'SELECT * FROM notification_channels WHERE id = ?'
    ).bind(id).first();
    
    if (!channel) {
      return c.json({ error: 'Channel not found' }, 404);
    }
    
    return c.json(channel);
  } catch (error) {
    return c.json({ error: 'Failed to fetch channel' }, 500);
  }
});

// Create channel
channels.post('/', zValidator('json', channelSchema), async (c) => {
  const data = c.req.valid('json');
  
  try {
    const result = await c.env.DB.prepare(
      `INSERT INTO notification_channels (name, channel_type, config, enabled, min_severity)
       VALUES (?, ?, ?, ?, ?)`
    ).bind(
      data.name,
      data.channel_type,
      JSON.stringify(data.config),
      data.enabled ? 1 : 0,
      data.min_severity
    ).run();
    
    const channel = await c.env.DB.prepare(
      'SELECT * FROM notification_channels WHERE id = ?'
    ).bind(result.meta.last_row_id).first();
    
    return c.json(channel, 201);
  } catch (error) {
    return c.json({ error: 'Failed to create channel' }, 500);
  }
});

// Update channel
channels.put('/:id', zValidator('json', channelSchema.partial()), async (c) => {
  const id = c.req.param('id');
  const data = c.req.valid('json');
  
  try {
    const updates: string[] = [];
    const bindings: any[] = [];
    
    if (data.name !== undefined) {
      updates.push('name = ?');
      bindings.push(data.name);
    }
    if (data.channel_type !== undefined) {
      updates.push('channel_type = ?');
      bindings.push(data.channel_type);
    }
    if (data.config !== undefined) {
      updates.push('config = ?');
      bindings.push(JSON.stringify(data.config));
    }
    if (data.enabled !== undefined) {
      updates.push('enabled = ?');
      bindings.push(data.enabled ? 1 : 0);
    }
    if (data.min_severity !== undefined) {
      updates.push('min_severity = ?');
      bindings.push(data.min_severity);
    }
    
    if (updates.length === 0) {
      return c.json({ error: 'No updates provided' }, 400);
    }
    
    bindings.push(id);
    
    await c.env.DB.prepare(
      `UPDATE notification_channels SET ${updates.join(', ')} WHERE id = ?`
    ).bind(...bindings).run();
    
    const channel = await c.env.DB.prepare(
      'SELECT * FROM notification_channels WHERE id = ?'
    ).bind(id).first();
    
    return c.json(channel);
  } catch (error) {
    return c.json({ error: 'Failed to update channel' }, 500);
  }
});

// Delete channel
channels.delete('/:id', async (c) => {
  const id = c.req.param('id');
  
  try {
    await c.env.DB.prepare('DELETE FROM notification_channels WHERE id = ?').bind(id).run();
    return c.json({ message: 'Channel deleted successfully' });
  } catch (error) {
    return c.json({ error: 'Failed to delete channel' }, 500);
  }
});

// Test channel
const testSchema = z.object({
  message: z.string().default('Test notification'),
});

channels.post('/:id/test', zValidator('json', testSchema), async (c) => {
  const id = c.req.param('id');
  const { message } = c.req.valid('json');
  
  try {
    const channel = await c.env.DB.prepare(
      'SELECT * FROM notification_channels WHERE id = ?'
    ).bind(id).first();
    
    if (!channel) {
      return c.json({ error: 'Channel not found' }, 404);
    }
    
    // TODO: Implement actual notification sending logic
    // For now, just simulate success
    
    return c.json({
      success: true,
      message: `Test notification sent to ${channel.name}`,
    });
  } catch (error) {
    return c.json({ error: 'Failed to test channel' }, 500);
  }
});

export default channels;
