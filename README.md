# AI Task Completion Agent

An autonomous AI agent that can plan, execute, and verify tasks using IBM watsonx.ai Granite LLM, LangGraph workflow orchestration, and RAG-enhanced context retrieval.

## 🌟 Features

- **🤖 Autonomous Task Execution**: Agent independently plans, executes, and verifies tasks
- **🧠 Intelligent Planning**: Uses Granite LLM to break down complex tasks into actionable steps
- **🔄 Iterative Refinement**: Self-verifies results and re-plans if needed
- **📚 RAG-Enhanced Context**: Retrieves relevant information using pgvector and ChromaDB
- **⚡ Real-time Updates**: WebSocket-based live progress monitoring
- **🎯 Multi-domain Support**: Handles code generation, data analysis, research, and more
- **💾 Persistent State**: Tracks task history and agent states in PostgreSQL
- **🔍 Semantic Search**: Vector similarity search across task history
- **📊 Interactive UI**: Modern React frontend with real-time feedback

## 🏗️ Architecture

```
┌─────────────────┐
│  React Frontend │
│   (TypeScript)  │
└────────┬────────┘
         │ HTTP/WebSocket
┌────────▼────────┐
│  FastAPI Server │
│    (Python)     │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼──┐  ┌──▼────┐
│ Agent│  │  RAG  │
│Graph │  │System │
└───┬──┘  └──┬────┘
    │        │
┌───▼────────▼───┐
│  watsonx.ai    │
│  Granite LLM   │
└────────────────┘
         │
    ┌────┴────┐
    │         │
┌───▼──┐  ┌──▼─────┐
│ PG + │  │ChromaDB│
│vector│  │        │
└──────┘  └────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- PostgreSQL 16+ with pgvector
- Docker & Docker Compose (recommended)
- IBM watsonx.ai account

### Docker Setup (Recommended)

```bash
# Clone repository
git clone <your-repo-url>
cd ai-task-agent

# Configure environment
cp backend/.env.example backend/.env
# Edit backend/.env with your watsonx.ai credentials

# Start all services
docker-compose -f docker/docker-compose.yml up -d

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

For detailed setup instructions, see [QUICK_START.md](QUICK_START.md).

## 📖 Documentation

- **[Implementation Plan](IMPLEMENTATION_PLAN.md)** - Detailed step-by-step implementation guide
- **[Architecture](ARCHITECTURE.md)** - System architecture and design decisions
- **[Quick Start](QUICK_START.md)** - Get up and running in 30 minutes
- **[API Documentation](http://localhost:8000/docs)** - Interactive API documentation (when running)

## 🛠️ Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **LangGraph** - Agent workflow orchestration
- **watsonx.ai** - IBM Granite LLM integration
- **PostgreSQL + pgvector** - Database with vector similarity search
- **ChromaDB** - Vector store for document retrieval
- **SQLAlchemy** - ORM and database migrations
- **Redis** - Caching and session management

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type-safe JavaScript
- **Vite** - Fast build tool
- **TanStack Query** - Data fetching and caching
- **Tailwind CSS** - Utility-first styling
- **Socket.io** - Real-time WebSocket communication

## 🎯 Use Cases

### Code Generation
```
Task: "Create a REST API for user management with CRUD operations"
→ Agent plans the structure
→ Generates code for models, routes, and tests
→ Verifies code quality and completeness
```

### Data Analysis
```
Task: "Analyze sales data and identify trends"
→ Agent retrieves relevant context
→ Performs analysis step-by-step
→ Generates insights and visualizations
```

### Research & Documentation
```
Task: "Research best practices for microservices architecture"
→ Agent searches knowledge base
→ Synthesizes information
→ Creates comprehensive documentation
```

## 🔧 Configuration

### Environment Variables

```env
# watsonx.ai Configuration
WATSONX_API_KEY=your_api_key
WATSONX_PROJECT_ID=your_project_id
WATSONX_URL=https://us-south.ml.cloud.ibm.com

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/taskagent_db

# Redis
REDIS_URL=redis://localhost:6379

# Application
SECRET_KEY=your-secret-key
ALLOWED_ORIGINS=http://localhost:3000
MAX_AGENT_ITERATIONS=5
AGENT_TIMEOUT_SECONDS=300
```

## 📊 Agent Workflow

The agent follows a three-phase iterative workflow:

### 1. Planning Phase
- Analyzes the task description
- Retrieves relevant context using RAG
- Generates a detailed execution plan
- Identifies dependencies and expected outcomes

### 2. Execution Phase
- Executes each step in the plan
- Tracks progress and intermediate results
- Handles errors and edge cases
- Maintains state throughout execution

### 3. Verification Phase
- Verifies task completion
- Assesses result quality
- Determines if re-planning is needed
- Provides final results or feedback

```mermaid
graph LR
    A[Task Input] --> B[Planning]
    B --> C[Execution]
    C --> D[Verification]
    D --> E{Complete?}
    E -->|Yes| F[Return Results]
    E -->|No| B
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest                          # Run all tests
pytest --cov=app tests/        # With coverage
pytest -v tests/test_agent.py  # Specific test file
```

### Frontend Tests
```bash
cd frontend
npm test              # Run tests
npm run test:coverage # With coverage
```

### Integration Tests
```bash
# Start services
docker-compose up -d

# Run integration tests
cd backend
pytest tests/integration/
```

## 📈 Performance

- **Average Task Completion**: 30-120 seconds (depending on complexity)
- **Concurrent Tasks**: Supports multiple simultaneous tasks
- **Vector Search**: Sub-second similarity search with pgvector
- **Real-time Updates**: <100ms WebSocket latency
- **Database Queries**: Optimized with indexes and connection pooling

## 🔒 Security

- API key authentication for watsonx.ai
- Environment-based configuration
- Input validation and sanitization
- Rate limiting on API endpoints
- Secure WebSocket connections
- SQL injection prevention via ORM

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 for Python code
- Use ESLint + Prettier for TypeScript
- Write tests for new features
- Update documentation
- Use semantic commit messages

## 📝 Example Usage

### Web Interface

1. Navigate to http://localhost:3000
2. Enter your task in the input form
3. Click "Start Task"
4. Monitor real-time progress
5. View results when complete

### API

```python
import requests

# Create a task
response = requests.post(
    "http://localhost:8000/api/v1/tasks",
    json={
        "title": "Generate Python function",
        "description": "Create a function to calculate prime numbers up to n"
    }
)

task_id = response.json()["id"]

# Get task status
status = requests.get(f"http://localhost:8000/api/v1/tasks/{task_id}")
print(status.json())
```

### WebSocket

```javascript
const socket = new WebSocket(`ws://localhost:8000/ws/tasks/${taskId}`);

socket.onmessage = (event) => {
  const update = JSON.parse(event.data);
  console.log('Task update:', update);
};
```

## 🐛 Troubleshooting

### Common Issues

**Backend won't start**
- Check Python version (3.11+)
- Verify virtual environment is activated
- Ensure PostgreSQL is running
- Check environment variables

**Frontend won't connect**
- Verify backend is running on port 8000
- Check CORS configuration
- Ensure WebSocket port is accessible

**Agent not responding**
- Verify watsonx.ai credentials
- Check API rate limits
- Review backend logs
- Ensure database connection

For more troubleshooting tips, see [QUICK_START.md](QUICK_START.md#troubleshooting).

## 📚 Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [LangGraph Guide](https://langchain-ai.github.io/langgraph/)
- [watsonx.ai Documentation](https://www.ibm.com/docs/en/watsonx-as-a-service)
- [pgvector GitHub](https://github.com/pgvector/pgvector)
- [ChromaDB Documentation](https://docs.trychroma.com)

## 🗺️ Roadmap

### Phase 1 (Current)
- [x] Core agent workflow
- [x] Basic RAG implementation
- [x] Task management API
- [x] Real-time monitoring

### Phase 2 (Planned)
- [ ] Multi-model LLM support
- [ ] Advanced tool integration
- [ ] Human-in-the-loop approval
- [ ] Enhanced error recovery

### Phase 3 (Future)
- [ ] Multi-agent collaboration
- [ ] Workflow templates
- [ ] Analytics dashboard
- [ ] Mobile application

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- IBM watsonx.ai team for Granite LLM
- LangChain team for LangGraph framework
- FastAPI community
- React and TypeScript communities
- Open source contributors

## 📞 Support

- **Documentation**: Check the `docs/` directory
- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/discussions)
- **Email**: support@example.com

---

**Built with ❤️ using IBM watsonx.ai Granite LLM**

*For detailed implementation guidance, see [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md)*