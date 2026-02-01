# Agent Workflow Definitions

## Overview

This directory contains workflow definitions for the multi-agent orchestration system. Workflows define how AI agents collaborate to accomplish development tasks using a test-driven approach.

## Current Structure

```
agent_workflow_definitions/
├── compliance_docs/          # Compliance and audit workflows
├── quality_assurance/        # Quality validation workflows
├── sys_ops/                  # System operations workflows
└── tdd_features/             # Test-driven development workflows
```

## Workflow Types

### 1. TDD Workflows (`tdd_features/`)

Test-driven development workflows that follow the red-green-refactor cycle:

- **tdd_fix_broken_agents_v1.json**: Comprehensive agent fixing workflow
- **tdd_incremental_agent_fix_v1.json**: Incremental improvement approach
- **tdd_multi_task_cli_agent_capability.json**: Multi-task agent testing

**Usage**:
```bash
python3 orchestrator.py custom agent_workflow_definitions/tdd_features/tdd_incremental_agent_fix_v1.json
```

### 2. Quality Assurance Workflows (`quality_assurance/`)

Standardized quality validation processes:

- **ai_code_quality_gates_v1.json**: 7-step quality validation
- **ai_commit_template.json**: Commit message template

**Usage**:
```bash
python3 orchestrator.py custom agent_workflow_definitions/quality_assurance/ai_code_quality_gates_v1.json
```

### 3. System Operations Workflows (`sys_ops/`)

System-level operations and maintenance:

- **security_auth/**: Agent permission and security workflows
- **maintenance/**: System maintenance workflows
- **refactors/**: Code refactoring workflows

### 4. Compliance Workflows (`compliance_docs/`)

Compliance and audit workflows (placeholder structure):

- **audit_logs/**: Audit logging workflows
- **regulatory_standards/**: Regulatory compliance workflows

## Development Process

### Creating New Workflows

1. **Identify Requirements**: Define what the workflow should accomplish
2. **Design Workflow**: Create JSON definition with tasks and dependencies
3. **Test Workflow**: Execute and validate in extended-tree sandbox
4. **Document Results**: Add to workflow_results/ with execution logs
5. **Commit**: Follow SDLC best practices for version control

### Workflow JSON Structure

```json
{
  "workflow_id": "unique_identifier",
  "description": "Clear description of purpose",
  "tasks": {
    "task_id": {
      "task_id": "unique_task_id",
      "agent": "agent_type",
      "type": "task_type",
      "input": "detailed_instructions",
      "output_file": "optional_output_path",
      "depends_on": ["dependency_list"],
      "expected_result": "success_criteria"
    }
  }
}
```

### Best Practices

1. **Naming Convention**: Use clear, descriptive names with version numbers
2. **Versioning**: Increment versions for significant changes
3. **Documentation**: Include purpose and usage in workflow description
4. **Testing**: Always test in extended-tree before master-tree commit
5. **Organization**: Group related workflows in appropriate sub-folders

## Current Development Focus

### AI Agents Self-Improvement Story

**Objective**: Improve existing AI agents through TDD workflows

**Current Workflows**:
- ✅ TDD workflows for agent improvement
- ✅ Quality assurance validation
- ✅ Documentation templates

**Next Steps**:
1. Execute incremental TDD workflow
2. Validate with quality gates
3. Document results
4. Commit improvements

### Future Contexts (Postponed)

**Java Service Integration**: Deferred until current story complete

**AWS Infrastructure**: Deferred until current story complete

**Other Contexts**: Will be added when specific requirements arise

## Quality Assurance Process

All workflows should pass through the quality assurance process:

1. **Syntax Validation**: No syntax errors, PEP 8 compliance
2. **Functionality Testing**: All tasks execute correctly
3. **Security Scan**: No vulnerabilities
4. **Documentation**: Complete and accurate
5. **Performance**: Meets requirements

**Validation Command**:
```bash
python3 orchestrator.py custom agent_workflow_definitions/quality_assurance/ai_code_quality_gates_v1.json
```

## Version Control Strategy

### Commit Message Format

```
feat(workflow): add {workflow_name} v{version}

- Purpose: {clear_description}
- Tasks: {task_count} tasks with {dependency_count} dependencies
- Testing: Executed in extended-tree, all quality gates passed
- Documentation: Updated README and workflow_results

Addresses: #{issue_number}
Related: {parent_workflow}
```

### File Organization

- Keep workflows in appropriate sub-folders
- Version files with `_v1`, `_v2` suffixes
- Maintain clear development lineage

## Demo Preparation

### Key Artifacts

1. **TDD Execution**: Show incremental improvement
2. **Quality Validation**: Demonstrate professional standards
3. **Documentation**: Show auto-generated docs
4. **Version Control**: Display clean git history

### Demo Commands

```bash
# Show TDD process
python3 orchestrator.py custom agent_workflow_definitions/tdd_features/tdd_incremental_agent_fix_v1.json

# Show quality validation
python3 orchestrator.py custom agent_workflow_definitions/quality_assurance/ai_code_quality_gates_v1.json

# Show results
ls -la workflow_results/tdd_features/
ls -la workflow_results/quality_assurance/
```

## Future Enhancements

### Planned Improvements

1. **Context-Specific Folders**: When new contexts arise
2. **Workflow Templates**: Standardized templates for common patterns
3. **Automated Testing**: CI/CD integration for workflow validation
4. **Performance Metrics**: Benchmarking and optimization

### Potential Contexts

```
agent_workflow_definitions/
├── java_service/          # Java service integration
├── aws_infrastructure/    # AWS infrastructure management
├── frontend_components/   # Frontend component generation
└── data_pipelines/        # Data pipeline workflows
```

## Support

For questions or issues:
- Check existing workflow examples
- Review SDLC_BEST_PRACTICES.md
- Consult workflow execution results
- Examine git history for patterns

---

**Last Updated**: 01/28/2026
**Maintainer**: Boris Li
**Contact**: boris.quan.li@gmail.com
