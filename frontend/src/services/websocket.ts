import { io, Socket } from 'socket.io-client';
import type { AgentUpdate } from '../types/task';

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';

class WebSocketService {
  private socket: Socket | null = null;
  private listeners: Map<string, Set<(data: AgentUpdate) => void>> = new Map();

  connect(taskId: string): void {
    if (this.socket?.connected) {
      this.disconnect();
    }

    this.socket = io(WS_URL, {
      path: `/ws/tasks/${taskId}`,
      transports: ['websocket'],
    });

    this.socket.on('connect', () => {
      console.log('WebSocket connected for task:', taskId);
    });

    this.socket.on('message', (data: AgentUpdate) => {
      this.notifyListeners(taskId, data);
    });

    this.socket.on('disconnect', () => {
      console.log('WebSocket disconnected');
    });

    this.socket.on('error', (error) => {
      console.error('WebSocket error:', error);
    });
  }

  disconnect(): void {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
  }

  send(message: any): void {
    if (this.socket?.connected) {
      this.socket.emit('message', message);
    }
  }

  subscribe(taskId: string, callback: (data: AgentUpdate) => void): () => void {
    if (!this.listeners.has(taskId)) {
      this.listeners.set(taskId, new Set());
    }
    this.listeners.get(taskId)!.add(callback);

    // Return unsubscribe function
    return () => {
      const listeners = this.listeners.get(taskId);
      if (listeners) {
        listeners.delete(callback);
        if (listeners.size === 0) {
          this.listeners.delete(taskId);
        }
      }
    };
  }

  private notifyListeners(taskId: string, data: AgentUpdate): void {
    const listeners = this.listeners.get(taskId);
    if (listeners) {
      listeners.forEach((callback) => callback(data));
    }
  }

  isConnected(): boolean {
    return this.socket?.connected || false;
  }
}

export const wsService = new WebSocketService();
export default wsService;

// Made with Bob
