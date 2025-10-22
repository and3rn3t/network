/**
 * WebSocket Durable Object for real-time updates
 */

export class WebSocketDurableObject {
  private state: DurableObjectState;
  private sessions: Set<WebSocket>;

  constructor(state: DurableObjectState) {
    this.state = state;
    this.sessions = new Set();
  }

  async fetch(request: Request): Promise<Response> {
    const upgradeHeader = request.headers.get('Upgrade');
    
    if (upgradeHeader !== 'websocket') {
      return new Response('Expected websocket', { status: 400 });
    }

    const pair = new WebSocketPair();
    const [client, server] = Object.values(pair);

    // Accept the WebSocket connection
    this.handleSession(server);

    return new Response(null, {
      status: 101,
      webSocket: client,
    });
  }

  handleSession(webSocket: WebSocket) {
    webSocket.accept();
    this.sessions.add(webSocket);

    webSocket.addEventListener('message', (event: MessageEvent) => {
      // Echo messages back for now
      // In production, handle different message types
      webSocket.send(JSON.stringify({
        type: 'echo',
        data: event.data,
        timestamp: new Date().toISOString(),
      }));
    });

    webSocket.addEventListener('close', () => {
      this.sessions.delete(webSocket);
    });

    webSocket.addEventListener('error', () => {
      this.sessions.delete(webSocket);
    });

    // Send welcome message
    webSocket.send(JSON.stringify({
      type: 'connected',
      message: 'Connected to UniFi Network API WebSocket',
      timestamp: new Date().toISOString(),
    }));
  }

  // Broadcast message to all connected clients
  broadcast(message: any) {
    const messageStr = JSON.stringify(message);
    this.sessions.forEach((session) => {
      try {
        session.send(messageStr);
      } catch (err) {
        // Remove failed sessions
        this.sessions.delete(session);
      }
    });
  }
}
