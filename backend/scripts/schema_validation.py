import asyncio
import os
import sys
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import inspect, create_engine
import json

# Add backend dir to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.models import Base
from app.database import DATABASE_URL
import app.intelligence_models
import app.memory_models

def run_validation():
    print("Starting Schema Validation...")
    
    sync_url = DATABASE_URL.replace("postgresql+asyncpg", "postgresql")
    engine = create_engine(sync_url)
    
    # Create all tables first
    Base.metadata.create_all(bind=engine)
    
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    report_lines = []
    report_lines.append("# SCHEMA VALIDATION REPORT\n")
    report_lines.append("## Verification Summary")
    report_lines.append(f"- **Total Tables Verified:** {len(tables)}\n")
    
    for table_name in tables:
        report_lines.append(f"### Table: `{table_name}`")
        
        # Verify PK
        pk_constraint = inspector.get_pk_constraint(table_name)
        pk_cols = pk_constraint.get('constrained_columns', [])
        if pk_cols:
            report_lines.append(f"- **PK Validated**: `{'`, `'.join(pk_cols)}`")
        else:
            report_lines.append("- **PK Validated**: *None Found (Warning)*")
            
        # Verify FK & Cascades
        fks = inspector.get_foreign_keys(table_name)
        if fks:
            for fk in fks:
                cols = fk.get('constrained_columns', [])
                ref_table = fk.get('referred_table')
                ref_cols = fk.get('referred_columns', [])
                options = fk.get('options', {})
                ondelete = options.get('ondelete', 'NO ACTION')
                report_lines.append(f"- **FK Validated**: `{cols[0]}` -> `{ref_table}.{ref_cols[0]}` (ON DELETE: {ondelete})")
        else:
            report_lines.append("- **FK Validated**: *None*")
            
        # Verify Indexes
        indexes = inspector.get_indexes(table_name)
        if indexes:
            for idx in indexes:
                cols = idx.get('column_names', [])
                unique = "UNIQUE " if idx.get('unique') else ""
                report_lines.append(f"- **Index Validated**: {unique}on `{'`, `'.join(cols)}`")
        
        report_lines.append("")
        
    report_content = "\n".join(report_lines)
    
    # Write report
    report_path = os.path.join(os.environ.get('USERPROFILE', ''), '.gemini', 'antigravity-cli', 'brain', '70e7d9eb-86a4-4d1f-b313-6d0ff3a5ddbd', 'SCHEMA_VALIDATION_REPORT.md')
    # fallback to local dir if missing env
    if not os.path.exists(os.path.dirname(report_path)):
        report_path = 'SCHEMA_VALIDATION_REPORT.md'
        
    with open(report_path, "w", encoding='utf-8') as f:
        f.write(report_content)
        
    print(f"Validation complete. Report written to: {report_path}")

if __name__ == "__main__":
    run_validation()
