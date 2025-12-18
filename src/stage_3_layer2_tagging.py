#!/usr/bin/env python3
"""
Stage 3: Semantic Tagging & Layer 2 Population

Tasks:
- 3.1: Extract content keywords
- 3.2: Map keywords to tags  
- 3.3: Validate and apply tags
"""

import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
import pandas as pd
import json
import logging
from collections import Counter

logger = logging.getLogger(__name__)


# Task 3.1: Extract Keywords
# =========================================================================

class KeywordExtractor:
    """Extract keywords and infer domain from content."""
    
    def __init__(self, domain_db: str = None, tech_terms_db: str = None):
        """Initialize with optional databases."""
        self.domains = {}
        self.technical_terms = set()
        
        if tech_terms_db and Path(tech_terms_db).exists():
            with open(tech_terms_db, 'r') as f:
                data = json.load(f)
                self.technical_terms = set(data.get('terms', []))
        
        if domain_db and Path(domain_db).exists():
            with open(domain_db, 'r') as f:
                self.domains = json.load(f)
    
    def extract_from_content(self, content: str) -> Dict:
        """
        Extract keywords from file content.
        
        Returns:
            Dict with keywords, domain, topics, and confidence
        """
        # Skip frontmatter
        if content.startswith('---'):
            end_marker = content.find('\n---\n')
            if end_marker != -1:
                content = content[end_marker + 5:]
        
        # Extract title (usually first heading)
        title = None
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if title_match:
            title = title_match.group(1)
        
        # Extract first paragraph
        first_para = None
        para_match = re.search(r'\n\n(.+?)(?:\n\n|\n#)', content, re.DOTALL)
        if para_match:
            first_para = para_match.group(1)[:200]
        
        # Extract all headings
        headings = re.findall(r'^#{1,3}\s+(.+)$', content, re.MULTILINE)
        
        # Find technical terms mentioned
        mentioned_terms = []
        for term in self.technical_terms:
            if term.lower() in content.lower():
                mentioned_terms.append(term)
        
        # Extract key concepts (words appearing multiple times)
        words = re.findall(r'\b[a-z][a-z\-]+\b', content.lower())
        word_counts = Counter(words)
        
        # Filter out common words
        common_words = {'the', 'and', 'or', 'is', 'a', 'an', 'to', 'of', 'in', 'for', 'with', 'on', 'at', 'by'}
        key_concepts = [
            word for word, count in word_counts.most_common(15)
            if count >= 2 and word not in common_words and len(word) > 3
        ]
        
        return {
            'title': title or 'Untitled',
            'keywords': key_concepts[:10],
            'technical_terms': mentioned_terms,
            'headings': headings,
            'first_para': first_para or '',
        }


def extract_keywords(source_dir: Path, domain_db: str = None, 
                    tech_terms_db: str = None, output_dir: Path = None) -> Dict:
    """
    Extract keywords from all files.
    
    Args:
        source_dir: Directory with markdown files
        domain_db: Path to domain database
        tech_terms_db: Path to technical terms database
        output_dir: Output directory for results
    
    Returns:
        Dictionary with extraction statistics
    """
    logger.info("Extracting keywords from content...")
    
    extractor = KeywordExtractor(domain_db, tech_terms_db)
    
    keywords_list = []
    files_processed = 0
    
    for md_file in source_dir.glob("*.md"):
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            extracted = extractor.extract_from_content(content)
            extracted['file_name'] = md_file.name
            keywords_list.append(extracted)
            files_processed += 1
            
        except Exception as e:
            logger.warning(f"Error extracting keywords from {md_file.name}: {str(e)}")
    
    # Save results
    if output_dir:
        df = pd.DataFrame(keywords_list)
        # Convert lists to strings for CSV
        for col in ['keywords', 'technical_terms', 'headings']:
            df[col] = df[col].apply(lambda x: '; '.join(x) if isinstance(x, list) else x)
        
        df.to_csv(output_dir / "content-keywords.csv", index=False)
    
    logger.info(f"Keywords extracted from {files_processed} files")
    
    return {
        'files_processed': files_processed,
        'keywords_extracted': len(keywords_list)
    }


# Task 3.2: Map Keywords to Tags
# =========================================================================

class TagMapper:
    """Map keywords to multi-dimensional tags."""
    
    def __init__(self, tag_schema: str = None, source_mappings: Dict = None):
        """Initialize with tag schema."""
        self.tag_schema = {}
        self.source_mappings = source_mappings or {}
        
        if tag_schema and Path(tag_schema).exists():
            with open(tag_schema, 'r') as f:
                self.tag_schema = json.load(f)
    
    def map_to_domain_tags(self, keywords: List[str], title: str, 
                           source_type: str = None) -> List[str]:
        """Map keywords to domain tags."""
        tags = []
        
        # Check source-specific mappings first
        if source_type and source_type in self.source_mappings:
            mapping = self.source_mappings[source_type]
            # Try to match title or keywords against mapping
            for key_pattern, tag_value in mapping.items():
                if key_pattern.lower() in title.lower():
                    tags.append(tag_value)
                    break
        
        # Default domain inference
        domain_keywords = {
            'cybersecurity': ['security', 'network', 'firewall', 'encryption', 'attack', 'threat'],
            'networking': ['network', 'router', 'protocol', 'tcp', 'ip', 'dns'],
            'systems': ['system', 'server', 'os', 'linux', 'windows', 'admin'],
            'development': ['code', 'program', 'api', 'database', 'app', 'script'],
            'virtualization': ['virtual', 'hypervisor', 'vm', 'container', 'docker'],
        }
        
        primary_domain = None
        max_matches = 0
        
        for domain, keywords_list in domain_keywords.items():
            matches = sum(1 for kw in keywords if kw.lower() in title.lower() 
                         or any(dk in kw.lower() for dk in keywords_list))
            if matches > max_matches:
                max_matches = matches
                primary_domain = domain
        
        if primary_domain:
            tags.append(f"#domain/{primary_domain}")
        
        return tags
    
    def map_to_activity_tags(self, title: str, content_length: int) -> List[str]:
        """Infer activity tags from content."""
        tags = []
        
        # Heuristics for activity type
        if any(word in title.lower() for word in ['tutorial', 'guide', 'intro', 'learn', 'course']):
            tags.append("#activity/learn::beginner")
        elif any(word in title.lower() for word in ['lab', 'hands-on', 'exercise', 'practice']):
            tags.append("#activity/execute::hands-on")
        elif any(word in title.lower() for word in ['reference', 'glossary', 'definition']):
            tags.append("#activity/reference")
        else:
            tags.append("#activity/learn::intermediate")
        
        return tags
    
    def map_to_proficiency_tags(self, keywords: List[str]) -> List[str]:
        """
        Create proficiency tags (all start as beginner on import).
        
        Returns:
            List with single proficiency tag
        """
        # On import, everything is beginner - user updates over time
        return ["#proficiency/topic::beginner"]
    
    def map_to_source_tags(self, source_type: str) -> List[str]:
        """Create source tags."""
        source_tag = f"#source/{source_type}"
        tags = [source_tag, "#quality/unverified"]
        return tags
    
    def map_keywords_to_all_tags(self, keywords: Dict, source_type: str = None) -> Dict:
        """
        Map keywords to all 8 tag dimensions.
        
        Returns:
            Dictionary with tags for each dimension
        """
        all_tags = {}
        
        # Extract components
        title = keywords.get('title', '')
        keyword_list = keywords.get('keywords', [])
        content_length = len(keywords.get('first_para', ''))
        
        # Domain tags
        all_tags['domain_tags'] = self.map_to_domain_tags(keyword_list, title, source_type)
        
        # Activity tags
        all_tags['activity_tags'] = self.map_to_activity_tags(title, content_length)
        
        # Proficiency tags
        all_tags['proficiency_tags'] = self.map_to_proficiency_tags(keyword_list)
        
        # Project tags (will be empty initially, populated by user)
        all_tags['project_tags'] = []
        
        # Goal tags (will be empty initially)
        all_tags['goal_tags'] = []
        
        # Connection tags (placeholders for Layer 3)
        all_tags['connection_tags'] = ["#prerequisite-for/", "#enables/", "#connects-to/"]
        
        # Readiness tags (will be empty initially)
        all_tags['readiness_tags'] = []
        
        # Source tags
        all_tags['source_tags'] = self.map_to_source_tags(source_type or 'unknown')
        
        return all_tags


def map_keywords_to_tags(source_dir: Path, keywords_file: Path, 
                        source_type: str, tag_schema: str = None,
                        source_mappings: Dict = None, output_dir: Path = None) -> Dict:
    """
    Map keywords to tags for all files.
    
    Args:
        source_dir: Directory with markdown files
        keywords_file: CSV file with extracted keywords
        source_type: Type of source (for source tags)
        tag_schema: Path to tag schema JSON
        source_mappings: Dictionary of source-specific mappings
        output_dir: Output directory for results
    
    Returns:
        Dictionary with tagging statistics
    """
    logger.info("Mapping keywords to tags...")
    
    mapper = TagMapper(tag_schema, source_mappings)
    
    # Load keywords
    keywords_df = pd.read_csv(keywords_file)
    
    all_tags_list = []
    files_processed = 0
    
    for _, row in keywords_df.iterrows():
        try:
            keywords_dict = {
                'title': row['title'],
                'keywords': row['keywords'].split('; ') if pd.notna(row['keywords']) else [],
                'first_para': row['first_para'] if pd.notna(row['first_para']) else '',
            }
            
            tags_dict = mapper.map_keywords_to_all_tags(keywords_dict, source_type)
            tags_dict['file_name'] = row['file_name']
            all_tags_list.append(tags_dict)
            files_processed += 1
            
        except Exception as e:
            logger.warning(f"Error mapping tags for {row['file_name']}: {str(e)}")
    
    # Save results
    if output_dir:
        df = pd.DataFrame(all_tags_list)
        # Convert lists to strings for CSV
        for col in df.columns:
            if col != 'file_name':
                df[col] = df[col].apply(lambda x: '; '.join(x) if isinstance(x, list) else x)
        
        df.to_csv(output_dir / "tags-mapped.csv", index=False)
    
    logger.info(f"Tags mapped for {files_processed} files")
    
    return {
        'files_processed': files_processed,
        'tags_mapped': len(all_tags_list)
    }


# Task 3.3: Validate & Apply Tags
# =========================================================================

def validate_tag_format(tag: str) -> Tuple[bool, str]:
    """
    Validate a single tag format.
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not tag.startswith('#'):
        return False, "Tag must start with #"
    
    # Remove # for further validation
    tag_content = tag[1:]
    
    # Check for valid characters
    if not re.match(r'^[a-z0-9/_\-:]+$', tag_content):
        return False, "Tag contains invalid characters"
    
    # If it has a level (::), validate it
    if '::' in tag:
        parts = tag_content.split('::')
        if len(parts) != 2:
            return False, "Invalid level specification (should be tag::level)"
        
        valid_levels = ['novice', 'beginner', 'intermediate', 'competent', 'expert', 'gap', 'strength', 'ready']
        if parts[1] not in valid_levels:
            return False, f"Invalid level: {parts[1]}"
    
    return True, ""


def apply_tags_to_file(file_path: Path, tags_dict: Dict) -> bool:
    """
    Add Layer 2 tags section to file.
    
    Args:
        file_path: Path to markdown file
        tags_dict: Dictionary with all tags
    
    Returns:
        True if successful
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find where to insert tags (after frontmatter, before content)
        if content.startswith('---'):
            end_marker = content.find('\n---\n')
            if end_marker != -1:
                frontmatter_end = end_marker + 5
                before_content = content[:frontmatter_end]
                main_content = content[frontmatter_end:]
            else:
                before_content = ''
                main_content = content
        else:
            before_content = ''
            main_content = content
        
        # Build tags section
        tags_section = "## Tags\n\n"
        
        # Collect all tags
        all_tags = []
        for key, tags in tags_dict.items():
            if key != 'file_name' and isinstance(tags, str):
                all_tags.extend([t.strip() for t in tags.split(';') if t.strip()])
        
        # Remove duplicates and placeholders
        all_tags = list(set([t for t in all_tags if t and '/' in t]))
        
        tags_section += " ".join(sorted(all_tags)) + "\n\n"
        
        # Combine and save
        new_content = before_content + tags_section + main_content
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return True
        
    except Exception as e:
        logger.error(f"Error applying tags to {file_path}: {str(e)}")
        return False


def validate_tags(source_dir: Path, tags_file: Path, tag_schema: str = None,
                 output_dir: Path = None) -> Dict:
    """
    Validate and apply tags to all files.
    
    Args:
        source_dir: Directory with markdown files
        tags_file: CSV file with tags to apply
        tag_schema: Path to tag schema for validation
        output_dir: Output directory for results
    
    Returns:
        Dictionary with validation statistics
    """
    logger.info("Validating and applying tags...")
    
    tags_df = pd.read_csv(tags_file)
    
    validation_results = []
    files_checked = 0
    files_passed = 0
    
    for _, row in tags_df.iterrows():
        file_path = source_dir / row['file_name']
        files_checked += 1
        
        issues = []
        
        # Collect all tags from row
        all_tags = []
        for col in tags_df.columns:
            if col != 'file_name' and pd.notna(row[col]):
                tags_list = [t.strip() for t in str(row[col]).split(';')]
                all_tags.extend(tags_list)
        
        # Validate each tag
        for tag in all_tags:
            if tag:
                is_valid, error = validate_tag_format(tag)
                if not is_valid:
                    issues.append(f"{tag}: {error}")
        
        if not issues:
            # Apply tags to file
            if apply_tags_to_file(file_path, row.to_dict()):
                files_passed += 1
                validation_results.append({
                    'file': row['file_name'],
                    'status': 'PASS',
                    'tags_count': len([t for t in all_tags if t]),
                    'issues': None
                })
            else:
                validation_results.append({
                    'file': row['file_name'],
                    'status': 'FAIL',
                    'tags_count': len(all_tags),
                    'issues': 'Failed to apply tags'
                })
        else:
            validation_results.append({
                'file': row['file_name'],
                'status': 'FAIL',
                'tags_count': len(all_tags),
                'issues': '; '.join(issues[:3])
            })
    
    # Save results
    if output_dir:
        pd.DataFrame(validation_results).to_csv(
            output_dir / "tags-validation-results.csv", index=False
        )
    
    logger.info(f"Tag validation: {files_passed}/{files_checked} passed")
    
    return {
        'files_checked': files_checked,
        'files_passed': files_passed,
        'files_failed': files_checked - files_passed
    }


if __name__ == '__main__':
    # For testing
    test_dir = Path('./test_files')
    output = Path('./stage_3_output')
    output.mkdir(exist_ok=True)
    
    # Extract keywords
    keywords_result = extract_keywords(test_dir, None, None, output)
    print(f"Keywords extracted: {keywords_result}")
