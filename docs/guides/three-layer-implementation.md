# Implementation Guide: Three-Layer Architecture in Practice

**Purpose**: Concrete steps, templates, and scripts to implement the three-layer system  
**Target**: Lighthouse Labs import as proof-of-concept, then scale to all sources  

---

## PHASE 1: SETUP (Hours 1-4)

### Task 1.1: Create Core Index Pages in Logseq

Create these pages in your Logseq `pages/` folder:

**`00-Dashboard.md`** - Master entry point
```markdown
---
title:: Dashboard - Learning Compass
type:: dashboard
updated:: 2025-12-18
---

# 📍 Knowledge Management System

## Quick Access

- [[01-Lighthouse-Labs-Master-Index]] - All course content
- [[02-Topics-by-Proficiency]] - What you know
- [[03-Projects-and-Goals]] - Active work
- [[04-Chronological-Archive]] - Learning timeline
- [[05-Source-Index]] - Organized by origin

## Today's Learning

- Today: YYYY-MM-DD
- Recent additions: X items
- Topics to review: X items

---

### Find By Proficiency

{{query (page-tags #proficiency/::strength)}}

### Find Gaps

{{query (page-tags #proficiency/::gap)}}
```

**`01-Lighthouse-Labs-Master-Index.md`** - Course navigation
```markdown
---
title:: Lighthouse Labs Cybersecurity - Master Index
type:: course-master-index
source:: lighthouse-labs
courses:: [1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12]
total-weeks:: 30
total-content-items:: 600
import-date:: 2025-12-18
---

# Lighthouse Labs - Complete Index

## Navigation

- [[Course 1 - IT Essentials]] (Weeks 1-3)
- [[Course 2 - Network Fundamentals]] (Weeks 4-6)
- [[Course 3 - Network Advanced]] (Weeks 6-8)
- ... (continue for all 12 courses)

## Quick Filters

### By Week
{{query (and (page-tags #week-01))}}

### By Topic
{{query (and (page-tags #domain/cybersecurity/network-security))}}

### By Proficiency
{{query (and (page-tags #source/lighthouse-labs) (page-tags #proficiency/::competent))}}

## Statistics
- Total Pages: 600
- Topics Indexed: 120+
- Labs: 50+
- Case Studies: 8
- Capstone Projects: 1
```

**`02-Topics-by-Proficiency.md`** - Proficiency dashboard
```markdown
---
title:: Topics by Proficiency Level
type:: proficiency-dashboard
updated:: 2025-12-18
---

# Your Proficiency Landscape

## Expert (Strength - Ready to Use) ⭐⭐⭐⭐⭐

{{query (and (page-tags #proficiency/::strength))}}

## Strong (Can Apply) ⭐⭐⭐⭐

{{query (and (page-tags #proficiency/::competent))}}

## Intermediate (Learning) ⭐⭐⭐

{{query (and (page-tags #proficiency/::intermediate))}}

## Beginner (Foundational) ⭐⭐

{{query (and (page-tags #activity/learn::beginner))}}

## Gaps (Need Study) ❌

{{query (and (page-tags #proficiency/::gap))}}
```

**`03-Projects-and-Goals.md`** - Active work hub
```markdown
---
title:: Projects and Career Goals
type:: project-hub
---

# 🎯 Active Projects & Goals

## Short-Term Projects (Next 3 months)

{{query (and (page-tags #project/active))}}

## Long-Term Career Goals

{{query (and (page-tags #goal/long-term))}}

## Knowledge Supporting Current Work

{{query (and (page-tags #project/active) (page-tags #readiness/job::ready))}}
```

### Task 1.2: Document Tag Schema

In Logseq, create reference pages for each tag dimension:

**`Reference-Tags-Domain.md`**:
```markdown
---
title:: Tag Reference - Domain Tags
type:: tag-reference
---

# Domain Tags

Use to classify WHAT the content is about.

## Format
`#domain/[parent]/[child]/[specific]`

## Examples

### Cybersecurity
- `#domain/cybersecurity/network-security/firewalls`
- `#domain/cybersecurity/incident-response`
- `#domain/cybersecurity/threat-intelligence`

### Web Development
- `#domain/web-development/frontend`
- `#domain/web-development/backend`

[Continue with full taxonomy]
```

Create similar reference pages for:
- `Reference-Tags-Activity.md`
- `Reference-Tags-Proficiency.md`
- `Reference-Tags-Project.md`
- `Reference-Tags-Connection.md`
- `Reference-Tags-Readiness.md`
- `Reference-Tags-Source.md`

---

## PHASE 2: PREPARE IMPORT DATA (Hours 5-8)

### Task 2.1: Create Metadata Mapping

For Lighthouse Labs, you already have the course structure. Create a mapping file:

**`import-metadata-lighthouse-labs.csv`**:
```csv
course,week,title,file,created_date,topic_primary,topic_secondary
1,1,Virtualization Basics,001.md,2025-11-15,virtualization,infrastructure
1,1,VirtualBox Setup,002.md,2025-11-15,virtualization,tools
1,2,Linux Fundamentals,003.md,2025-11-20,linux,operating-systems
...
```

This enables automated tagging during import.

### Task 2.2: Create Import Script Template

Create a Python script that will:
1. Read each markdown file
2. Add Layer 1 metadata
3. Add Layer 2 initial tags  
4. Add Layer 3 placeholders
5. Output ready-to-import files

**`import-with-layers.py`** (simplified):
```python
#!/usr/bin/env python3
import os
import sys
from pathlib import Path
from datetime import datetime
import csv

def add_layers_to_note(md_content, metadata):
    """
    Add three layers of structure to a note
    
    Layer 1: Hierarchy + metadata
    Layer 2: Tags
    Layer 3: Placeholder connections
    """
    
    # Layer 1: Build frontmatter
    frontmatter = f"""---
title:: "{metadata['title']}"
source:: {metadata['source']}
source-path:: "{metadata['source_path']}"
hierarchy:: {metadata['hierarchy']}
created:: {metadata['created']}
created-chronological:: {metadata['created_chronological']}
course:: {metadata.get('course', 'N/A')}
week:: {metadata.get('week', 'N/A')}
depth:: {len(metadata['hierarchy'])}
type:: {metadata['type']}
updated:: {datetime.now().isoformat()}
---

"""
    
    # Layer 2: Build tags
    tags_section = "tags:: \n"
    for tag in metadata['tags']:
        tags_section += f"  - {tag}\n"
    
    # Layer 3: Build placeholder connections
    connections = """

## Related Topics (Layer 3 - Connections)

### Prerequisites
- (To be populated: What must I know first?)

### Enables Learning Of
- (To be populated: What topics does this enable?)

### Used In Projects
- (To be populated: Which active projects use this?)

### Related Concepts
- (To be populated: Similar or connected ideas)

"""
    
    # Combine all sections
    result = frontmatter + tags_section + "\n" + connections + "\n" + md_content
    
    return result

def build_metadata(row, source='lighthouse-labs'):
    """Build metadata dict from CSV row"""
    
    course = row['course']
    week = row['week']
    title = row['title']
    
    source_path = f"Course {course} > Week {week} > {row['topic_primary']}"
    hierarchy = [
        f"course-{course}",
        f"week-{week.zfill(2)}",
        row['topic_primary'].lower().replace(' ', '-'),
        row['topic_secondary'].lower().replace(' ', '-') if row['topic_secondary'] else '',
    ]
    hierarchy = [h for h in hierarchy if h]  # Remove empty strings
    
    created_date = datetime.fromisoformat(row['created_date'])
    created_week = created_date.strftime('%Y-W%W')
    
    # Build initial tags
    tags = [
        f"#source/{source}",
        f"#domain/{row['topic_primary'].lower().replace(' ', '-')}",
        "#activity/learn",
        "#proficiency/::beginner",
        "#quality/draft",
        f"#source-date/{created_week}",
    ]
    
    return {
        'title': title,
        'source': source,
        'source_path': source_path,
        'hierarchy': hierarchy,
        'created': created_date.isoformat(),
        'created_chronological': created_week,
        'course': course,
        'week': week,
        'type': 'lesson-note',
        'tags': tags,
    }

# Main execution
def main():
    # Read metadata CSV
    with open('import-metadata-lighthouse-labs.csv', 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    # Read markdown files
    input_dir = Path('logseq_notes')
    output_dir = Path('logseq_notes_layered')
    output_dir.mkdir(exist_ok=True)
    
    for row in rows:
        file_path = input_dir / row['file']
        
        if not file_path.exists():
            print(f"⚠️  File not found: {file_path}")
            continue
        
        # Read content
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Build metadata
        metadata = build_metadata(row)
        
        # Add layers
        layered_content = add_layers_to_note(content, metadata)
        
        # Output
        output_path = output_dir / row['file']
        with open(output_path, 'w') as f:
            f.write(layered_content)
        
        print(f"✅ Processed: {row['title']}")
    
    print(f"\n✅ Complete! {len(rows)} notes layered and ready for import.")
    print(f"   Output directory: {output_dir}")

if __name__ == '__main__':
    main()
```

**Usage**:
```bash
python3 import-with-layers.py
# This creates logseq_notes_layered/ with all 600 files layered with metadata and tags
```

---

## PHASE 3: IMPORT PROCESS (Hours 9-12)

### Task 3.1: Copy Layered Files to Logseq

```bash
# Backup existing pages
cp -r ~/Logseq/graph/pages ~/Logseq/graph/pages.backup.2025-12-18

# Copy layered imports
cp logseq_notes_layered/*.md ~/Logseq/graph/pages/

# If you're not using ~/Logseq/graph, replace with your actual path
```

### Task 3.2: Re-index Logseq

1. Open Logseq desktop app
2. Go to Settings (gear icon)
3. Advanced tab
4. Click "Clear all caches and re-index"
5. Wait for indexing to complete

### Task 3.3: Verify Import

Check that:
- [ ] All 600 files appear in search
- [ ] Master index page loads: `[[01-Lighthouse-Labs-Master-Index]]`
- [ ] Tags work: Try searching `#source/lighthouse-labs`
- [ ] Queries run: Check proficiency dashboard
- [ ] Navigate hierarchy: Course 1 → Week 1 → Topic

---

## PHASE 4: POPULATE LAYER 3 (Ongoing - Weeks 2-4)

### Task 4.1: Review and Link Workflow

For each topic you review/study:

**Step 1: Open the note**

**Step 2: Review connections section**
```markdown
### Prerequisites
- [ ] [[OSI Model]] - Network layers foundation
- [ ] [[Network Architecture]] - Segmentation concepts
```

**Step 3: Fill in real prerequisites**
```markdown
### Prerequisites
- ✅ [[OSI Model - Complete]] - Understand layer architecture
- ✅ [[Network Architecture Basics]] - Know why segmentation matters
```

**Step 4: Fill in "enables" section**
```markdown
### Enables Learning Of
- ✅ Enables [[VLAN Configuration]] - VLANs are segmentation implementation
- ✅ Enables [[DMZ Design]] - Segmentation in practice
```

**Step 5: Note if used in project**
```markdown
### Used In Projects
- [[Project: Homelab Network]] - Implementing segmentation design
```

**Step 6: Update proficiency tag**
```markdown
tags:: 
  - #proficiency/network-segmentation::intermediate  # Changed from beginner
  - #activity/execute  # Added - did lab
  - #project/active/homelab-network  # Added - used in real work
```

---

## PHASE 5: BUILD META-KNOWLEDGE VIEWS (Weeks 3-4)

### Create Proficiency Report Page

**`Reports-Proficiency-Summary.md`**:
```markdown
---
title:: Proficiency Report - December 2025
type:: proficiency-report
created:: 2025-12-18
---

# Your Proficiency Report

## How to Use This
Run this query monthly to track growth:

### Strength Areas (Ready to Demonstrate)

{{query 
  (and 
    (page-tags #proficiency/::strength)
    (page-tags #activity/execute)
  )
}}

**Count**: ___ topics
**Implication**: These are your marketable skills

### Developing Areas (Active Learning)

{{query 
  (and 
    (page-tags #proficiency/::intermediate)
    (page-tags #project/active)
  )
}}

**Count**: ___ topics
**Implication**: Growing skills through real projects

### Gap Areas (Priority Study)

{{query 
  (and 
    (page-tags #proficiency/::gap)
    (page-tags #goal/long-term)
  )
}}

**Count**: ___ topics
**Implication**: Critical for goals, needs focused study

## Proficiency By Domain

### Network Security
- Topics: 15
- Strength: 10 ⭐⭐⭐⭐⭐
- Intermediate: 4 ⭐⭐⭐
- Gap: 1 ❌

### Incident Response
- Topics: 12
- Strength: 8 ⭐⭐⭐⭐⭐
- Intermediate: 3 ⭐⭐⭐
- Gap: 1 ❌

[Continue for all domains]

## Job Readiness

### Security Analyst (Target Role)

#### Ready to Demonstrate
{{query 
  (and 
    (page-tags #readiness/job::security-analyst::ready)
    (page-tags #activity/execute)
  )
}}

#### In Development
{{query 
  (and 
    (page-tags #readiness/job::security-analyst)
    (page-tags #proficiency/::intermediate)
  )
}}

#### Critical Gaps
{{query 
  (and 
    (page-tags #readiness/job::security-analyst::gap)
    (page-tags #goal/short-term)
  )
}}

## Next Month Targets
- [ ] Move 2 topics from intermediate → strength
- [ ] Fill 1 critical gap
- [ ] Add 1 new domain for career goal
```

---

## PHASE 6: PROJECT-LINKED LEARNING (Week 4+)

### Create Project Hub

**`Project-Homelab-Network-Infrastructure.md`**:
```markdown
---
title:: Project: Homelab Network Infrastructure
type:: project-hub
status:: active
progress:: 0%
started:: 2025-12-18
target-completion:: 2026-01-31
related-topics:: 12
---

# 🏗️ Project: Homelab Network Infrastructure

## Project Goal
Design and implement a segmented home network with firewalls and VLANs.

## Knowledge Inventory

### 🟢 Ready to Use (Strength)
{{query 
  (and 
    (page-tags #project/homelab-network)
    (page-tags #proficiency/::strength)
  )
}}

### 🟡 Learning as I Go (Intermediate)
{{query 
  (and 
    (page-tags #project/homelab-network)
    (page-tags #proficiency/::intermediate)
  )
}}

### 🔴 Need Before Starting (Gaps)
{{query 
  (and 
    (page-tags #project/homelab-network)
    (page-tags #proficiency/::gap)
  )
}}

## Study Plan
- Week 1: Review all "🟢 Ready" topics
- Week 2-3: Complete "🟡 Learning" labs
- Week 4: Address "🔴 Gaps" with focused study
- Week 5+: Implementation

## Progress Tracking
- [ ] Complete foundational review
- [ ] Finish all labs
- [ ] Design network topology
- [ ] Purchase equipment
- [ ] Implement core infrastructure
- [ ] Test segmentation
- [ ] Document lessons learned
```

---

## QUICK START CHECKLIST

### Week 1: Foundation
- [ ] Create index pages (Task 1.1)
- [ ] Document tag schema (Task 1.2)
- [ ] Create metadata mapping (Task 2.1)
- [ ] Test import script on 10 sample notes (Task 2.2)

### Week 2: Import
- [ ] Run import script on all 600 files (Task 2.2)
- [ ] Copy to Logseq (Task 3.1)
- [ ] Re-index (Task 3.2)
- [ ] Verify 5+ queries work (Task 3.3)

### Week 3: Populate Layer 3
- [ ] Review 10 notes from each course
- [ ] Add real prerequisites and connections
- [ ] Update proficiency tags based on understanding
- [ ] Create first proficiency report

### Week 4: Build Views
- [ ] Create proficiency dashboard (Task 5)
- [ ] Create career goal page (Phase 3B)
- [ ] Create project hub (Phase 6)
- [ ] Run meta-knowledge queries

---

## EXAMPLE: Concrete Flow for Single Note

**Scenario**: You're reviewing "Firewall Configuration"

**Step 1: Find the note**
- Search: `firewall configuration` in Logseq
- Opens: `Lighthouse Labs > Course 1 > Week 3 > Firewalls > Firewall Configuration`

**Step 2: See what's there**
```markdown
---
title:: "Firewall Configuration Best Practices"
tags:: 
  - #source/lighthouse-labs
  - #domain/cybersecurity/network-security/firewalls
  - #activity/learn
  - #proficiency/::beginner
  - #quality/draft
---

## Prerequisites (Layer 3 - Placeholder)
- (To be populated: What must I know first?)

## Content
[Original course content here]
```

**Step 3: Study the content**
- Read through
- Do any associated lab
- Take notes

**Step 4: Update based on your experience**
```markdown
---
title:: "Firewall Configuration Best Practices"
tags:: 
  - #source/lighthouse-labs
  - #domain/cybersecurity/network-security/firewalls
  - #activity/learn
  - #activity/execute        # Added - did the lab
  - #proficiency/firewalls::intermediate   # Updated from beginner
  - #quality/verified        # Updated from draft
  - #project/homelab-network # Added - using for project
  - #readiness/job::security-analyst::ready # Added - job-relevant
---

## Prerequisites (Layer 3 - Populated)
- [[OSI Model]] - Understand network layers
- [[Network Fundamentals]] - Protocol basics
- [[Access Control Lists]] - Rule syntax

## Enables Learning Of
- [[Advanced Firewall Rules]] - Complex scenarios
- [[Network Segmentation]] - Applying firewalls in design
- [[DDoS Mitigation]] - Advanced use cases

## Used In Projects
- [[Project: Homelab Network Infrastructure]] - Core security component

## Proficiency Journey
- Learned: 2025-11-15
- Lab completed: 2025-11-20 (intermediate)
- Applied to project: 2025-12-10 (competent)

[Original content]
```

**Step 5: See impact**
- Run query: `#proficiency/firewalls::intermediate` → Now appears
- Run query: `#project/homelab-network` → Now lists this note as resource
- Check goal: `[[Goal: Security Analyst Role]]` → Now shows as ready skill

---

## MAINTENANCE

**Monthly**:
- [ ] Run proficiency report
- [ ] Update 5+ notes with refined proficiency tags
- [ ] Check for new project connections

**Quarterly**:
- [ ] Review all "gap" items
- [ ] Move topics from gap → intermediate → strength
- [ ] Identify new topics to add

**Annually**:
- [ ] Full proficiency audit
- [ ] Reorganize by new goals
- [ ] Build skills summary for resume/portfolio

---

## TROUBLESHOOTING

**Q: Proficiency query returns nothing**
A: Tags may be using wrong format. Check:
- Tag format: `#proficiency/topic::level`
- Level values: `novice`, `beginner`, `intermediate`, `competent`, `expert`, `gap`, `strength`

**Q: Can't find notes after import**
A: Re-index Logseq (Settings → Advanced → Re-index)

**Q: Project hub isn't showing related notes**
A: Make sure notes have `#project/projectname` tag

**Q: Queries are slow**
A: Logseq may be indexing. Wait a minute, then try again.

