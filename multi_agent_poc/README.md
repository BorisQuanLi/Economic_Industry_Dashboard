# Multi-Agent POC System

A proof-of-concept implementation of a multi-agent AI system for software development productivity.

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Google Cloud SDK (for Gemini Agent)
- Mistral AI API key (optional, for Mistral Vibe Agent)

### Setup

```bash
# From project root
cd Economic_Industry_Dashboard/multi_agent_poc/

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### Configuration

#### Gemini Agent (Google Vertex AI)

```bash
# Authenticate with Google Cloud
gcloud auth application-default login

# Ensure Vertex AI API is enabled
gcloud services enable aiplatform.googleapis.com
```

#### Mistral Vibe Agent (Optional)

```bash
# Create .env file with your Mistral API key
cp .env.example .env
echo "MISTRAL_API_KEY=your_api_key_here" >> .env
```

## 🤖 AI Agents Overview

The system consists of three specialized AI agents working in parallel:

### 1. Gemini Agent - Code Generation Specialist

**Role**: Code generation, refactoring, and Docker compatibility

**Usage**:
```bash
python3 gemini_agent.py "<your_prompt>"
```

**Example**:
```bash
python3 gemini_agent.py "Create a Python function that returns 'hello world'"
```

**Features**:
- Google Vertex AI integration (gemini-2.0-flash-001)
- System instruction for Python refactoring
- Docker compatibility focus
- Comprehensive error handling

### 2. Mistral Vibe Agent - Testing & Validation Specialist

**Role**: Code quality validation, test generation, and performance analysis

**Usage**:
```bash
python3 mistral_vibe_agent.py <task_type> "<code_or_file>"
```

**Task Types**:
- `test-suite`: Generate comprehensive test suites
- `validate`: Validate code quality and best practices
- `performance`: Analyze performance characteristics

**Examples**:
```bash
# Generate test suite
python3 mistral_vibe_agent.py test-suite "def add(a, b): return a + b"

# Validate code quality
python3 mistral_vibe_agent.py validate my_module.py

# Analyze performance
python3 mistral_vibe_agent.py performance "def factorial(n): return 1 if n == 0 else n * factorial(n-1)"
```

**Features**:
- Mistral AI API integration (with placeholder fallback)
- Comprehensive testing capabilities
- Code quality validation
- Performance analysis and optimization suggestions
- File and direct code input support

### 3. Amazon Q Agent - Documentation Specialist

**Role**: Architecture documentation and system design

**Usage**:
```bash
python3 amazon_q_agent.py "<documentation_request>"
```

**Example**:
```bash
python3 amazon_q_agent.py "Generate architecture diagram for multi-agent system"
```

**Status**: Placeholder implementation (AWS integration planned)

## 🎯 Division of Labor

The three agents work together to provide comprehensive AI-powered development:

```
Code Generation → Testing & Validation → Documentation
    (Gemini)          (Mistral Vibe)      (Amazon Q)
```

**Workflow Example**:
```bash
# 1. Generate code with Gemini
python3 gemini_agent.py "Create a data processing function"

# 2. Validate and test with Mistral Vibe
python3 mistral_vibe_agent.py validate "generated_code.py"
python3 mistral_vibe_agent.py test-suite "generated_code.py"

# 3. Document with Amazon Q
python3 amazon_q_agent.py "Document the data processing module"
```

## 📁 Project Structure

```
multi_agent_poc/
├── .env                    # Environment configuration
├── .venv/                  # Virtual environment
├── README.md               # This file
├── requirements.txt        # Dependencies
├── gemini_agent.py         # Gemini Agent implementation
├── mistral_vibe_agent.py   # Mistral Vibe Agent implementation
├── amazon_q_agent.py       # Amazon Q Agent implementation
├── models.py               # Data models (Pydantic)
└── orchestrator.py         # Multi-agent orchestrator (placeholder)
```

## 🔧 Development

### Running Tests

```bash
# Test Gemini Agent
python3 gemini_agent.py "Create a Python function that returns 'hello world'"

# Test Mistral Vibe Agent
python3 mistral_vibe_agent.py validate "def test(): pass"
python3 mistral_vibe_agent.py test-suite "def add(a, b): return a + b"
python3 mistral_vibe_agent.py performance "def factorial(n): return 1 if n == 0 else n * factorial(n-1)"

# Test Amazon Q Agent
python3 amazon_q_agent.py "Generate documentation for test module"
```

### Environment Variables

```
# .env file
MISTRAL_API_KEY="your_mistral_api_key_here"
DEBUG_MODE=true
```

### Dependencies

```
# Google Cloud Vertex AI SDK
google-cloud-aiplatform

# Mistral Vibe Agent dependencies
requests>=2.31.0
python-dotenv>=1.0.0
```

## 🚀 Future Development

### Planned Enhancements

1. **Amazon Q Agent**: Complete AWS SDK integration
2. **Orchestrator**: Implement multi-agent coordination
3. **Security**: Add vulnerability scanning to Mistral Vibe
4. **Performance**: Implement benchmarking tools
5. **Integration**: Add CI/CD pipeline support

### Production Readiness

- Configure actual API keys
- Add rate limiting and error recovery
- Implement logging and monitoring
- Add comprehensive test suite

## 📚 Documentation

Detailed development notes and testing methodologies are available in:
```
refactoring_notes_Economic_Industry_Dashboard/00-backend-refactoring/02-AI-Engineering-since-01-2026/01_intuit_ai_native_se/
```

## 🤝 Contributing

This is a proof-of-concept system. Contributions are welcome for:
- Agent enhancements
- Orchestrator development
- Testing improvements
- Documentation expansion
- Performance optimization

## 📈 Impact

This multi-agent system demonstrates the transformative potential of AI in software development:
- **Exponential Productivity**: Parallel specialized agents
- **Comprehensive Coverage**: Code generation to documentation
- **Quality Assurance**: Built-in validation and testing
- **Scalability**: Enterprise-grade architecture
