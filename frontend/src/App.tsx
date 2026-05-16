import { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import TaskInput from './components/TaskInput';
import TaskMonitor from './components/TaskMonitor';
import TaskHistory from './components/TaskHistory';
import type { Task } from './types/task';

const queryClient = new QueryClient();

function App() {
  const [currentTask, setCurrentTask] = useState<Task | null>(null);

  return (
    <QueryClientProvider client={queryClient}>
      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <header className="bg-gradient-to-r from-blue-600 to-blue-800 text-white shadow-lg">
          <div className="container mx-auto px-6 py-8">
            <h1 className="text-4xl font-bold mb-2">🤖 AI Task Completion Agent</h1>
            <p className="text-blue-100 text-lg">
              Autonomous Planning, Execution & Verification powered by IBM watsonx.ai Granite
            </p>
          </div>
        </header>

        {/* Main Content */}
        <main className="container mx-auto px-6 py-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Left Column - Task Input and Monitor */}
            <div className="space-y-6">
              <TaskInput onTaskCreated={setCurrentTask} />
              {currentTask && <TaskMonitor task={currentTask} />}
            </div>

            {/* Right Column - Task History */}
            <div>
              <TaskHistory onTaskSelect={setCurrentTask} selectedTaskId={currentTask?.id} />
            </div>
          </div>
        </main>

        {/* Footer */}
        <footer className="bg-gray-800 text-gray-300 mt-16">
          <div className="container mx-auto px-6 py-6 text-center">
            <p>Built with FastAPI, React, LangGraph & IBM watsonx.ai</p>
          </div>
        </footer>
      </div>
    </QueryClientProvider>
  );
}

export default App;

// Made with Bob
