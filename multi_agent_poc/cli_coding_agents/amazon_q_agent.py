#!/usr/bin/env python3
"""
Amazon Q Agent - Documentation and Architecture Specialist

This agent specializes in generating comprehensive documentation,
architecture diagrams, and system design documentation.
"""

import sys
import os
import boto3
from botocore.exceptions import ClientError
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv
import subprocess

# Load environment variables
load_dotenv()

# --- Configuration Constants ---
AGENT_NAME = "Amazon Q"
ROLE = "Documentation and Architecture Specialist"
SYSTEM_INSTRUCTION = (
    "You are an expert technical writer and solutions architect. "
    "Generate comprehensive documentation, architecture diagrams, "
    "and system design documentation. Focus on clarity, completeness, "
    "and adherence to industry best practices."
)

# AWS Configuration
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AWS_PROFILE = os.getenv("AWS_PROFILE", "default")

class AmazonQAgent:
    """
    Amazon Q Agent for documentation and architecture tasks.
    """
    
    def __init__(self):
        """Initialize the Amazon Q agent."""
        self.session = boto3.Session(profile_name=AWS_PROFILE, region_name=AWS_REGION)
        print(f"✅ {AGENT_NAME} Agent initialized with AWS integration")
        print(f"Region: {AWS_REGION}, Profile: {AWS_PROFILE}")
    
    def generate_documentation(self, code_content: str, doc_type: str = "module") -> Dict[str, Any]:
        """Generate comprehensive documentation for the given code."""
        prompt = f"""As a technical writer, generate comprehensive {doc_type} documentation for:

Code:
```python
{code_content}
```

Include:
1. Overview and purpose
2. Installation and setup
3. API reference
4. Usage examples
5. Best practices
6. Troubleshooting guide"""
        
        return self._generate_response(prompt, "documentation")
    
    def create_architecture_diagram(self, system_description: str, format: str = "mermaid") -> Dict[str, Any]:
        """Create architecture diagram based on system description."""
        prompt = f"""As a solutions architect, create a {format} architecture diagram for:

System Description:
{system_description}

Include:
1. Main components and their relationships
2. Data flow between components
3. External dependencies
4. Deployment architecture
5. Key interfaces and protocols"""
        
        return self._generate_response(prompt, "architecture_diagram")
    
    def generate_api_docs(self, api_endpoints: List[str]) -> Dict[str, Any]:
        """Generate API documentation from endpoints."""
        endpoints_list = "\n".join([f"- {ep}" for ep in api_endpoints])
        prompt = f"""Generate comprehensive API documentation for these endpoints:

Endpoints:
{endpoints_list}

Include:
1. Endpoint descriptions
2. Request/response formats
3. Authentication requirements
4. Error codes and handling
5. Usage examples
6. Rate limiting information"""
        
        return self._generate_response(prompt, "api_documentation")
    
    def create_user_guide(self, feature_description: str) -> Dict[str, Any]:
        """Create user guide for specific features."""
        prompt = f"""Create a user guide for this feature:

Feature:
{feature_description}

Include:
1. Feature overview
2. Step-by-step instructions
3. Screenshots/diagrams (describe)
4. Common use cases
5. Troubleshooting tips
6. FAQ section"""
        
        return self._generate_response(prompt, "user_guide")
    
    def _generate_response(self, prompt: str, task_type: str) -> Dict[str, Any]:
        """Generate response using AWS services or placeholder."""
        # Placeholder implementation - replace with actual Amazon Q API calls
        print(f"📝 Generating {task_type} response...")
        
        # In a real implementation, this would call Amazon Q API
        # For POC, we'll generate placeholder responses
        
        if "documentation" in task_type:
            response = self._generate_placeholder_documentation(prompt)
        elif "architecture" in task_type:
            response = self._generate_placeholder_architecture(prompt)
        elif "api" in task_type:
            response = self._generate_placeholder_api_docs(prompt)
        else:
            response = self._generate_placeholder_user_guide(prompt)
        
        return {
            "success": True,
            "task_type": task_type,
            "response": response,
            "placeholder": True,
            "message": "This is a placeholder response. Implement AWS Amazon Q integration for real functionality."
        }
    
    def _generate_placeholder_documentation(self, prompt: str) -> str:
        """Generate placeholder documentation response."""
        return f"""# Comprehensive Documentation

## Overview
This documentation covers the implementation and usage of [Module/Component Name].

## Installation

### Prerequisites
- Python 3.12+
- Required dependencies (see requirements.txt)

### Setup
```bash
pip install -r requirements.txt
```

## API Reference

### Functions

#### `function_name(param1, param2)`
- **Parameters**:
  - `param1` (type): Description
  - `param2` (type): Description
- **Returns**: (type) Description
- **Raises**: ExceptionType - Description

## Usage Examples

### Basic Usage
```python
from module import function_name

result = function_name(value1, value2)
print(result)
```

### Advanced Usage
```python
# Complex example with error handling
try:
    result = function_name(complex_input, options)
    process_result(result)
except ValueError as e:
    handle_error(e)
```

## Best Practices

1. **Error Handling**: Always handle potential exceptions
2. **Performance**: Consider caching for repeated operations
3. **Security**: Validate all inputs and outputs
4. **Logging**: Use appropriate logging levels

## Troubleshooting

### Common Issues

**Issue**: Problem description
- **Cause**: Likely causes
- **Solution**: Step-by-step resolution

### Debugging Tips
- Enable debug logging
- Check input validation
- Verify environment configuration
"""
    
    def _generate_placeholder_architecture(self, prompt: str) -> str:
        """Generate placeholder architecture diagram."""
        return f"""# Architecture Diagram (Mermaid Format)

```mermaid
%% Example architecture diagram
flowchart TD
    A[Client Application] --> B[API Gateway]
    B --> C[Authentication Service]
    B --> D[Main Application]
    D --> E[Database]
    D --> F[Cache]
    D --> G[External Services]

    style A fill:#f9f,stroke:#333
    style B fill:#bbf,stroke:#333
    style D fill:#bfb,stroke:#333
```

## Component Description

### API Gateway
- **Purpose**: Entry point for all client requests
- **Responsibilities**:
  - Request routing
  - Load balancing
  - Rate limiting
  - Authentication

### Main Application
- **Purpose**: Core business logic processing
- **Components**:
  - Service Layer
  - Business Logic
  - Data Access
  - Integration Layer

### Data Flow
1. Client sends request to API Gateway
2. Gateway authenticates and routes request
3. Main application processes business logic
4. Database operations performed as needed
5. Response returned through gateway to client

## Deployment Architecture

### Production Environment
- **Scaling**: Horizontal scaling with auto-scaling groups
- **Availability**: Multi-AZ deployment
- **Monitoring**: CloudWatch metrics and alarms
- **Logging**: Centralized logging with retention

### Development Environment
- **Scaling**: Single instance
- **Availability**: Single AZ
- **Monitoring**: Basic metrics
- **Logging**: Local logging
"""
    
    def _generate_placeholder_api_docs(self, prompt: str) -> str:
        """Generate placeholder API documentation."""
        return f"""# API Documentation

## Authentication

All API endpoints require authentication using API keys.

**Header**: `X-API-Key: your_api_key_here`

**Rate Limits**: 100 requests per minute per API key

## Endpoints

### GET /api/resource

**Description**: Retrieve resource information

**Parameters**:
- `id` (string, required): Resource identifier
- `fields` (string, optional): Comma-separated list of fields to return

**Response**:
```json
{
  "success": true,
  "data": {
    "id": "resource123",
    "name": "Resource Name",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-02T00:00:00Z"
  }
}
```

**Error Codes**:
- `401 Unauthorized`: Invalid or missing API key
- `404 Not Found`: Resource not found
- `429 Too Many Requests`: Rate limit exceeded

### POST /api/resource

**Description**: Create a new resource

**Request Body**:
```json
{
  "name": "New Resource",
  "description": "Resource description",
  "tags": ["tag1", "tag2"]
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "id": "new_resource_id",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

## Usage Examples

### Python Example
```python
import requests

api_key = "your_api_key_here"
headers = {"X-API-Key": api_key}

# GET request
response = requests.get("https://api.example.com/api/resource?id=123", headers=headers)
data = response.json()

# POST request
new_resource = {"name": "Test", "description": "Test resource"}
response = requests.post("https://api.example.com/api/resource", json=new_resource, headers=headers)
result = response.json()
```

### Error Handling
```python
try:
    response = requests.get("https://api.example.com/api/resource?id=999", headers=headers)
    response.raise_for_status()
    data = response.json()
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 404:
        print("Resource not found")
    elif e.response.status_code == 429:
        print("Rate limit exceeded")
    else:
        print(f"API error: {e}")
```
"""
    
    def _generate_placeholder_user_guide(self, prompt: str) -> str:
        """Generate placeholder user guide."""
        return f"""# User Guide: [Feature Name]

## Overview

[Feature Name] allows you to [brief description of what the feature does and its benefits].

## Getting Started

### Prerequisites
- Active account
- Required permissions
- Supported browser (Chrome, Firefox, Safari, Edge)

### Accessing the Feature
1. Log in to the application
2. Navigate to [Menu] > [Submenu] > [Feature Name]
3. Click "Get Started" button

## Step-by-Step Instructions

### Basic Usage

1. **Step 1**: Description of first step
   - Click [button/element]
   - Enter [information]
   - Select [option]

2. **Step 2**: Description of second step
   - Review [information]
   - Confirm [details]
   - Click "Continue"

3. **Step 3**: Description of final step
   - Verify [results]
   - Save or export [output]
   - Complete the process

### Advanced Features

**Feature A**: Description
1. Access through [menu/path]
2. Configure [settings]
3. Apply [changes]

**Feature B**: Description
1. Enable in [settings]
2. Customize [options]
3. Save [configuration]

## Common Use Cases

### Use Case 1: [Description]
1. Start with [initial condition]
2. Perform [action]
3. Achieve [result]

### Use Case 2: [Description]
1. Begin with [situation]
2. Execute [steps]
3. Obtain [outcome]

## Troubleshooting

### Common Issues

**Issue**: [Problem Description]
- **Cause**: [Likely causes]
- **Solution**: [Step-by-step resolution]

**Issue**: [Another Problem]
- **Cause**: [Possible reasons]
- **Solution**: [Resolution steps]

### FAQ

**Q**: [Frequent Question]?
**A**: [Detailed Answer]

**Q**: [Another Question]?
**A**: [Comprehensive Response]

## Best Practices

1. **Regular Backups**: Always back up before major operations
2. **Incremental Changes**: Make small, testable changes
3. **Review Settings**: Double-check configurations before applying
4. **Monitor Performance**: Watch for unusual behavior
5. **Stay Updated**: Keep software current with latest versions

## Additional Resources

- [Official Documentation](#)
- [Video Tutorials](#)
- [Community Forum](#)
- [Support Contact](#)
"""

def main():
    """
    Main function for Amazon Q Agent.
    """
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} <task_type> \"<request_details>\"")
        print(f"\n{AGENT_NAME} - {ROLE}")
        print("\nAvailable task types:")
        print("  documentation <code_file> - Generate comprehensive documentation")
        print("  architecture <description> - Create architecture diagram")
        print("  api-docs <endpoints> - Generate API documentation")
        print("  user-guide <feature> - Create user guide")
        print("\nExamples:")
        print("  python amazon_q_agent.py documentation my_module.py")
        print("  python amazon_q_agent.py architecture \"Three-tier web application\"")
        print("  python amazon_q_agent.py api-docs \"/api/users /api/posts\"")
        print("  python amazon_q_agent.py user-guide \"User authentication system\"")
        sys.exit(1)
    
    task_type = sys.argv[1]
    request_details = sys.argv[2] if len(sys.argv) > 2 else None
    
    print(f"\n{AGENT_NAME} Agent Activated")
    print(f"Role: {ROLE}")
    print(f"System Instruction: {SYSTEM_INSTRUCTION}")
    print(f"Task Type: {task_type}")
    if request_details:
        print(f"Request: {request_details}")
    
    # Initialize the agent
    try:
        agent = AmazonQAgent()
    except Exception as e:
        print(f"❌ Failed to initialize {AGENT_NAME} Agent: {e}")
        print("Ensure AWS credentials are properly configured.")
        sys.exit(1)
    
    # Read code file if provided
    code_content = ""
    api_endpoints = []
    
    if request_details:
        if task_type == "api-docs" and "," in request_details:
            # Parse as comma-separated endpoints
            api_endpoints = [ep.strip() for ep in request_details.split(",")]
            print(f"📋 Parsed {len(api_endpoints)} API endpoints")
        elif os.path.isfile(request_details):
            # Read code file
            try:
                with open(request_details, 'r', encoding='utf-8') as f:
                    code_content = f.read()
                print(f"📄 Loaded code from: {request_details}")
            except Exception as e:
                print(f"❌ Error reading file: {e}")
                sys.exit(1)
        else:
            code_content = request_details
    
    # Execute the appropriate task
    try:
        if task_type == "documentation":
            result = agent.generate_documentation(code_content)
        elif task_type == "architecture":
            result = agent.create_architecture_diagram(code_content)
        elif task_type == "api-docs":
            result = agent.generate_api_docs(api_endpoints)
        elif task_type == "user-guide":
            result = agent.create_user_guide(code_content)
        else:
            print(f"❌ Unknown task type: {task_type}")
            sys.exit(1)
        
        # Display results
        if result["success"]:
            print(f"\n✅ Task completed successfully!")
            print(f"Task Type: {result['task_type']}")
            if result.get("placeholder"):
                print(f"📝 {result['message']}")
            print(f"\n{'='*60}")
            print("RESULTS:")
            print('='*60)
            print(result["response"])
        else:
            print(f"❌ Task failed: {result.get('error', 'Unknown error')}")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()