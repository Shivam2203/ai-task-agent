import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { taskApi } from '../services/api';
import type { Task, TaskCreate } from '../types/task';

interface TaskInputProps {
  onTaskCreated: (task: Task) => void;
}

export default function TaskInput({ onTaskCreated }: TaskInputProps) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');

  const createTaskMutation = useMutation({
    mutationFn: (task: TaskCreate) => taskApi.createTask(task),
    onSuccess: (data) => {
      onTaskCreated(data);
      setTitle('');
      setDescription('');
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (title && description) {
      createTaskMutation.mutate({ title, description, priority: 0 });
    }
  };

  return (
    <div className="card">
      <h2 className="text-2xl font-bold mb-4 text-gray-800">Create New Task</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Task Title
          </label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="input"
            placeholder="Enter task title..."
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Task Description
          </label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="textarea"
            rows={6}
            placeholder="Describe the task in detail..."
            required
          />
        </div>

        <button
          type="submit"
          disabled={createTaskMutation.isPending}
          className="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {createTaskMutation.isPending ? 'Creating Task...' : 'Start Task'}
        </button>

        {createTaskMutation.isError && (
          <div className="text-red-600 text-sm">
            Error creating task. Please try again.
          </div>
        )}
      </form>
    </div>
  );
}

// Made with Bob
