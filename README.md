# CloudCart Prompt Management with LLM

## Project Overview

This enterprise-grade implementation demonstrates secure prompt management for a CloudCart e-commerce support system using LangChain, Groq API, and comprehensive validation layers. The system showcases prompt injection defense, YAML-based versioning, and production-ready architecture.


## Features

### Security Features
- **Prompt Injection Defense**: Multi-layer validation prevents injection attacks
- **Input Sanitization**: Detects emails, phone numbers, credit cards, oversized inputs
- **Output Validation**: Prevents prompt leakage and hallucinated responses
- **Role Separation**: Strict system/human message boundaries

### Prompt Management
- **YAML Versioning**: Structured prompt definitions with metadata
- **Few-Shot Examples**: Context-aware response patterns
- **Dynamic Compilation**: Runtime prompt building with safe variable substitution
- **Version Upgrades**: Seamless prompt evolution

### Enterprise Architecture
- **Modular Design**: Clean separation of concerns
- **Type Safety**: Full Pydantic validation and type hints
- **Rich Logging**: Structured logging with console formatting
- **Error Handling**: Comprehensive exception management
- **Test Coverage**: Unit tests for all critical components

## Quick Start

### 1. Setup Environment
```bash
# Clone the repository
git clone https://github.com/Akhil52153/Cloudcart.git
cd Cloudcart

# Create virtual environment
python -m venv venv

# Activate (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment
Create `.env` file in project root:
```env
GROQ_API_KEY=your_groq_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

### 3. Run Interactive Demo
```bash
streamlit run streamlit_app.py
```

Open http://localhost:8501 in your browser.

## Interactive Demo Features

### 🔒 Secure Agent Tab
- Enter custom queries to test the secure pipeline
- See real-time validation and processing steps
- Observe prompt injection blocking
- View YAML prompt loading and compilation
- Monitor LLM responses and output validation

### ⚠️ Vulnerable Demo Tab
- Compare with unsafe prompt construction
- See how direct string interpolation enables injection
- Understand the security risks of vulnerable approaches

## Project Flow

When you enter a query in the Streamlit UI:

1. **Input Validation**: Checks for injection attempts, sensitive data, length limits
2. **Prompt Loading**: Loads current YAML prompt version with metadata
3. **Prompt Compilation**: Builds ChatPromptTemplate with few-shot examples
4. **Variable Substitution**: Applies `partial()` for platform_name and support_tier
5. **LLM Invocation**: Calls Groq API with secure prompt structure
6. **Output Validation**: Checks response for leakage or policy violations
7. **Result Display**: Shows final response with expandable processing details

## Secure vs Vulnerable Prompting

### Secure Approach
```python
# Uses ChatPromptTemplate with role separation
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a {support_tier} agent for {platform_name}..."),
    ("human", "{user_query}")
])
prompt = prompt.partial(platform_name="CloudCart", support_tier="Premium")
```

### Vulnerable Approach
```python
# Direct string interpolation - UNSAFE
system_prompt = f"You are a {tier} agent for {platform}..."
full_prompt = f"{system_prompt}\nUser: {user_input}"
```

## YAML Prompt Versioning

### Structure
```yaml
metadata:
  version: "1.1.0"
  description: "Enhanced security prompt"
system_prompt: |
  You are a {support_tier} agent for {platform_name}...
few_shot_examples:
  - input: "How to reset password?"
    output: "Click forgot password..."
input_schema:
  type: object
  required:
    - user_query
  properties:
    user_query:
      type: string
      max_length: 500
```

### Version Management
- **v1.0.0**: Basic support prompt
- **v1.1.0**: Enhanced with injection resistance
- **current.yaml**: Active version (OS-level atomic symlink for zero-downtime)

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html
```

## Folder Structure

```
Genai_agenticai_rag/
├── streamlit_app.py     # Interactive demo application
├── app.py              # Simple entry point
├── requirements.txt    # Python dependencies
├── .env               # Environment variables
├── .gitignore         # Git ignore rules
│
├── configs/
│   └── settings.py    # Centralized configuration
│
├── prompts/
│   └── cloudcart/
│       ├── v1.0.0.yaml   # Initial prompt version
│       ├── v1.1.0.yaml   # Enhanced version
│       └── current.yaml  # Active version
│
├── src/
│   ├── agents/
│   │   └── cloudcart_agent.py    # Main agent logic
│   ├── llms/
│   │   └── groq_client.py        # LLM configuration
│   ├── models/
│   │   └── schemas.py           # Pydantic models
│   ├── prompts/
│   │   ├── prompt_builder.py    # Prompt construction
│   │   └── prompt_manager.py    # Version management
│   ├── validators/
│   │   ├── input_validator.py   # Input security
│   │   └── output_validator.py  # Output safety
│   └── utils/
│       └── logger.py            # Logging setup
│
├── tests/
│   ├── test_inputs.py     # Input validation tests
│   ├── test_outputs.py    # Output validation tests
│   └── test_agent.py      # Agent integration tests
│
└── demos/
    ├── vulnerable_demo.py # Shows injection vulnerability
    └── secure_demo.py     # Shows secure implementation
```

## Security Features Explained

### Input Validation
- Detects prompt injection keywords ("ignore previous", "reveal system")
- Blocks sensitive data (emails, phones, credit cards)
- Enforces length limits (500 chars max)

### Output Validation
- Prevents prompt leakage detection
- Blocks hallucinated product data
- Enforces content policy compliance

### Prompt Security
- Uses parameterized templates instead of string concatenation
- Applies variables via `partial()` method
- Maintains strict role separation (system vs human)

## Contributing

1. Follow SOLID principles and type safety
2. Add comprehensive tests for new features
3. Update documentation for API changes
4. Use Rich logging for debug information

## License

This project is part of a Generative AI assignment and is provided for educational purposes.

---

**Built with:** Python 3.11+, LangChain, Groq API, Streamlit  
**Architecture:** Clean Architecture, Modular Design  
**Security:** Multi-layer validation, Injection prevention  
**Demo:** Interactive Streamlit UI
