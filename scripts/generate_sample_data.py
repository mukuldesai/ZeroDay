import os
import sys
import json
import random
from pathlib import Path
from datetime import datetime, timedelta
from faker import Faker
from loguru import logger
from dotenv import load_dotenv
load_dotenv()

sys.path.append(str(Path(__file__).parent.parent))

from vector_store.index_builder import IndexBuilder

fake = Faker()

def generate_code_documents(count=50):
    logger.info(f"Generating {count} code documents...")
    
    documents = []
    
    languages = ["python", "javascript", "typescript", "java", "go"]
    frameworks = ["react", "express", "django", "spring", "fastapi"]
    
    code_templates = {
        "python": """
def {function_name}({params}):
    '''
    {description}
    '''
    {implementation}
    return result

if __name__ == "__main__":
    {usage_example}
""",
        "javascript": """
function {function_name}({params}) {{
    // {description}
    {implementation}
    return result;
}}

module.exports = {{ {function_name} }};
""",
        "typescript": """
interface {interface_name} {{
    {properties}
}}

export function {function_name}({params}): {return_type} {{
    // {description}
    {implementation}
    return result;
}}
"""
    }
    
    for i in range(count):
        language = random.choice(languages)
        framework = random.choice(frameworks)
        
        function_name = fake.word() + "_" + fake.word()
        description = fake.sentence()
        
        if language == "python":
            params = "data, options=None"
            implementation = "    result = process_data(data)\n    if options:\n        result = apply_options(result, options)"
            usage_example = f"    result = {function_name}(sample_data)"
            
            content = code_templates["python"].format(
                function_name=function_name,
                params=params,
                description=description,
                implementation=implementation,
                usage_example=usage_example
            )
            
        elif language in ["javascript", "typescript"]:
            params = "data, options"
            implementation = "    const result = processData(data);\n    return applyOptions(result, options);"
            
            if language == "typescript":
                interface_name = fake.word().capitalize() + "Data"
                properties = "id: string;\n    name: string;\n    value: number;"
                return_type = "Promise<ProcessedData>"
                
                content = code_templates["typescript"].format(
                    interface_name=interface_name,
                    properties=properties,
                    function_name=function_name,
                    params=params,
                    return_type=return_type,
                    description=description,
                    implementation=implementation
                )
            else:
                content = code_templates["javascript"].format(
                    function_name=function_name,
                    params=params,
                    description=description,
                    implementation=implementation
                )
        
        repository = fake.word() + "-" + fake.word()
        file_path = f"src/{fake.word()}/{function_name}.{language}"
        
        documents.append({
            "content": content.strip(),
            "metadata": {
                "source_type": "code",
                "file_path": file_path,
                "repository": repository,
                "language": language,
                "framework": framework,
                "created_at": fake.date_time_between(start_date='-1y', end_date='now').isoformat(),
                "author": fake.name(),
                "tags": [language, framework, "function"],
                "lines_of_code": len(content.split('\n')),
                "complexity": random.choice(["low", "medium", "high"])
            }
        })
    
    logger.success(f"Generated {len(documents)} code documents")
    return documents

def generate_documentation_documents(count=30):
    logger.info(f"Generating {count} documentation documents...")
    
    documents = []
    
    doc_types = ["setup", "api", "tutorial", "troubleshooting", "reference"]
    categories = ["getting-started", "development", "deployment", "maintenance"]
    
    for i in range(count):
        doc_type = random.choice(doc_types)
        category = random.choice(categories)
        
        title = fake.catch_phrase()
        
        if doc_type == "setup":
            content = f"""
# {title}

## Prerequisites
- {fake.word().capitalize()} {fake.random_int(1, 20)}+
- {fake.word().capitalize()} {fake.random_int(1, 10)}.{fake.random_int(0, 9)}
- Basic knowledge of {fake.word()}

## Installation

1. Install dependencies:
   ```bash
   npm install {fake.word()}-{fake.word()}
   ```

2. Configure environment:
   ```bash
   cp .env.example .env
   ```

3. Start the application:
   ```bash
   npm start
   ```

## Verification

Run the following command to verify installation:
```bash
{fake.word()} --version
```

## Troubleshooting

If you encounter issues, check:
- {fake.sentence()}
- {fake.sentence()}
- {fake.sentence()}
"""
        
        elif doc_type == "api":
            endpoint = fake.word()
            method = random.choice(["GET", "POST", "PUT", "DELETE"])
            
            content = f"""
# {title}

## Endpoint
`{method} /api/{endpoint}`

## Description
{fake.paragraph()}

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| {fake.word()} | string | Yes | {fake.sentence()} |
| {fake.word()} | number | No | {fake.sentence()} |
| {fake.word()} | boolean | No | {fake.sentence()} |

## Example Request

```json
{{
  "{fake.word()}": "{fake.word()}",
  "{fake.word()}": {fake.random_int(1, 100)},
  "{fake.word()}": {random.choice(['true', 'false'])}
}}
```

## Example Response

```json
{{
  "success": true,
  "data": {{
    "id": "{fake.uuid4()}",
    "status": "{fake.word()}"
  }}
}}
```

## Error Codes

- 400: {fake.sentence()}
- 404: {fake.sentence()}
- 500: {fake.sentence()}
"""
        
        elif doc_type == "tutorial":
            content = f"""
# {title}

## Overview
{fake.paragraph()}

## What You'll Learn
- {fake.sentence()}
- {fake.sentence()}
- {fake.sentence()}

## Step 1: {fake.catch_phrase()}
{fake.paragraph()}

```bash
{fake.word()} {fake.word()} --{fake.word()}={fake.word()}
```

## Step 2: {fake.catch_phrase()}
{fake.paragraph()}

```javascript
const {fake.word()} = require('{fake.word()}');

{fake.word()}.{fake.word()}({{
  {fake.word()}: '{fake.word()}',
  {fake.word()}: {fake.random_int(1, 100)}
}});
```

## Step 3: {fake.catch_phrase()}
{fake.paragraph()}

## Next Steps
- {fake.sentence()}
- {fake.sentence()}
- Read the {fake.word()} documentation
"""
        
        else:
            content = f"""
# {title}

## Overview
{fake.paragraph()}

## Details
{fake.paragraph()}

{fake.paragraph()}

## Examples
{fake.paragraph()}

## Best Practices
- {fake.sentence()}
- {fake.sentence()}
- {fake.sentence()}

## Related Topics
- {fake.word().capitalize()}
- {fake.word().capitalize()}
- {fake.word().capitalize()}
"""
        
        file_path = f"docs/{category}/{fake.word()}-{fake.word()}.md"
        
        documents.append({
            "content": content.strip(),
            "metadata": {
                "source_type": "documentation",
                "file_path": file_path,
                "doc_type": doc_type,
                "category": category,
                "title": title,
                "created_at": fake.date_time_between(start_date='-1y', end_date='now').isoformat(),
                "author": fake.name(),
                "tags": [doc_type, category, "documentation"],
                "difficulty": random.choice(["beginner", "intermediate", "advanced"]),
                "estimated_read_time": random.randint(2, 15)
            }
        })
    
    logger.success(f"Generated {len(documents)} documentation documents")
    return documents

def generate_conversation_documents(count=25):
    logger.info(f"Generating {count} conversation documents...")
    
    documents = []
    
    channels = ["general", "development", "design", "product", "support"]
    users = [fake.user_name() for _ in range(10)]
    
    for i in range(count):
        channel = random.choice(channels)
        participants = random.sample(users, random.randint(2, 5))
        
        conversation_length = random.randint(5, 20)
        messages = []
        
        for j in range(conversation_length):
            user = random.choice(participants)
            
            if channel == "development":
                message_templates = [
                    "I'm working on the {feature} implementation",
                    "Found a bug in the {component} module",
                    "Can someone review PR #{number}?",
                    "The {service} deployment is complete",
                    "Need help with {technology} integration"
                ]
                message = random.choice(message_templates).format(
                    feature=fake.word(),
                    component=fake.word(),
                    number=fake.random_int(1, 200),
                    service=fake.word(),
                    technology=fake.word()
                )
            elif channel == "support":
                message_templates = [
                    "User reported issue with {feature}",
                    "Fixed the {problem} in production",
                    "Monitoring shows {metric} is elevated",
                    "Created ticket {ticket_id} for tracking",
                    "Customer feedback: {feedback}"
                ]
                message = random.choice(message_templates).format(
                    feature=fake.word(),
                    problem=fake.word(),
                    metric=fake.word(),
                    ticket_id=fake.bothify("SUP-####"),
                    feedback=fake.sentence()
                )
            else:
                message = fake.sentence()
            
            timestamp = fake.date_time_between(start_date='-30d', end_date='now')
            messages.append(f"[{timestamp.strftime('%H:%M')}] {user}: {message}")
        
        content = f"Channel: #{channel}\nDate: {fake.date()}\n\n" + "\n".join(messages)
        
        documents.append({
            "content": content,
            "metadata": {
                "source_type": "conversation",
                "channel": channel,
                "participants": participants,
                "message_count": len(messages),
                "date": fake.date().isoformat(),
                "created_at": fake.date_time_between(start_date='-30d', end_date='now').isoformat(),
                "tags": ["slack", "conversation", channel],
                "thread_type": random.choice(["discussion", "announcement", "question", "update"])
            }
        })
    
    logger.success(f"Generated {len(documents)} conversation documents")
    return documents

def generate_ticket_documents(count=20):
    logger.info(f"Generating {count} ticket documents...")
    
    documents = []
    
    ticket_types = ["bug", "feature", "improvement", "task"]
    priorities = ["low", "medium", "high", "critical"]
    statuses = ["open", "in-progress", "review", "closed"]
    
    for i in range(count):
        ticket_type = random.choice(ticket_types)
        priority = random.choice(priorities)
        status = random.choice(statuses)
        
        ticket_id = fake.bothify("ZD-####")
        title = fake.catch_phrase()
        reporter = fake.name()
        assignee = fake.name() if random.choice([True, False]) else "Unassigned"
        
        if ticket_type == "bug":
            content = f"""
**Ticket ID:** {ticket_id}
**Type:** Bug Report
**Priority:** {priority.upper()}
**Status:** {status.upper()}
**Reporter:** {reporter}
**Assignee:** {assignee}

## Summary
{title}

## Description
{fake.paragraph()}

## Steps to Reproduce
1. {fake.sentence()}
2. {fake.sentence()}
3. {fake.sentence()}

## Expected Behavior
{fake.sentence()}

## Actual Behavior
{fake.sentence()}

## Environment
- Browser: {random.choice(['Chrome', 'Firefox', 'Safari', 'Edge'])}
- OS: {random.choice(['Windows 10', 'macOS', 'Ubuntu 20.04'])}
- Version: {fake.random_int(1, 10)}.{fake.random_int(0, 9)}.{fake.random_int(0, 9)}

## Additional Notes
{fake.paragraph()}
"""
        
        elif ticket_type == "feature":
            content = f"""
**Ticket ID:** {ticket_id}
**Type:** Feature Request
**Priority:** {priority.upper()}
**Status:** {status.upper()}
**Reporter:** {reporter}
**Assignee:** {assignee}

## Summary
{title}

## User Story
As a {fake.job()}, I want to {fake.sentence().lower()} so that I can {fake.sentence().lower()}

## Description
{fake.paragraph()}

## Acceptance Criteria
- [ ] {fake.sentence()}
- [ ] {fake.sentence()}
- [ ] {fake.sentence()}

## Design Mockups
See attached designs in {fake.word()}-{fake.word()}.figma

## Technical Notes
{fake.paragraph()}

## Business Value
{fake.paragraph()}
"""
        
        else:
            content = f"""
**Ticket ID:** {ticket_id}
**Type:** {ticket_type.capitalize()}
**Priority:** {priority.upper()}
**Status:** {status.upper()}
**Reporter:** {reporter}
**Assignee:** {assignee}

## Summary
{title}

## Description
{fake.paragraph()}

## Requirements
- {fake.sentence()}
- {fake.sentence()}
- {fake.sentence()}

## Success Criteria
{fake.sentence()}

## Timeline
Estimated: {fake.random_int(1, 10)} days

## Dependencies
{fake.sentence()}
"""
        
        documents.append({
            "content": content.strip(),
            "metadata": {
                "source_type": "ticket",
                "ticket_id": ticket_id,
                "type": ticket_type,
                "priority": priority,
                "status": status,
                "reporter": reporter,
                "assignee": assignee,
                "title": title,
                "created_at": fake.date_time_between(start_date='-6m', end_date='now').isoformat(),
                "tags": [ticket_type, priority, status],
                "component": fake.word(),
                "estimated_hours": random.randint(1, 40) if ticket_type != "bug" else None
            }
        })
    
    logger.success(f"Generated {len(documents)} ticket documents")
    return documents

def generate_pull_request_documents(count=15):
    logger.info(f"Generating {count} pull request documents...")
    
    documents = []
    
    for i in range(count):
        pr_number = fake.random_int(1, 500)
        title = fake.catch_phrase()
        author = fake.name()
        repository = fake.word() + "-" + fake.word()
        
        content = f"""
# Pull Request #{pr_number}: {title}

**Author:** {author}
**Repository:** {repository}
**Status:** {random.choice(['open', 'merged', 'closed'])}
**Branch:** feature/{fake.word()}-{fake.word()}
**Target:** main

## Description
{fake.paragraph()}

## Changes Made
- {fake.sentence()}
- {fake.sentence()}
- {fake.sentence()}

## Files Modified
- `src/{fake.word()}/{fake.word()}.py`
- `tests/test_{fake.word()}.py`
- `docs/{fake.word()}.md`
- `package.json`

## Testing
- [x] Unit tests pass
- [x] Integration tests pass
- [x] Manual testing completed
- [ ] Performance testing

## Screenshots
![Before and after comparison]({fake.word()}-{fake.word()}.png)

## Review Notes
{fake.paragraph()}

## Breaking Changes
{random.choice(['None', fake.sentence()])}

## Checklist
- [x] Code follows style guidelines
- [x] Tests added/updated
- [x] Documentation updated
- [x] No merge conflicts
"""
        
        documents.append({
            "content": content.strip(),
            "metadata": {
                "source_type": "pull_request",
                "pr_number": pr_number,
                "title": title,
                "author": author,
                "repository": repository,
                "status": random.choice(['open', 'merged', 'closed']),
                "created_at": fake.date_time_between(start_date='-3m', end_date='now').isoformat(),
                "tags": ["pull-request", "code-review"],
                "files_changed": random.randint(1, 10),
                "lines_added": random.randint(10, 500),
                "lines_deleted": random.randint(0, 200)
            }
        })
    
    logger.success(f"Generated {len(documents)} pull request documents")
    return documents

def save_sample_data(documents, filename):
    logger.info(f"Saving sample data to {filename}...")
    
    sample_data_dir = Path("demo/sample_data")
    sample_data_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = sample_data_dir / filename
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(documents, f, indent=2, default=str)
    
    logger.success(f"Saved {len(documents)} documents to {output_file}")

def index_sample_data(documents, collection_type):
    logger.info(f"Indexing {len(documents)} documents to {collection_type} collection...")
    
    indexer = IndexBuilder(user_id="demo_user", org_id="demo_org")
    
    result = indexer.add_documents(documents, collection_type)
    
    if result.get("success"):
        logger.success(f"Indexed {result.get('chunks_created')} chunks to {collection_type}")
        return True
    else:
        logger.error(f"Failed to index documents: {result.get('error')}")
        return False

def generate_all_sample_data():
    logger.info("Generating comprehensive sample data...")
    
    document_generators = [
        ("code", generate_code_documents, 50),
        ("documentation", generate_documentation_documents, 30),
        ("conversations", generate_conversation_documents, 25),
        ("tickets", generate_ticket_documents, 20),
        ("pull_requests", generate_pull_request_documents, 15)
    ]
    
    all_results = {}
    
    for collection_type, generator_func, count in document_generators:
        logger.info(f"Generating {collection_type} data...")
        
        documents = generator_func(count)
        
        save_sample_data(documents, f"{collection_type}_sample_data.json")
        
        if index_sample_data(documents, collection_type):
            all_results[collection_type] = {
                "success": True,
                "document_count": len(documents)
            }
        else:
            all_results[collection_type] = {
                "success": False,
                "document_count": 0
            }
    
    return all_results

def print_generation_summary(results):
    total_documents = sum(r.get("document_count", 0) for r in results.values())
    successful_collections = sum(1 for r in results.values() if r.get("success"))
    
    print("\n" + "="*60)
    print(" Sample Data Generation Complete!")
    print("="*60)
    print(f"\nTotal Documents Generated: {total_documents}")
    print(f"Collections Populated: {successful_collections}/{len(results)}")
    print("\nBreakdown by Collection:")
    
    for collection, result in results.items():
        status =  if result.get("success") else 
        count = result.get("document_count", 0)
        print(f"  {status} {collection.capitalize()}: {count} documents")
    
    print(f"\n Sample data files saved to: demo/sample_data/")
    print(" Data indexed and ready for search")
    print("\nNext Steps:")
    print("  1. Test search functionality")
    print("  2. Verify data quality")
    print("  3. Add custom data as needed")
    print("="*60)

def main():
    logger.info("Starting sample data generation...")
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "code":
            documents = generate_code_documents()
            save_sample_data(documents, "code_sample_data.json")
            index_sample_data(documents, "code")
        elif command == "docs":
            documents = generate_documentation_documents()
            save_sample_data(documents, "documentation_sample_data.json")
            index_sample_data(documents, "documentation")
        elif command == "conversations":
            documents = generate_conversation_documents()
            save_sample_data(documents, "conversations_sample_data.json")
            index_sample_data(documents, "slack_messages")
        elif command == "tickets":
            documents = generate_ticket_documents()
            save_sample_data(documents, "tickets_sample_data.json")
            index_sample_data(documents, "tickets")
        elif command == "prs":
            documents = generate_pull_request_documents()
            save_sample_data(documents, "pull_requests_sample_data.json")
            index_sample_data(documents, "pull_requests")
        else:
            logger.error(f"Unknown command: {command}")
            print("Available commands: code, docs, conversations, tickets, prs")
            sys.exit(1)
    else:
        results = generate_all_sample_data()
        print_generation_summary(results)

if __name__ == "__main__":
    main()