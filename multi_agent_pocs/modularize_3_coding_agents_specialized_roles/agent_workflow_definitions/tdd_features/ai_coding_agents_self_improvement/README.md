# AI Coding Agents Self-Improvement Workflows

## Development and Testing Workflow

This folder implements a complete enterprise SDLC for AI agent self-improvement, demonstrating test-driven development with automated remediation.

## Workflow Execution

### 1. Initial Agent Generation
```bash
python3 orchestrator.py custom agent_workflow_definitions/tdd_features/ai_coding_agents_self_improvement/sys_ops_agent_labor_and_permissioning_v1.json
```

**Purpose**: Generates v2 agents with specialized roles:
- Mistral Vibe: Code Generation Specialist
- Amazon Q: Testing and Validation Specialist  
- Gemini: Documentation and Synthesis Specialist

### 2. Enterprise SDLC Testing and Remediation
```bash
python3 orchestrator.py custom agent_workflow_definitions/tdd_features/ai_coding_agents_self_improvement/tdd_test_multi_task_capabilities_v1.json
```

**Enterprise SDLC Steps Implemented**:
1. **Unit Testing**: Execute actual failing command to detect issues
2. **Error Detection**: Capture syntax errors and failure modes
3. **Automated Remediation**: Trigger code generation to fix issues
4. **Validation**: Re-run tests to confirm fixes
5. **Documentation**: Auto-generate process documentation

## Files to Review After Execution

### Execution Results
```bash
cat workflow_results/ai_coding_agents_self_improvement/tdd_enterprise_agent_fix_v1_results.json
```

### Generated/Fixed Agents
```bash
cat cli_coding_agents/mistral_vibe_agent_v2.py
cat cli_coding_agents/amazon_q_agent_v2.py
cat cli_coding_agents/gemini_agent_v2.py
```

### Validation Tests
```bash
python3 cli_coding_agents/mistral_vibe_agent_v2.py documentation 'Update README.md'
python3 cli_coding_agents/amazon_q_agent_v2.py test-suite 'validate functionality'
python3 cli_coding_agents/gemini_agent_v2.py refactor 'improve code quality'
```

## Enterprise SDLC Compliance

✅ **Requirements Analysis**: Product manager user story implementation
✅ **Test-Driven Development**: Unit tests written before code fixes
✅ **Automated Testing**: Executable test commands, not AI prompts
✅ **Error Detection**: Systematic identification of failure modes
✅ **Automated Remediation**: AI-driven code generation for fixes
✅ **Validation**: Comprehensive testing of remediated code
✅ **Documentation**: Self-documenting workflow execution
✅ **Version Control**: Git-trackable development lineage

## Development Lineage

1. **Foundation**: `sys_ops_agent_labor_and_permissioning_v1.json` - Initial agent generation
2. **Testing**: `tdd_test_multi_task_capabilities_v1.json` - Enterprise SDLC implementation
3. **Results**: Functional multi-task agents with comprehensive error handling

## Maintainer Notes

- All workflows follow dependency management with `depends_on` chains
- Bootstrap fallback mechanism handles broken agents automatically
- Results are persisted in `workflow_results/` with execution metadata
- Agent division of labor maintained throughout remediation process