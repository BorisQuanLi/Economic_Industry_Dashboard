#!/usr/bin/env python3
"""
Mistral Vibe Agent - Testing and Validation Specialist

This agent specializes in testing, validation, and quality assurance for the multi-agent POC project.
It focuses on ensuring code quality, reliability, and performance.

Integration with Mistral AI API for advanced testing and validation capabilities.
"""

import sys
import os
import subprocess
import requests
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- Configuration Constants ---
AGENT_NAME = "Mistral Vibe"
ROLE = "Testing and Validation Specialist"
SYSTEM_INSTRUCTION = (
    "You are an expert QA engineer and testing specialist. "
    "Create comprehensive test suites, validate code quality, "
    "and ensure software reliability. Focus on edge cases, "
    "performance testing, and adherence to best practices."
)

# Mistral API Configuration
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
MISTRAL_API_ENDPOINT = "https://api.mistral.ai/v1/chat/completions"

class MistralVibeAgent:
    """
    Mistral Vibe Agent for testing and validation tasks.
    """
    
    def __init__(self, api_key: str = None, system_instruction: str = None):
        """Initialize the Mistral Vibe agent."""
        self.api_key = api_key or MISTRAL_API_KEY
        self.system_instruction = system_instruction or SYSTEM_INSTRUCTION
        
        if not self.api_key or self.api_key == "your_mistral_api_key_here":
            print("⚠️  Warning: Mistral API key not configured. Using placeholder mode.")
            self.placeholder_mode = True
        else:
            self.placeholder_mode = False
            print("✅ Mistral Vibe Agent initialized with API integration")
    
    def generate_test_suite(self, code_content: str, requirements: str = None) -> Dict[str, Any]:
        """Generate a comprehensive test suite for the given code."""
        prompt = f"""As a testing and validation specialist, analyze the following code and generate a comprehensive test suite:

Code:
```python
{code_content}
```

Requirements:
{requirements or 'General testing requirements'}

Please provide:
1. Unit tests for individual functions
2. Integration tests for module interactions
3. Edge case tests
4. Performance test suggestions
5. Code quality recommendations

Follow best practices for Python testing using pytest."""
        
        return self._call_mistral_api(prompt, "test_suite_generation")
    
    def validate_code_quality(self, code_content: str) -> Dict[str, Any]:
        """Validate code quality and suggest improvements."""
        prompt = f"""As a code quality expert, analyze the following Python code and provide a detailed quality assessment:

Code:
```python
{code_content}
```

Please evaluate:
1. Code readability and style (PEP 8 compliance)
2. Error handling and robustness
3. Performance considerations
4. Security vulnerabilities
5. Maintainability and documentation
6. Best practices adherence

Provide specific recommendations for improvement."""
        
        return self._call_mistral_api(prompt, "code_quality_validation")
    
    def analyze_performance(self, code_content: str, use_case: str = None) -> Dict[str, Any]:
        """Analyze code performance and suggest optimizations."""
        prompt = f"""As a performance testing specialist, analyze the following code for performance characteristics:

Code:
```python
{code_content}
```

Use case: {use_case or 'General usage'}

Please provide:
1. Time complexity analysis
2. Space complexity analysis
3. Potential bottlenecks
4. Optimization suggestions
5. Scalability considerations
6. Benchmarking recommendations"""
        
        return self._call_mistral_api(prompt, "performance_analysis")
    
    def _call_mistral_api(self, prompt: str, task_type: str) -> Dict[str, Any]:
        """Call Mistral AI API with the given prompt."""
        if self.placeholder_mode:
            return self._generate_placeholder_response(prompt, task_type)
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": "mistral-large-latest",
            "messages": [
                {
                    "role": "system",
                    "content": self.system_instruction
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 2048
        }
        
        try:
            response = requests.post(
                MISTRAL_API_ENDPOINT,
                headers=headers,
                data=json.dumps(payload),
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            return {
                "success": True,
                "task_type": task_type,
                "response": result["choices"][0]["message"]["content"],
                "usage": result.get("usage", {}),
                "model": result.get("model", "mistral-large-latest")
            }
            
        except requests.exceptions.RequestException as e:
            print(f"❌ API Error: {e}")
            return {
                "success": False,
                "error": str(e),
                "task_type": task_type
            }
    
    def _generate_placeholder_response(self, prompt: str, task_type: str) -> Dict[str, Any]:
        """Generate a placeholder response when API key is not configured."""
        print(f"📝 Generating placeholder response for {task_type}...")
        
        # Generate different placeholder responses based on task type
        if "test_suite" in task_type:
            response_content = f"""# Comprehensive Test Suite for Requested Code

## Unit Tests
```python
def test_function_name():
    # Test normal case
    result = function_name(input_data)
    assert result == expected_output
    
    # Test edge cases
    with pytest.raises(ValueError):
        function_name(invalid_input)
```

## Integration Tests
```python
def test_module_integration():
    # Test how this module interacts with others
    module1 = Module1()
    module2 = Module2()
    result = module1.process(module2.get_data())
    assert result.status == "success"
```

## Edge Case Tests
- Test with empty inputs
- Test with maximum allowed values
- Test with invalid data types
- Test with None values
- Test with concurrent access

## Performance Test Suggestions
- Benchmark with different input sizes
- Test memory usage under load
- Measure response times
- Test with parallel execution

## Code Quality Recommendations
- Add type hints for better IDE support
- Include docstrings for all public functions
- Add logging for debugging purposes
- Consider using dataclasses for complex data structures
- Implement proper error handling"""
        
        elif "code_quality" in task_type:
            response_content = f"""# Code Quality Assessment

## Analysis Results

### ✅ Strengths
- Good function naming and organization
- Proper use of Python idioms
- Clear separation of concerns
- Appropriate error handling

### ⚠️  Areas for Improvement

1. **PEP 8 Compliance**
   - Some lines exceed 79 character limit
   - Inconsistent spacing around operators
   - Missing blank lines between functions

2. **Documentation**
   - Add docstrings for all public functions
   - Include type hints for better IDE support
   - Add module-level documentation

3. **Error Handling**
   - Add specific exception types
   - Include more detailed error messages
   - Consider custom exception classes

4. **Performance**
   - Cache repeated computations
   - Use generators for large datasets
   - Consider async/await for I/O operations

### 📋 Specific Recommendations
```python
# Before
def calculate(x, y):
    return x + y

# After (with improvements)
def calculate(x: float, y: float) -> float:
    '''Calculate the sum of two numbers.
    
    Args:
        x: First number
        y: Second number
        
    Returns:
        Sum of x and y
        
    Raises:
        TypeError: If inputs are not numbers
    '''
    if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
        raise TypeError("Inputs must be numbers")
    return x + y
```"""
        
        elif "performance" in task_type:
            response_content = f"""# Performance Analysis Report

## Complexity Analysis

### Time Complexity
- Overall: O(n log n) - dominated by sorting operations
- Best case: O(n) - when data is already sorted
- Worst case: O(n²) - with pathological input patterns

### Space Complexity
- O(n) - linear space usage
- Memory efficient for typical use cases

## Bottleneck Identification

### Potential Bottlenecks
1. **Data Loading**: I/O operations can be slow
2. **Sorting Operations**: O(n log n) complexity
3. **Nested Loops**: Watch for O(n²) patterns
4. **API Calls**: Network latency impact

## Optimization Suggestions

### Immediate Improvements
```python
# Use list comprehensions instead of loops
result = [process(x) for x in data if condition(x)]

# Cache expensive computations
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_computation(x):
    # ... computation here
    return result
```

### Architectural Recommendations
- Implement caching layer for repeated requests
- Use async/await for I/O-bound operations
- Consider parallel processing for CPU-bound tasks
- Optimize database queries with proper indexing

### Benchmarking Recommendations
```python
import time
from functools import wraps

def benchmark(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"Function executed in {end - start:.4f} seconds")
        return result
=======
        result = func(*args, **kwargs)
        end = time.time()
        execution_time = end - start
        print(f"Function executed in {execution_time:.4f} seconds")
        return result
    return wrapper

@benchmark
def your_function():
    # Function implementation
    pass
```
=======
### Benchmarking Recommendations
```python
import time
from functools import wraps

def benchmark(function_to_measure):
    @wraps(function_to_measure)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = function_to_measure(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Function executed in {execution_time:.4f} seconds")
        return result
    return wrapper

@benchmark
def example_function():
    # Your function implementation here
    pass
```"""
        
        else:
            response_content = f"""# Mistral Vibe Analysis Response

## Task: {task_type}

### Analysis Summary
This is a placeholder response demonstrating the capabilities of the Mistral Vibe agent.

### Key Findings
- Code structure appears logical and well-organized
- Function naming follows Python conventions
- Error handling could be enhanced
- Performance characteristics seem reasonable

### Recommendations
1. Add comprehensive test coverage
2. Implement proper logging
3. Consider adding type hints
4. Review error handling strategies
5. Optimize critical sections

### Next Steps
- Implement suggested improvements
- Run performance benchmarks
- Add integration tests
- Review security considerations"""
        
        return {
            "success": True,
            "task_type": task_type,
            "response": response_content,
            "placeholder": True,
            "message": "This is a placeholder response. Configure MISTRAL_API_KEY in .env for real API calls."
        }

def main():
    """
    Main function for Mistral Vibe Agent.
    """
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} <task_type> \"<request_details>\"")
        print(f"\n{AGENT_NAME} - {ROLE}")
        print("\nAvailable task types:")
        print("  test-suite <code_file> - Generate comprehensive test suite")
        print("  validate <code_file> - Validate code quality")
        print("  performance <code_file> - Analyze performance")
        print("\nExamples:")
        print("  python mistral_vibe_agent.py test-suite my_module.py")
        print("  python mistral_vibe_agent.py validate complex_function.py")
        print("  python mistral_vibe_agent.py performance slow_algorithm.py")
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
    agent = MistralVibeAgent()
    
    # Read code file if provided
    code_content = ""
    if request_details and os.path.isfile(request_details):
        try:
            with open(request_details, 'r', encoding='utf-8') as f:
                code_content = f.read()
            print(f"📄 Loaded code from: {request_details}")
        except Exception as e:
            print(f"❌ Error reading file: {e}")
            sys.exit(1)
    elif request_details:
        code_content = request_details
    
    # Execute the appropriate task
    try:
        if task_type == "test-suite":
            result = agent.generate_test_suite(code_content)
        elif task_type == "validate":
            result = agent.validate_code_quality(code_content)
        elif task_type == "performance":
            result = agent.analyze_performance(code_content)
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