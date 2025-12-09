# GitHub Labels Guide

This document describes all the labels available for issues and pull requests in the Credit Risk RAG System project.

## 📊 Label Categories

### Priority Labels
- **priority:critical** - Critical priority, requires immediate attention (Red: #b60205)
- **priority:high** - High priority, important tasks (Orange: #d93f0b)
- **priority:medium** - Medium priority, normal tasks (Yellow: #fbca04)
- **priority:low** - Low priority, can be deferred (Green: #0e8a16)

### Type Labels
- **type:feature** - New feature or enhancement (Light Blue: #a2eeef)
- **type:bug** - Bug or defect (Red: #d73a4a)
- **type:docs** - Documentation improvements (Blue: #0075ca)
- **type:refactor** - Code refactoring (Gray: #cfd3d7)
- **type:performance** - Performance improvements (Light Blue: #c5def5)

### Component Labels

#### Core Components
- **rag** - RAG engine and retrieval (Orange: #d93f0b)
- **llm** - LLM integration and prompts (Pink: #e99695)
- **ml** - Machine learning models (Purple: #5319e7)
- **api** - REST API related (Blue: #0075ca)
- **database** - Database related (Light Blue: #c5def5)

#### Domain Specific
- **finance** - Financial analysis features (Teal: #006b75)
- **risk** - Risk assessment and scoring (Dark Red: #b60205)
- **analytics** - Analytics and reporting (Yellow: #e4e669)
- **reporting** - Report generation (Light Yellow: #fef2c0)
- **document-processing** - Document parsing and processing (Peach: #f9d0c4)

#### Compliance & Security
- **security** - Security and compliance (Red: #d73a4a)
- **compliance** - Regulatory compliance (Light Green: #c2e0c6)
- **regulatory** - Banking regulations (Purple: #7057ff)

#### Infrastructure & DevOps
- **infrastructure** - Infrastructure and DevOps related (Green: #0e8a16)
- **setup** - Initial setup and configuration (Light Blue: #bfdadc)
- **docker** - Docker and containerization (Blue: #0052cc)
- **kubernetes** - Kubernetes orchestration (Blue: #326ce5)
- **ci-cd** - CI/CD pipelines (Green: #128a0c)
- **monitoring** - Monitoring and observability (Blue: #1d76db)

#### Testing
- **testing** - Testing and QA (Yellow: #fbca04)

### Status Labels
- **in-progress** - Currently being worked on (Yellow: #fbca04)
- **blocked** - Blocked by dependencies (Pink: #e99695)
- **needs-review** - Awaiting code review (Purple: #d4c5f9)

### Community Labels
- **good-first-issue** - Good for newcomers (Purple: #7057ff)
- **help-wanted** - Extra attention needed (Teal: #008672)

### Default GitHub Labels (Keep for compatibility)
- **bug** - Something isn't working (Red: #d73a4a)
- **documentation** - Improvements or additions to documentation (Blue: #0075ca)
- **duplicate** - This issue or pull request already exists (Gray: #cfd3d7)
- **enhancement** - New feature or request (Light Blue: #a2eeef)
- **good first issue** - Good for newcomers (Purple: #7057ff)
- **help wanted** - Extra attention is needed (Teal: #008672)
- **invalid** - This doesn't seem right (Yellow: #e4e669)
- **question** - Further information is requested (Pink: #d876e3)
- **wontfix** - This will not be worked on (White: #ffffff)

## 🏷️ Label Usage Guidelines

### How to Label Issues

1. **Always add a priority label** - Every issue should have exactly one priority label
2. **Add a type label** - Every issue should have exactly one type label
3. **Add component labels** - Add 1-3 relevant component labels
4. **Add status labels** - Update as the issue progresses
5. **Add community labels** - If appropriate for new contributors

### Example Label Combinations

#### Issue #1: Project Setup
- `infrastructure`
- `setup`
- `priority:critical`
- `type:feature`

#### Feature: RAG Engine Implementation
- `rag`
- `llm`
- `priority:high`
- `type:feature`

#### Bug: API Authentication Failure
- `api`
- `security`
- `priority:critical`
- `type:bug`

#### Documentation: API Guide
- `api`
- `priority:medium`
- `type:docs`

#### Performance: Optimize Query Speed
- `rag`
- `database`
- `priority:medium`
- `type:performance`

## 📝 Adding Labels to Issues

### Using GitHub CLI
```bash
# Add single label
gh issue edit 1 --add-label "infrastructure"

# Add multiple labels
gh issue edit 1 --add-label "infrastructure,setup,priority:critical"

# Remove label
gh issue edit 1 --remove-label "bug"
```

### Using GitHub Web Interface
1. Open the issue
2. Click on "Labels" in the right sidebar
3. Select the appropriate labels
4. Labels are saved automatically

## 🔄 Label Maintenance

- Review labels quarterly to ensure they're still relevant
- Add new labels as the project evolves
- Deprecate labels that are no longer used
- Keep label descriptions up-to-date

## 📊 Label Statistics

Total Labels: 43
- Priority: 4
- Type: 5
- Component: 20
- Status: 3
- Community: 2
- Default: 9

---

**Last Updated:** November 2025
