# Roadmap

voria's feature roadmap and product vision.

##  Current Status: PRODUCTION READY ✅

voria is feature-complete for its first official release (**v0.0.1**). All core orchestration, LLM, and GitHub integration components are stable and distributed via npm.

**Phase 1: Core Orchestration** ✅ COMPLETE
- Node.js CLI entry point with premium blue theme
- Python Engine for AI logic and agent loop
- NDJSON-based Inter-Process Communication (IPC)

**Phase 2: LLM Integration** ✅ COMPLETE
- Support for Claude, OpenAI, Gemini, Modal, and Kimi
- Token tracking and budget management
- Dynamic model discovery

**Phase 3: GitHub Integration** ✅ COMPLETE
- Issue fetching and listing
- Automatic PR creation and branch management
- Intelligent fix generation for GitHub issues

**Phase 4: Testing & Iteration** ✅ COMPLETE
- Multi-framework test execution (pytest, jest, go test)
- Failure analysis and automatic refinement (up to 5 iterations)
- Safe patch application with rollback support

**Phase 5: First Release (v0.0.1)** ✅ COMPLETE
- Public publication to npm as `@srizdebnath/voria`
- Integrated documentation and help system
- 100% test pass rate for CLI and Engine

---

##  What's Next: Phase 9 & Beyond

### Phase 9: Advanced Analysis (v0.2.0) 📋 PLANNED

#### Dependency Graph Analysis
**Status:** Design phase  
**Impact:** Higher-quality patches by understanding code relationships  
**Implementation:**
```python
# voria will analyze call chains
graph = CodeGraph(repo)
caller_chain = graph.find_callers("function_name")  # Who calls this?
impact = graph.estimate_impact(file_change)  # What breaks?
```

**Benefits:**
- Avoid breaking dependent code
- Better context for LLM  
- Predict side effects

#### File Relationship Understanding
**Status:** Design phase  
**Features:**
- Import chain analysis
- Shared data structure mapping
- Side effect prediction
- Cross-module behavior analysis

#### Risk Scoring
**Status:** Design phase  
**Example Scores:**
```
Low risk (0-2):
  ✅ Add new method to unused class
  ✅ Update docstring  
  ✅ Add new config option

Medium risk (3-5):
  🟡 Modify function signature
  🟡 Change return type
  🟡 Remove deprecated code

High risk (6-10):
  ⚠️ Modify shared data structure
  ⚠️ Change core orchestration logic
  ⚠️ Update IPC protocol
```

#### Context-Aware Selection
**Status:** Design phase  
**Benefit:** Only include affected code in context window
```
# voria will automatically reduce context size
Full repo: 50,000 lines
Affected modules: 2,000 lines  # 96% reduction
Context sent to LLM: 2,000 lines  # Same quality, less cost
```

---

### Phase 10: Enterprise Features (v0.3.0) 📋 PLANNED

#### Organization Management
**Status:** Planning  
**Features:**
- Multiple teams per organization
- Role-based access control (RBAC)
- Resource quotas by team
- Cost allocation to projects
- Team dashboards and analytics

#### Team Collaboration
**Status:** Planning  
**Features:**
- Pull request integration (voria creates PRs)
- Code review requests
- Approval workflows
- Merge policies enforcement
- Team notifications and alerts

#### Compliance & Audit
**Status:** Planning  
**Features:**
- Detailed audit logs
- Who made what change and when
- Cost reporting and analytics
- Approval trail for regulated environments
- HIPAA/SOC2 readiness
- Compliance certifications

---

##  Future Capabilities (Phase 11+)

### Distributed Execution
🔮 **Concept:** Run multiple issue fixes in parallel  
**Benefits:** Handle backlogs faster  
**Challenge:** Coordinating across team members  
**Timeline:** Q3 2026

### IDE Integration
🔮 **Concept:** voria inside VS Code / JetBrains / IntelliJ  
**Benefits:** Real-time AI assistance while coding  
**Challenge:** UI complexity in IDE constraints  
**Timeline:** Q4 2026

### Multi-Provider Optimization
🔮 **Concept:** Use different LLMs for different tasks  
**Example:**
- Fast model for code analysis
- Best quality for generation
- Specialized models for specific languages
**Timeline:** Q3 2026

### Predictive Testing
🔮 **Concept:** Run tests in parallel before applying patches  
**Benefits:** Faster feedback, better quality  
**Challenge:** Managing test infrastructure  
**Timeline:** Q4 2026

### CI/CD Integration
🔮 **Concept:** voria as a GitHub Action, GitLab/Jenkins plugin  
**Benefits:** Automated fixes in CI/CD pipelines  
**Timeline:** Q2 2026

---

##  Release Timeline

| Version | Status | Release Date | Key Features |
|---------|--------|--------------|--------------|
| v0.0.1 | ✅ Released | April 2026 | Basic foundation |
| v0.0.1 | ✅ Released | April 2026 | Full LLM support |
| v0.0.1 | ✅ Released | Apr 10, 2026 | Production-ready |
| v0.1.0 | 📋 Planned | Q2 2026 | Advanced analysis |
| v0.2.0 | 📋 Planned | Q3 2026 | Enterprise features |
| vv0.0.1 | 📋 Planned | Q4 2026 | Stable API + IDE integration |

---

##  Success Metrics

**Completed Goals:**
- ✅ 5 LLM providers integrated
- ✅ 100% test suite passing
- ✅ All phases shipped and tested
- ✅ Published to npm as global tool
- ✅ Production-ready code with no critical bugs
- ✅ Multi-framework test support (pytest, jest, go)
- ✅ GitHub issue fetching and PR creation
- ✅ Safe patch application with rollback

**Upcoming Metrics:**
- 📊 Advanced code analysis (dependency graphs)
- 📊 Risk scoring engine
- 📊 Enterprise feature parity
- 📊 Community plugins and extensions

---

##  How to Contribute

We're looking for contributions in several areas:

**High Priority:**
- [ ] Dependency graph analysis implementation
- [ ] Risk scoring engine
- [ ] Additional language support
- [ ] Enhanced IDE integrations

**Medium Priority:**
- [ ] Performance optimizations
- [ ] Better error messages
- [ ] Documentation improvements
- [ ] CI/CD plugin templates

**Nice to Have:**
- [ ] Web dashboard
- [ ] Advanced analytics
- [ ] Custom LLM integration templates
- [ ] Plugin marketplace

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.
- Interactive configuration
- Plugin system
- More LLM providers (Modal, Gemini, Claude, Kimi)

### v0.0.1 (April 2026) ✅
- Enhanced test failure analysis
- Batch processing
- Performance improvements
- Documentation overhaul

---

##  Community Contribution Opportunities

### Easy (Good for Newcomers)
- [ ] Add new test framework support (Jasmine, Jest, Vitest)
- [ ] Add language support (Go, Ruby, PHP)
- [ ] Documentation improvements
- [ ] Bug fixes in open issues

### Medium (Getting Serious)
- [ ] New LLM provider support (Anthropic, Mistral, Llama)
- [ ] VCS system support (Gitea, Gitlab)
- [ ] CI/CD integrations (GH Actions, GitLab CI, Jenkins)
- [ ] Performance optimizations

### Hard (Expert Level)
- [ ] Graph analysis implementation
- [ ] Risk analysis engine
- [ ] Team collaboration features
- [ ] Audit logging system

**Want to help?** See [CONTRIBUTING.md](CONTRIBUTING.md)

---

##  Feature Request Process

### How to Request Features

1. **Check existing requests** - https://github.com/Srizdebnath/voria/discussions
2. **Create discussion** with:
   - What problem it solves
   - How you'd use it
   - Why it matters
3. **Get feedback** - Community votes/discusses
4. **Implement or report** - We prioritize based on demand

### Prioritization

We use this framework:

| Priority | Impact | Effort | Timeline |
|----------|--------|--------|----------|
| 🔴 Critical | High | Low | This week |
| 🟠 High | High | Medium | This month |
| 🟡 Medium | Medium | Medium | This quarter |
| 🟢 Low | Low-Med | Any | Later |
| ⚪ Nice-to-have | Low | High | When ready |

---

##  Success Metrics

We track progress by:

- **Adoption:** Downloads, GitHub stars, active users
- **Quality:** Bug reports, test coverage, performance
- **Community:** Contributors, issues resolved, discussions
- **Enterprise:** Organizations using voria, team seats


---

##  Feedback Loop

### How We Gather Input
1. **GitHub Issues** - Bug reports
2. **Discussions** - Feature ideas
3. **Usage telemetry** - What features are used
4. **Direct feedback** - Email to support@voria.dev

### How Decisions Are Made
1. **Community votes** on proposals
2. **Roadmap alignment** with product strategy
3. **Implementation complexity** assessment
4. **Resource availability**
5. **Time to value** consideration

---

##  Getting Started with Beta Features

### Enable Beta Features

```bash
# Add to ~/.voria/config.json
{
  "beta_features": ["graph_analysis", "risk_scoring"],
  "enable_telemetry": true  # Help us improve
}
```

### Provide Feedback

Found an issue with a beta feature?
```bash
voria --report-beta-issue graph-analysis
# Opens form to describe issue
```

---

##  Contact & Support

- **GitHub:** [Discussions](https://github.com/Srizdebnath/voria/discussions)
- **Email:** srizd449@gmail.com


---

**Last Updated:** April 2026
**Next Review:** End of Q1 2026

**See Also:**
- [ARCHITECTURE.md](ARCHITECTURE.md) - Current system design
- [DESIGN_DECISIONS.md](DESIGN_DECISIONS.md) - Why things are the way they are
- [CONTRIBUTING.md](CONTRIBUTING.md) - How to contribute
