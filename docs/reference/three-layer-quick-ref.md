# Quick Reference: Three-Layer Logseq System

**Print this or keep in Logseq for quick lookup**

---

## THE THREE LAYERS AT A GLANCE

### 🏛️ LAYER 1: Hierarchy + Metadata
**Preserves structure. Enables "where does this come from?"**

```
Frontmatter includes:
- source: lighthouse-labs, perplexity, vscode, etc
- source-path: "Course 1 > Week 3 > Topic"
- hierarchy: [course-1, week-03, topic-name]
- created: 2025-11-15
- created-chronological: 2025-W46
- course, week, depth: numeric values for sorting
```

**Ask**: "Can I trace this back to its original course?"  
**Success**: Yes, easily navigate Course → Week → Topic

---

### 🏷️ LAYER 2: Semantic Tags  
**Describes content from multiple angles. Enables "what do I know and where am I weak?"**

#### Tag Dimensions

| Dimension | Examples | Purpose |
|-----------|----------|---------|
| **Domain** | `#domain/cybersecurity/firewalls` | What is this about? |
| **Activity** | `#activity/execute`, `#activity/learn::beginner` | What can I do with it? |
| **Proficiency** | `#proficiency/firewalls::intermediate` | Where am I with this? |
| **Project** | `#project/active/homelab-network` | What work uses this? |
| **Goal** | `#goal/short-term/security-plus-exam` | How does it serve me? |
| **Connection** | `#connects-to/vpn-config`, `#prerequisite-for/incident-response` | How is it related? |
| **Readiness** | `#readiness/job::security-analyst::ready` | Can I use it professionally? |
| **Source** | `#source/lighthouse-labs`, `#quality/verified` | Where from? Quality? |

#### Proficiency Levels

- `#proficiency/topic::novice` - Just heard of it
- `#proficiency/topic::beginner` - Just started learning  
- `#proficiency/topic::intermediate` - Can apply, still learning
- `#proficiency/topic::competent` - Can do independently
- `#proficiency/topic::expert` - Can teach others
- `#proficiency/topic::gap` - Known gap, needs study
- `#proficiency/topic::strength` - Core competency

**Ask**: "What am I expert in vs what do I need to study?"  
**Success**: Run query, get proficiency heatmap

---

### 🔗 LAYER 3: Dynamic Linking
**Connects topics to your learning journey. Enables "how does this serve my goals?"**

#### Link Types

| Link Type | Purpose | Example |
|-----------|---------|---------|
| **Prerequisite** | What must I learn first | [[OSI Model]] ← foundation for [[Firewall Config]] |
| **Enables** | What topics does this unlock | [[Firewall Config]] → enables [[Network Segmentation]] |
| **Project** | What active work uses this | [[Project: Homelab]] uses [[Firewall Config]] |
| **Goal** | What career target uses this | [[Security Analyst Role]] requires [[Firewall Config]] |
| **Related** | Similar or alternative | [[Firewall]] ~= [[IPS/IDS]] |
| **Enriches** | Deepens understanding of | [[Case Study: Breach]] enriches [[Threat Modeling]] |

**Ask**: "How does this connect to my projects and goals?"  
**Success**: Click through related concepts, see how knowledge serves your work

---

## QUICK QUERIES

Copy and paste these into Logseq query blocks:

### Find Your Strengths
```clojure
{{query (and (page-tags #proficiency/::strength) (page-tags #activity/execute))}}
```
*Returns: What you're expert in and ready to use*

### Find Your Gaps
```clojure
{{query (and (page-tags #proficiency/::gap) (page-tags #goal/long-term))}}
```
*Returns: Critical things you need to learn for your goals*

### What's Job-Ready
```clojure
{{query (and (page-tags #readiness/job::security-analyst::ready) (page-tags #activity/execute))}}
```
*Returns: Skills you can demonstrate on resume*

### Find by Domain
```clojure
{{query (and (page-tags #domain/cybersecurity) (page-tags #proficiency/::competent))}}
```
*Returns: Everything in a domain you're competent with*

### This Week's Learning
```clojure
{{query (block-content "created-chronological" "2025-W50")}}
```
*Returns: What you learned this week (change W50 to current week)*

### Active Project Resources
```clojure
{{query (and (page-tags #project/active/homelab-network) (page-tags #activity/execute))}}
```
*Returns: What ready-to-use knowledge your projects need (change project name)*

---

## IMPORT CHECKLIST

### Before Import
- [ ] Organize files with metadata
- [ ] Prepare metadata CSV/mapping
- [ ] Create index pages (Dashboard, Course Index, etc.)
- [ ] Test import script on sample (10 files)

### During Import
- [ ] Run import script: `python3 import-with-layers.py`
- [ ] Copy files to Logseq pages/
- [ ] Re-index Logseq (Settings → Advanced)

### After Import
- [ ] Verify search finds content
- [ ] Test 3+ queries work
- [ ] Check hierarchy navigable
- [ ] Confirm tags applied

### Next: Populate Layer 3
- [ ] Review 5 notes
- [ ] Add real prerequisites
- [ ] Add real "enables"
- [ ] Update proficiency based on understanding
- [ ] Mark used in projects

---

## TAG TEMPLATE

Use this template when tagging a note:

```markdown
---
# Layer 1: Metadata
source:: lighthouse-labs
course:: 1
week:: 3
created:: 2025-11-15

# Layer 2: Tags
tags::
  # What is it?
  - #domain/cybersecurity/network-security
  
  # What can I do with it?
  - #activity/learn
  - #activity/execute
  
  # Where am I?
  - #proficiency/networking::intermediate
  
  # What project?
  - #project/active/homelab
  
  # What goal?
  - #goal/short-term/security-plus
  
  # How ready?
  - #readiness/job::security-analyst::ready
  
  # Quality?
  - #source/lighthouse-labs/compass
  - #quality/verified
---
```

---

## PROFICIENCY LEVELS: QUICK GUIDE

| Level | I Can... | Ready for... | Next Step |
|-------|----------|--------------|-----------|
| **Novice** ⭐ | ...recognize it | Nothing yet | Study fundamentals |
| **Beginner** ⭐⭐ | ...explain basics | Learning activities | Do labs |
| **Intermediate** ⭐⭐⭐ | ...apply with help | Side projects | Real-world practice |
| **Competent** ⭐⭐⭐⭐ | ...do independently | Job tasks | Teach others |
| **Expert** ⭐⭐⭐⭐⭐ | ...teach others | Interviews, leadership | Innovate |
| **Gap** ❌ | ...almost nothing | Nothing | High-priority study |

---

## EXAMPLE: ONE NOTE, FULLY LAYERED

**Title**: "Firewall Configuration Lab"

### Layer 1 (Hierarchy + Metadata)
```
source: lighthouse-labs
source-path: "Course 1 > Week 3 > Network Security"
course: 1
week: 3
created: 2025-11-15
```
✅ Can trace back to original source

### Layer 2 (Tags)
```
#domain/cybersecurity/network-security/firewalls
#activity/execute
#proficiency/firewalls::intermediate
#project/active/homelab-network
#goal/short-term/security-plus-exam
#readiness/job::security-analyst::ready
#quality/verified
```
✅ Can describe what I know and how it serves me

### Layer 3 (Links)
```
Prerequisites: [[OSI Model]], [[Network Fundamentals]]
Enables: [[Advanced Firewall Rules]], [[DDoS Mitigation]]
Used In: [[Project: Homelab Network]]
Career Goal: [[Security Analyst Role]]
```
✅ Can see how this connects to my journey

---

## IMPLEMENTATION PHASES

### Phase 1: Setup (4 hours)
1. Create index pages
2. Document tag schema
3. Test on sample notes

### Phase 2: Import (4 hours)
1. Run import script
2. Copy to Logseq
3. Re-index and verify

### Phase 3: Layer 3 Populate (Ongoing, 30 min/day)
1. Review note
2. Add real prerequisites/enables
3. Update proficiency tag
4. Mark project connections

### Phase 4: Meta-Knowledge Views (4 hours)
1. Create proficiency dashboard
2. Create project hubs
3. Create career goal pages
4. Build skill tree

---

## WHAT SUCCESS LOOKS LIKE

✅ **Layer 1**: You can navigate from any note back to "Course X, Week Y, Topic Z"

✅ **Layer 2**: You run a query and see exactly:
   - What you're expert in (10 topics)
   - What you're developing (25 topics)
   - What's a critical gap (5 topics)

✅ **Layer 3**: You click on your active project and see:
   - All knowledge you're ready to use (green)
   - Knowledge you're developing (yellow)
   - Knowledge gaps you need first (red)

✅ **Meta-Knowledge**: You can answer:
   - "What am I really good at?" → Shows your strengths
   - "What do I need for my next job?" → Shows readiness
   - "How is my learning progressing?" → Shows growth timeline
   - "How does concept X connect to concept Y?" → Shows relationships

---

## MAINTENANCE ROUTINE

### Daily
- Study a note, update its proficiency tag
- Use notes in projects, mark with project tag

### Weekly
- Review 5 notes, populate Layer 3 connections
- Run proficiency query, note any patterns

### Monthly
- Create proficiency report
- Update 10+ tags based on progress

### Quarterly
- Review all "gap" items
- Move topics from gap → intermediate → strength
- Identify new topics for goals

---

## COMMON QUERIES TO SAVE

Create these as permanent query blocks in Logseq:

**Block 1: My Strengths**
```clojure
{{query (and (page-tags #proficiency/::strength) (page-tags #activity/execute))}}
```

**Block 2: My Gaps (Priority)**
```clojure
{{query (and (page-tags #proficiency/::gap) (page-tags #goal/long-term))}}
```

**Block 3: Job-Ready Skills**
```clojure
{{query (and (page-tags #readiness/job::security-analyst::ready) (page-tags #activity/execute))}}
```

**Block 4: Learning This Month**
```clojure
{{query (and (block-content "created-chronological" "2025-12") (page-tags #activity/learn))}}
```

**Block 5: Active Project Knowledge**
```clojure
{{query (and (page-tags #project/active) (page-tags #proficiency/::competent))}}
```

---

## EMERGENCY REFERENCE

**"I need to find X quickly"**
- X by topic? Search domain tag: `#domain/topic-name`
- X I can use? Search: `#activity/execute`
- X for my job? Search: `#readiness/job::role::ready`
- X I learned recently? Filter by week: `created-chronological`
- X for current project? Go to project hub, check green section

**"I'm overwhelmed, where to start?"**
1. Go to Dashboard
2. Check "Gaps (Priority)" query
3. Pick one gap
4. Click prerequisites
5. Study those first

**"Show me proficiency progress"**
1. Open proficiency dashboard
2. Look at counts: Expert / Strong / Intermediate / Gap
3. Compare to last month

**"What's my next career step?"**
1. Go to Career Goal page
2. Check readiness heatmap
3. Find red items (critical gaps)
4. Create focused study plan

---

## FILE LOCATIONS

These documents are in `/home/violetf/Games2/Nextcloud/Documents/Notes/`:

- `THREE-LAYER-LOGSEQ-ARCHITECTURE.md` - Full specification
- `IMPLEMENTATION-GUIDE-THREE-LAYER.md` - Step-by-step walkthrough
- `ORGANIZATION-STRATEGY.md` - Original planning document
- `PRIOR-WORK-SUMMARY.md` - What's already been done
- `LOGSEQ_IMPORT_GUIDE.md` - Lighthouse Labs import details
- `tag-schema.md` - Tag reference

---

## REMEMBER

This system works because it does THREE things:

1. 🏛️ **Preserves hierarchy** - Know where knowledge comes from
2. 🏷️ **Tracks proficiency** - Know what you know and what you don't
3. 🔗 **Connects to goals** - Know how knowledge serves your journey

The result is a **personal learning compass** that helps you navigate growth, not just a note repository.

