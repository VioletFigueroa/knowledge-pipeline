#!/usr/bin/env python3
"""
Orchestration script for batch import pipeline.

Coordinates all 5 stages of the import process:
1. Markdown Quality Assurance
2. Metadata Extraction & Layer 1 Population
3. Semantic Tagging & Layer 2 Population
4. Layer 3 Placeholder Generation
5. Validation & Quality Checks

Usage:
    python3 orchestrate_import.py \
        --source-dir /path/to/source \
        --source-type lighthouse_labs \
        --batch-id lighthouse-labs-batch-1 \
        --output-dir /path/to/output \
        --config config.json
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from datetime import datetime

# Import stage modules
from stage_1_quality_assurance import (
    identify_files,
    lint_markdown,
    normalize_spelling,
    extract_existing_metadata
)
from stage_2_layer1_metadata import (
    map_file_to_hierarchy,
    build_layer1_frontmatter,
    validate_layer1
)
from stage_3_layer2_tagging import (
    extract_keywords,
    map_keywords_to_tags,
    validate_tags
)
from stage_4_layer3_placeholders import (
    detect_layer3_connections,
    build_layer3_placeholders,
    validate_layer3
)
from stage_5_validation import (
    validate_file_integrity,
    validate_batch_consistency,
    analyze_tag_coverage,
    generate_import_report
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('import_orchestration.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ImportOrchestrator:
    """Orchestrates the complete batch import pipeline."""
    
    def __init__(self, source_dir, source_type, batch_id, output_dir, config_path):
        """Initialize orchestrator with configuration."""
        self.source_dir = Path(source_dir)
        self.source_type = source_type
        self.batch_id = batch_id
        self.output_dir = Path(output_dir)
        self.config = self._load_config(config_path)
        self.import_date = datetime.now().isoformat()
        self.stage_outputs = {}
        
        # Create output directories
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / "stage_1_qa").mkdir(parents=True, exist_ok=True)
        (self.output_dir / "stage_2_layer1").mkdir(parents=True, exist_ok=True)
        (self.output_dir / "stage_3_layer2").mkdir(parents=True, exist_ok=True)
        (self.output_dir / "stage_4_layer3").mkdir(parents=True, exist_ok=True)
        (self.output_dir / "stage_5_validation").mkdir(parents=True, exist_ok=True)
        (self.output_dir / "processed_batch_files").mkdir(parents=True, exist_ok=True)
        (self.output_dir / "manual_review").mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Orchestrator initialized: batch_id={batch_id}, source_type={source_type}")
    
    def _load_config(self, config_path):
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {config_path}")
            sys.exit(1)
    
    def run_stage_1_qa(self):
        """
        Stage 1: Markdown Quality Assurance.
        
        Tasks:
        - 1.1: Identify all source files
        - 1.2: Lint markdown formatting
        - 1.3: Normalize spelling & grammar
        - 1.4: Extract existing metadata
        """
        logger.info("=" * 80)
        logger.info("STAGE 1: MARKDOWN QUALITY ASSURANCE")
        logger.info("=" * 80)
        
        try:
            # Task 1.1: Identify files
            logger.info("Task 1.1: Identifying source files...")
            manifest_df = identify_files(
                self.source_dir,
                output_dir=self.output_dir / "stage_1_qa"
            )
            logger.info(f"Found {len(manifest_df)} files")
            self.stage_outputs['manifest'] = manifest_df
            
            # Task 1.2: Lint markdown
            logger.info("Task 1.2: Linting markdown...")
            linting_results = lint_markdown(
                self.source_dir,
                output_dir=self.output_dir / "stage_1_qa"
            )
            logger.info(f"Linting complete: {linting_results['files_checked']} files")
            
            # Task 1.3: Normalize spelling
            logger.info("Task 1.3: Normalizing spelling and grammar...")
            spelling_results = normalize_spelling(
                self.source_dir,
                custom_dict=self.config.get('custom_dictionary'),
                output_dir=self.output_dir / "stage_1_qa"
            )
            logger.info(f"Spelling check complete: {spelling_results['issues_found']} issues")
            
            # Task 1.4: Extract metadata
            logger.info("Task 1.4: Extracting existing metadata...")
            metadata_df = extract_existing_metadata(
                self.source_dir,
                output_dir=self.output_dir / "stage_1_qa"
            )
            logger.info(f"Metadata extracted from {len(metadata_df)} files")
            self.stage_outputs['existing_metadata'] = metadata_df
            
            logger.info("✅ Stage 1 complete")
            return True
            
        except Exception as e:
            logger.error(f"❌ Stage 1 failed: {str(e)}")
            return False
    
    def run_stage_2_layer1(self):
        """
        Stage 2: Metadata Extraction & Layer 1 Population.
        
        Tasks:
        - 2.1: Map file to source hierarchy
        - 2.2: Build Layer 1 frontmatter
        - 2.3: Validate Layer 1 integrity
        """
        logger.info("=" * 80)
        logger.info("STAGE 2: METADATA EXTRACTION & LAYER 1 POPULATION")
        logger.info("=" * 80)
        
        try:
            manifest_df = self.stage_outputs.get('manifest')
            if manifest_df is None:
                logger.error("Manifest not found. Run Stage 1 first.")
                return False
            
            # Task 2.1: Map hierarchy
            logger.info("Task 2.1: Mapping files to source hierarchy...")
            hierarchy_df = map_file_to_hierarchy(
                manifest_df,
                source_type=self.source_type,
                output_dir=self.output_dir / "stage_2_layer1"
            )
            logger.info(f"Hierarchy mapped for {len(hierarchy_df)} files")
            self.stage_outputs['hierarchy'] = hierarchy_df
            
            # Task 2.2: Build Layer 1
            logger.info("Task 2.2: Building Layer 1 frontmatter...")
            layer1_results = build_layer1_frontmatter(
                self.source_dir,
                hierarchy_df=hierarchy_df,
                batch_id=self.batch_id,
                import_date=self.import_date,
                output_dir=self.output_dir / "stage_2_layer1"
            )
            logger.info(f"Layer 1 frontmatter applied to {layer1_results['files_processed']} files")
            
            # Task 2.3: Validate Layer 1
            logger.info("Task 2.3: Validating Layer 1 integrity...")
            validation_results = validate_layer1(
                self.output_dir / "stage_2_layer1",
                output_dir=self.output_dir / "stage_2_layer1"
            )
            logger.info(f"Validation complete: {validation_results['files_passed']}/{validation_results['files_checked']} passed")
            self.stage_outputs['layer1_validation'] = validation_results
            
            logger.info("✅ Stage 2 complete")
            return True
            
        except Exception as e:
            logger.error(f"❌ Stage 2 failed: {str(e)}")
            return False
    
    def run_stage_3_layer2(self):
        """
        Stage 3: Semantic Tagging & Layer 2 Population.
        
        Tasks:
        - 3.1: Extract content keywords
        - 3.2: Map keywords to tags
        - 3.3: Validate and apply tags
        """
        logger.info("=" * 80)
        logger.info("STAGE 3: SEMANTIC TAGGING & LAYER 2 POPULATION")
        logger.info("=" * 80)
        
        try:
            # Task 3.1: Extract keywords
            logger.info("Task 3.1: Extracting content keywords...")
            keywords_results = extract_keywords(
                self.output_dir / "stage_2_layer1",
                domain_db=self.config.get('domain_database'),
                tech_terms_db=self.config.get('technical_terms_db'),
                output_dir=self.output_dir / "stage_3_layer2"
            )
            logger.info(f"Keywords extracted for {keywords_results['files_processed']} files")
            
            # Task 3.2: Map to tags
            logger.info("Task 3.2: Mapping keywords to tags...")
            tagging_results = map_keywords_to_tags(
                self.output_dir / "stage_2_layer1",
                keywords_file=self.output_dir / "stage_3_layer2" / "content-keywords.csv",
                source_type=self.source_type,
                tag_schema=self.config.get('tag_schema'),
                source_mappings=self.config.get('domain_mappings'),
                output_dir=self.output_dir / "stage_3_layer2"
            )
            logger.info(f"Tags mapped for {tagging_results['files_processed']} files")
            self.stage_outputs['tagging'] = tagging_results
            
            # Task 3.3: Validate tags
            logger.info("Task 3.3: Validating and applying tags...")
            tag_validation = validate_tags(
                self.output_dir / "stage_2_layer1",
                tags_file=self.output_dir / "stage_3_layer2" / "tags-mapped.csv",
                tag_schema=self.config.get('tag_schema'),
                output_dir=self.output_dir / "stage_3_layer2"
            )
            logger.info(f"Tag validation complete: {tag_validation['files_passed']}/{tag_validation['files_checked']} passed")
            
            logger.info("✅ Stage 3 complete")
            return True
            
        except Exception as e:
            logger.error(f"❌ Stage 3 failed: {str(e)}")
            return False
    
    def run_stage_4_layer3(self):
        """
        Stage 4: Layer 3 Placeholder Generation.
        
        Tasks:
        - 4.1: Detect potential connections
        - 4.2: Build placeholder sections
        - 4.3: Validate structure
        """
        logger.info("=" * 80)
        logger.info("STAGE 4: LAYER 3 PLACEHOLDER GENERATION")
        logger.info("=" * 80)
        
        try:
            # Task 4.1: Detect connections
            logger.info("Task 4.1: Detecting potential Layer 3 connections...")
            connection_results = detect_layer3_connections(
                self.output_dir / "stage_3_layer2",
                graph_structure=self.config.get('graph_structure'),
                output_dir=self.output_dir / "stage_4_layer3"
            )
            logger.info(f"Connection detection complete: {connection_results['connections_found']} candidates")
            self.stage_outputs['connections'] = connection_results
            
            # Task 4.2: Build placeholders
            logger.info("Task 4.2: Building Layer 3 placeholder sections...")
            placeholder_results = build_layer3_placeholders(
                self.output_dir / "stage_3_layer2",
                candidates_file=self.output_dir / "stage_4_layer3" / "layer3-candidates.csv",
                output_dir=self.output_dir / "stage_4_layer3"
            )
            logger.info(f"Layer 3 placeholders created for {placeholder_results['files_processed']} files")
            
            # Task 4.3: Validate structure
            logger.info("Task 4.3: Validating Layer 3 structure...")
            layer3_validation = validate_layer3(
                self.output_dir / "stage_4_layer3",
                output_dir=self.output_dir / "stage_4_layer3"
            )
            logger.info(f"Layer 3 validation complete: {layer3_validation['files_passed']}/{layer3_validation['files_checked']} passed")
            
            logger.info("✅ Stage 4 complete")
            return True
            
        except Exception as e:
            logger.error(f"❌ Stage 4 failed: {str(e)}")
            return False
    
    def run_stage_5_validation(self):
        """
        Stage 5: Validation & Quality Checks.
        
        Tasks:
        - 5.1: File integrity validation
        - 5.2: Cross-file consistency check
        - 5.3: Tag coverage analysis
        - 5.4: Generate final report
        """
        logger.info("=" * 80)
        logger.info("STAGE 5: VALIDATION & QUALITY CHECKS")
        logger.info("=" * 80)
        
        try:
            # Task 5.1: Integrity validation
            logger.info("Task 5.1: Running file integrity validation...")
            integrity_results = validate_file_integrity(
                self.output_dir / "stage_4_layer3",
                output_dir=self.output_dir / "stage_5_validation"
            )
            logger.info(f"Integrity validation: {integrity_results['files_passed']}/{integrity_results['files_checked']} passed")
            
            # Task 5.2: Consistency check
            logger.info("Task 5.2: Running cross-file consistency check...")
            consistency_results = validate_batch_consistency(
                self.output_dir / "stage_4_layer3",
                output_dir=self.output_dir / "stage_5_validation"
            )
            logger.info(f"Consistency check: {consistency_results['checks_passed']}/{consistency_results['checks_total']} passed")
            
            # Task 5.3: Tag coverage analysis
            logger.info("Task 5.3: Analyzing tag coverage...")
            coverage_results = analyze_tag_coverage(
                self.output_dir / "stage_4_layer3",
                output_dir=self.output_dir / "stage_5_validation"
            )
            logger.info(f"Tag coverage analysis complete")
            
            # Task 5.4: Generate report
            logger.info("Task 5.4: Generating import report...")
            report_path = generate_import_report(
                batch_id=self.batch_id,
                source_type=self.source_type,
                import_date=self.import_date,
                integrity_results=integrity_results,
                consistency_results=consistency_results,
                coverage_results=coverage_results,
                stage_outputs=self.stage_outputs,
                output_dir=self.output_dir / "stage_5_validation"
            )
            logger.info(f"Import report generated: {report_path}")
            
            logger.info("✅ Stage 5 complete")
            return True
            
        except Exception as e:
            logger.error(f"❌ Stage 5 failed: {str(e)}")
            return False
    
    def finalize(self):
        """Copy processed files to final output directory."""
        logger.info("=" * 80)
        logger.info("FINALIZING: Copying processed files to deployment directory")
        logger.info("=" * 80)
        
        try:
            import shutil
            
            source = self.output_dir / "stage_4_layer3"
            dest = self.output_dir / "processed_batch_files"
            
            for md_file in source.glob("*.md"):
                if md_file.is_file():
                    shutil.copy2(md_file, dest / md_file.name)
            
            logger.info(f"✅ Processed files copied to {dest}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Finalization failed: {str(e)}")
            return False
    
    def run(self):
        """Execute the complete import pipeline."""
        logger.info(f"\n{'=' * 80}")
        logger.info(f"BATCH IMPORT PIPELINE STARTED")
        logger.info(f"Batch ID: {self.batch_id}")
        logger.info(f"Source Type: {self.source_type}")
        logger.info(f"Source Directory: {self.source_dir}")
        logger.info(f"Output Directory: {self.output_dir}")
        logger.info(f"{'=' * 80}\n")
        
        stages = [
            ("Stage 1: QA", self.run_stage_1_qa),
            ("Stage 2: Layer 1", self.run_stage_2_layer1),
            ("Stage 3: Layer 2", self.run_stage_3_layer2),
            ("Stage 4: Layer 3", self.run_stage_4_layer3),
            ("Stage 5: Validation", self.run_stage_5_validation),
            ("Finalization", self.finalize),
        ]
        
        results = {}
        for stage_name, stage_func in stages:
            success = stage_func()
            results[stage_name] = "✅ PASS" if success else "❌ FAIL"
            
            if not success:
                logger.error(f"\n❌ Pipeline stopped at {stage_name}")
                logger.error("Review logs and error files in output directory")
                break
        
        # Print final summary
        logger.info(f"\n{'=' * 80}")
        logger.info("PIPELINE SUMMARY")
        logger.info(f"{'=' * 80}")
        for stage_name, result in results.items():
            logger.info(f"{stage_name}: {result}")
        logger.info(f"{'=' * 80}\n")
        
        all_passed = all("✅" in result for result in results.values())
        if all_passed:
            logger.info("✅ IMPORT BATCH READY FOR DEPLOYMENT")
            logger.info(f"See: {self.output_dir / 'stage_5_validation' / 'import-batch-report.md'}")
        
        return all_passed


def main():
    """Parse arguments and run orchestrator."""
    parser = argparse.ArgumentParser(
        description='Orchestrate batch note import with three-layer Logseq structure'
    )
    parser.add_argument('--source-dir', required=True, help='Source directory with markdown files')
    parser.add_argument('--source-type', required=True, 
                       choices=['lighthouse_labs', 'perplexity', 'vs_code_notes', 'journals', 'other'],
                       help='Type of source material')
    parser.add_argument('--batch-id', required=True, help='Unique batch identifier')
    parser.add_argument('--output-dir', required=True, help='Output directory for processed files')
    parser.add_argument('--config', default='config.json', help='Configuration file path')
    
    args = parser.parse_args()
    
    orchestrator = ImportOrchestrator(
        source_dir=args.source_dir,
        source_type=args.source_type,
        batch_id=args.batch_id,
        output_dir=args.output_dir,
        config_path=args.config
    )
    
    success = orchestrator.run()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
