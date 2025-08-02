# Agent Coordination Guidelines - Korean Stock Backtesting Simulation

## Multi-Agent Task Coordination Framework

**Last Updated**: 2025-08-01 21:55

This document defines how multiple specialized agents coordinate on complex tasks that span multiple domains in the Korean Stock Backtesting Simulation project.

## Coordination Principles

### 1. Lead Agent Assignment
For multi-domain tasks, the Project Manager assigns a **Lead Agent** based on the primary domain:
- **Primary Domain**: The most critical aspect of the task
- **Lead Agent**: Takes ownership of task completion and final integration
- **Supporting Agents**: Provide domain expertise and deliverables to the Lead Agent

### 2. Communication Protocol
```
Project Manager → Task Analysis → Lead Agent Assignment → Supporting Agent Coordination → Integration → Delivery
```

**Key Rules**:
- All agents report progress to Project Manager
- Lead Agent coordinates directly with supporting agents
- Project Manager ensures integration quality and timeline adherence
- No agent works in isolation on multi-agent tasks

### 3. Handoff Standards
Each agent must provide:
- **Clear deliverables** with specifications met
- **Integration instructions** for other agents
- **Testing verification** that their component works
- **Documentation** of any assumptions or dependencies

## Common Multi-Agent Scenarios

### Scenario 1: New Feature Development
**Example**: "Add real-time Korean stock alerts with notification UI"

**Agent Assignment**:
- **Lead Agent**: securities-ui-engineer (UI is primary user-facing component)
- **Supporting Agents**: 
  - automated-trading-advisor (real-time data integration)
  - stock-trading-expert (alert trigger logic)

**Coordination Flow**:
1. **Project Manager**: Analyzes requirements and assigns Lead Agent
2. **securities-ui-engineer**: Designs notification UI components and integration points
3. **automated-trading-advisor**: Develops real-time data monitoring and WebSocket connections
4. **stock-trading-expert**: Creates alert condition algorithms and trigger logic
5. **Lead Agent**: Integrates all components and ensures end-to-end functionality
6. **Project Manager**: Validates integration and approves completion

### Scenario 2: Performance Optimization
**Example**: "Optimize backtesting performance and add progress indicators"

**Agent Assignment**:
- **Lead Agent**: dx-ax-platform-consultant (architecture optimization is primary)
- **Supporting Agents**:
  - stock-trading-expert (backtesting algorithm optimization)
  - securities-ui-engineer (progress indicator UI)
  - code-reviewer (performance validation)

**Coordination Flow**:
1. **dx-ax-platform-consultant**: Analyzes performance bottlenecks and creates optimization plan
2. **stock-trading-expert**: Optimizes backtesting algorithms and data processing
3. **securities-ui-engineer**: Implements progress indicators and loading states
4. **code-reviewer**: Validates performance improvements and code quality
5. **Lead Agent**: Integrates optimizations and measures performance gains
6. **Project Manager**: Approves performance targets are met

### Scenario 3: Bug Fix with Multiple Components
**Example**: "Fix chart data synchronization issues between real-time updates and historical data"

**Agent Assignment**:
- **Lead Agent**: automated-trading-advisor (data synchronization is core issue)
- **Supporting Agents**:
  - securities-ui-engineer (chart component fixes)
  - code-reviewer (root cause analysis and testing)

**Coordination Flow**:
1. **code-reviewer**: Analyzes root cause and identifies affected components
2. **automated-trading-advisor**: Fixes data synchronization logic and caching
3. **securities-ui-engineer**: Updates chart components to handle synchronized data
4. **Lead Agent**: Tests end-to-end data flow and synchronization
5. **Project Manager**: Validates bug is resolved and no regressions introduced

## Agent Responsibility Matrix

| Task Type | Lead Agent Priority Order | Supporting Agents |
|-----------|---------------------------|-------------------|
| **New UI Feature** | securities-ui-engineer → automated-trading-advisor → stock-trading-expert | Others as needed |
| **Data Integration** | automated-trading-advisor → securities-ui-engineer → stock-trading-expert | dx-ax-platform-consultant |
| **Trading Algorithm** | stock-trading-expert → automated-trading-advisor → securities-ui-engineer | code-reviewer |
| **Performance Issue** | dx-ax-platform-consultant → code-reviewer → domain-specific | All others |
| **Architecture Change** | dx-ax-platform-consultant → automated-trading-advisor → securities-ui-engineer | code-reviewer |
| **Quality/Security** | code-reviewer → dx-ax-platform-consultant → domain-specific | All others |

## Integration Checkpoints

### Before Starting Multi-Agent Task
- [ ] Project Manager assigns Lead Agent and Supporting Agents
- [ ] Lead Agent creates integration plan with clear deliverables
- [ ] All agents confirm understanding of their responsibilities
- [ ] Dependencies and handoff points identified

### During Execution
- [ ] Regular progress updates to Project Manager
- [ ] Lead Agent coordinates with Supporting Agents
- [ ] Early integration testing of components
- [ ] Issue escalation to Project Manager if needed

### Before Completion
- [ ] All components integrated by Lead Agent
- [ ] End-to-end testing completed
- [ ] code-reviewer validates quality if not already involved
- [ ] Project Manager approves final deliverable

## Quality Gates for Multi-Agent Tasks

### Code Quality
- All code changes must be reviewed by code-reviewer
- No direct merging of multi-agent work without integration testing
- Korean market specific validations by automated-trading-advisor

### Architecture Consistency
- dx-ax-platform-consultant validates architectural decisions
- No breaking changes without explicit approval
- Performance impact assessed for user-facing changes

### User Experience
- securities-ui-engineer validates all UI changes
- Korean localization and formatting verified
- Responsive design and accessibility maintained

### Domain Expertise
- stock-trading-expert validates all trading logic and calculations
- Korean market compliance and accuracy verified
- Financial calculation precision maintained

## Escalation Procedures

### When to Escalate to Project Manager
1. **Conflicting Requirements**: Agents disagree on approach or priorities
2. **Technical Blockers**: Dependencies cannot be resolved between agents
3. **Timeline Issues**: Task complexity exceeds initial estimates
4. **Quality Concerns**: Integration issues or quality gate failures
5. **Scope Changes**: Requirements expand beyond initial analysis

### Escalation Process
1. **Agent** identifies issue and attempts resolution with peer agents
2. **Lead Agent** facilitates discussion and seeks consensus
3. **Project Manager** intervenes if no resolution within reasonable time
4. **Decision**: Project Manager makes final decision with rationale
5. **Implementation**: All agents proceed with approved approach

## Success Metrics

### Coordination Efficiency
- Time from task assignment to completion
- Number of integration iterations required
- Quality of handoffs between agents

### Quality Outcomes
- Defect rate in multi-agent deliverables
- Integration testing success rate
- User acceptance of complex features

### Agent Collaboration
- Cross-agent communication effectiveness
- Knowledge sharing and learning
- Conflict resolution speed

This coordination framework ensures complex multi-agent tasks are completed efficiently while maintaining the high quality standards required for the Korean Stock Backtesting Simulation project.