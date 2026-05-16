export interface Task {
  id: string;
  title: string;
  description: string;
  status: 'pending' | 'planning' | 'executing' | 'verifying' | 'completed' | 'failed';
  priority: number;
  created_at: string;
  updated_at: string;
  completed_at?: string;
  result?: string;
  error?: string;
  metadata?: Record<string, any>;
}

export interface TaskCreate {
  title: string;
  description: string;
  priority?: number;
  metadata?: Record<string, any>;
}

export interface AgentUpdate {
  type: 'connected' | 'status' | 'update' | 'complete' | 'error' | 'pong';
  task_id: string;
  status?: string;
  message?: string;
  data?: any;
  error?: string;
}

export interface AgentState {
  id: string;
  state_type: 'planning' | 'executing' | 'verifying';
  iteration: number;
  created_at: string;
  state_data: Record<string, any>;
}

export interface AgentStep {
  id: string;
  step_type: string;
  step_number: number;
  status: 'pending' | 'running' | 'completed' | 'failed';
  started_at: string;
  completed_at?: string;
  input_data?: Record<string, any>;
  output_data?: Record<string, any>;
  error?: string;
}

// Made with Bob
