# Demo Scenarios

## Overview

ZeroDay includes three pre-configured demo scenarios that showcase different organizational contexts and use cases. Each scenario contains realistic synthetic data to demonstrate the platform's capabilities.

## Available Scenarios

### 1. Startup Scenario

**Context:** Fast-growing tech startup with 15-30 employees

**Characteristics:**
- Agile development methodology
- Small, cross-functional teams
- Rapid iteration and MVP focus
- Limited documentation processes
- Informal communication channels

**Sample Data Includes:**
- 50+ code files across 3 repositories
- Basic documentation and README files
- Slack conversations about feature development
- Pull requests for new features
- Bug reports and feature requests
- Team onboarding materials

**Use Cases:**
- New developer onboarding
- Code review processes
- Feature documentation
- Bug troubleshooting
- Team communication patterns

**Demo User Roles:**
- Junior Frontend Developer
- Backend Developer
- Product Manager
- DevOps Engineer

**Sample Queries:**
- "How do I set up the development environment?"
- "What's the authentication flow in our app?"
- "How do I deploy to staging?"
- "What are the current sprint priorities?"

### 2. Enterprise Scenario

**Context:** Large enterprise corporation with 500+ developers

**Characteristics:**
- Complex microservices architecture
- Multiple development teams
- Strict compliance requirements
- Formal documentation processes
- Advanced CI/CD pipelines

**Sample Data Includes:**
- 200+ code files across 15 repositories
- Comprehensive API documentation
- Architecture decision records (ADRs)
- Security and compliance guidelines
- Team communication across multiple channels
- Complex deployment procedures
- Performance monitoring data

**Use Cases:**
- Enterprise developer onboarding
- Architecture understanding
- Compliance training
- Security best practices
- Cross-team collaboration
- Legacy system integration

**Demo User Roles:**
- Senior Software Engineer
- Technical Lead
- Solution Architect
- Security Engineer
- DevOps Specialist

**Sample Queries:**
- "What's our microservices communication pattern?"
- "How do we handle PII data in our systems?"
- "What are the deployment approval processes?"
- "How do I integrate with the user service?"

### 3. Freelancer Scenario

**Context:** Independent developer or small consultancy

**Characteristics:**
- Multiple client projects
- Solo or very small team
- Diverse technology stack
- Project-based work
- Minimal formal processes

**Sample Data Includes:**
- 30+ code files across 5 client projects
- Project-specific documentation
- Client communication records
- Time tracking and project management
- Technical decision logs
- Learning resources and tutorials

**Use Cases:**
- Project context switching
- Client requirement tracking
- Technology learning
- Best practice documentation
- Time and project management

**Demo User Roles:**
- Freelance Full-Stack Developer
- Independent Consultant
- Technical Writer
- Project Manager

**Sample Queries:**
- "What were the requirements for the e-commerce project?"
- "How did I implement authentication for Client A?"
- "What's the deployment process for the React app?"
- "What technologies am I using for each project?"

## Data Generation Process

### Document Types

Each scenario generates the following types of synthetic documents:

**Code Documents:**
- Repository README files
- Source code examples
- Configuration files
- API specifications
- Database schemas

**Documentation:**
- Setup and installation guides
- API documentation
- Architecture overviews
- Troubleshooting guides
- Best practices

**Communication:**
- Slack/Teams conversations
- Email threads
- Meeting notes
- Code review comments
- Support tickets

**Project Management:**
- User stories and requirements
- Bug reports
- Feature requests
- Sprint planning notes
- Progress updates

### Metadata Structure

Each document includes comprehensive metadata:

```json
{
  "source_type": "documentation|code|conversation|ticket",
  "file_path": "path/to/file.md",
  "repository": "repo-name",
  "language": "javascript",
  "created_at": "2024-01-15T10:30:00Z",
  "author": "developer-name",
  "tags": ["authentication", "api", "security"],
  "difficulty": "beginner|intermediate|advanced",
  "category": "setup|development|deployment"
}
```

## Scenario Customization

### Modifying Existing Scenarios

1. Edit scenario files in `demo/scenarios/`
2. Update the JSON configuration
3. Regenerate demo data

```bash
python vector_store/demo_vectorstore.py reset
python vector_store/demo_vectorstore.py populate startup
```

### Creating Custom Scenarios

1. Create new scenario JSON file
2. Define company context and data structure
3. Generate synthetic documents
4. Populate vector store collections

**Example Custom Scenario:**
```json
{
  "company": {
    "name": "MedTech Solutions",
    "industry": "Healthcare Technology",
    "size": "100-200 employees",
    "description": "HIPAA-compliant medical software"
  },
  "codebase": {
    "repositories": [
      {
        "name": "patient-portal",
        "description": "React-based patient portal",
        "technologies": ["React", "Node.js", "PostgreSQL"]
      }
    ]
  }
}
```

## Demo Data Quality

### Realism Factors

**Technical Accuracy:**
- Valid code syntax and patterns
- Realistic error messages and logs
- Authentic development workflows
- Industry-standard practices

**Contextual Consistency:**
- Cross-referenced information
- Consistent naming conventions
- Logical progression of conversations
- Realistic timeline and dependencies

**Diversity and Scale:**
- Multiple programming languages
- Various complexity levels
- Different communication styles
- Comprehensive coverage of topics

### Quality Metrics

**Coverage:**
- 90%+ of common development scenarios
- Multiple difficulty levels per topic
- Cross-functional team perspectives
- Complete development lifecycle

**Relevance:**
- Industry-specific terminology
- Current technology trends
- Real-world problem patterns
- Practical implementation examples

## Usage Guidelines

### For Sales Demos

**Startup Scenario:**
- Emphasize rapid onboarding
- Show agile development support
- Highlight informal knowledge sharing
- Demonstrate scaling capabilities

**Enterprise Scenario:**
- Focus on compliance features
- Show security and governance
- Emphasize architecture complexity
- Highlight cross-team collaboration

**Freelancer Scenario:**
- Show project management
- Emphasize context switching
- Highlight learning support
- Demonstrate efficiency gains

### For Technical Evaluation

**Development Testing:**
- Use realistic code examples
- Test with complex queries
- Validate response accuracy
- Assess performance metrics

**Integration Testing:**
- Multi-source data retrieval
- Cross-collection search
- Permission boundary testing
- Scalability assessment

### For Training

**New User Onboarding:**
- Start with startup scenario
- Progress to enterprise complexity
- Practice with various query types
- Explore different user roles

**Feature Training:**
- Scenario-specific features
- Role-based demonstrations
- Progressive complexity
- Real-world application

## Performance Characteristics

### Data Volume

| Scenario | Documents | Code Files | Conversations | Tickets |
|----------|-----------|------------|---------------|---------|
| Startup | 150+ | 50+ | 30+ | 20+ |
| Enterprise | 500+ | 200+ | 100+ | 75+ |
| Freelancer | 100+ | 30+ | 20+ | 15+ |

### Search Performance

**Response Times:**
- Simple queries: <200ms
- Complex searches: <500ms
- Multi-collection: <1s
- Full-text search: <100ms

**Accuracy Metrics:**
- Relevance score: >0.8
- Context accuracy: >90%
- Source attribution: 100%
- Response completeness: >85%

## Maintenance

### Data Refresh

**Scheduled Updates:**
- Monthly scenario review
- Quarterly data regeneration
- Annual scenario expansion
- Continuous quality monitoring

**Version Control:**
- Scenario configuration versioning
- Data generation script tracking
- Quality metric baselines
- Performance benchmarks

### Quality Assurance

**Automated Testing:**
- Data consistency validation
- Search result verification
- Performance regression testing
- Security compliance checking

**Manual Review:**
- Content quality assessment
- User experience testing
- Scenario realism evaluation
- Feature coverage analysis