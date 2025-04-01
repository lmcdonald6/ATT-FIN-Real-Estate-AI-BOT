"""
Data Migration Tool
Imports and structures existing ATTOM data into the new storage system
"""
from typing import Dict, List, Optional
import pandas as pd
import json
import os
import logging
from datetime import datetime
from pathlib import Path
import shutil
import asyncio
from .extractors import AttomDataExtractor
from ..utils.formatter import ResponseFormatter

class DataMigrationTool:
    """Migrates existing ATTOM data to new storage structure"""
    
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.excel_dir = self.base_dir / 'excel'
        self.json_dir = self.base_dir / 'json_backup'
        self.attom_dir = self.base_dir / 'attom_data'
        self.cloud_dir = self.base_dir / 'cloud_backup'
        self.extractor = AttomDataExtractor()
        self.formatter = ResponseFormatter()
        self.logger = logging.getLogger(__name__)
        
        # Create necessary directories
        for directory in [self.excel_dir, self.json_dir, self.attom_dir, self.cloud_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    async def migrate_data(self, source_dir: str) -> Dict:
        """
        Migrate all data from source directory to new storage structure
        Returns statistics about the migration
        """
        stats = {
            'total_files': 0,
            'successful_migrations': 0,
            'failed_migrations': 0,
            'data_types': {}
        }
        
        try:
            source_path = Path(source_dir)
            if not source_path.exists():
                raise FileNotFoundError(f"Source directory {source_dir} not found")
            
            # Process all JSON files in source directory
            for file_path in source_path.rglob('*.json'):
                stats['total_files'] += 1
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                    
                    # Determine data type and extract accordingly
                    data_type = self._determine_data_type(data)
                    if data_type:
                        stats['data_types'][data_type] = stats['data_types'].get(data_type, 0) + 1
                        await self._process_data(data, data_type)
                        stats['successful_migrations'] += 1
                    else:
                        self.logger.warning(f"Could not determine data type for {file_path}")
                        stats['failed_migrations'] += 1
                
                except Exception as e:
                    self.logger.error(f"Error migrating {file_path}: {str(e)}")
                    stats['failed_migrations'] += 1
            
            return stats
        
        except Exception as e:
            self.logger.error(f"Migration failed: {str(e)}")
            raise
    
    def _determine_data_type(self, data: Dict) -> Optional[str]:
        """Determine the type of ATTOM data"""
        if 'property' in data:
            return 'property_details'
        elif 'assessment' in data:
            return 'tax_assessment'
        elif 'value' in data:
            return 'valuation'
        elif 'owner' in data:
            return 'owner_info'
        elif 'market' in data:
            return 'market_data'
        elif 'foreclosure' in data:
            return 'foreclosure'
        elif 'deed' in data:
            return 'deed'
        elif 'mls' in data:
            return 'mls'
        return None
    
    async def _process_data(self, data: Dict, data_type: str) -> None:
        """Process and store data based on its type"""
        try:
            # Extract structured data
            extracted_data = self._extract_data(data, data_type)
            
            # Store in various formats
            await asyncio.gather(
                self._store_json(extracted_data, data_type),
                self._store_excel(extracted_data, data_type),
                self._store_cloud(extracted_data, data_type)
            )
            
        except Exception as e:
            self.logger.error(f"Error processing {data_type} data: {str(e)}")
            raise
    
    def _extract_data(self, data: Dict, data_type: str) -> Dict:
        """Extract data using appropriate extractor"""
        extraction_methods = {
            'property_details': self.extractor.extract_property_details,
            'tax_assessment': self.extractor.extract_tax_assessment,
            'valuation': self.extractor.extract_valuation,
            'owner_info': self.extractor.extract_owner_info,
            'market_data': self.extractor.extract_market_data,
            'foreclosure': self.extractor.extract_foreclosure,
            'deed': self.extractor.extract_deed,
            'mls': self.extractor.extract_mls
        }
        
        extractor = extraction_methods.get(data_type)
        if not extractor:
            raise ValueError(f"No extractor found for data type: {data_type}")
        
        return extractor(data)
    
    async def _store_json(self, data: Dict, data_type: str) -> None:
        """Store data as JSON backup"""
        try:
            file_path = self.json_dir / f"{data_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error storing JSON backup: {str(e)}")
            raise
    
    async def _store_excel(self, data: Dict, data_type: str) -> None:
        """Store data in structured Excel format"""
        try:
            file_path = self.excel_dir / f"{data_type}.xlsx"
            
            # Convert nested dict to flat structure for Excel
            flat_data = self._flatten_dict(data)
            df = pd.DataFrame([flat_data])
            
            # Append to existing file or create new one
            if file_path.exists():
                existing_df = pd.read_excel(file_path)
                df = pd.concat([existing_df, df], ignore_index=True)
            
            df.to_excel(file_path, index=False)
            
        except Exception as e:
            self.logger.error(f"Error storing Excel data: {str(e)}")
            raise
    
    async def _store_cloud(self, data: Dict, data_type: str) -> None:
        """Store data in cloud backup"""
        try:
            file_path = self.cloud_dir / f"{data_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error storing cloud backup: {str(e)}")
            raise
    
    def _flatten_dict(self, d: Dict, parent_key: str = '', sep: str = '_') -> Dict:
        """Flatten nested dictionary for Excel storage"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                # Convert list to string representation
                items.append((new_key, str(v)))
            else:
                items.append((new_key, v))
        
        return dict(items)
    
    async def verify_migration(self, stats: Dict) -> bool:
        """Verify migration success and data integrity"""
        try:
            # Check if all directories were created
            directories = [self.excel_dir, self.json_dir, self.attom_dir, self.cloud_dir]
            if not all(d.exists() for d in directories):
                return False
            
            # Check if files were created for each data type
            for data_type in stats['data_types']:
                excel_file = self.excel_dir / f"{data_type}.xlsx"
                if not excel_file.exists():
                    return False
            
            # Check success rate
            success_rate = stats['successful_migrations'] / stats['total_files']
            return success_rate >= 0.95  # 95% success rate threshold
            
        except Exception as e:
            self.logger.error(f"Error verifying migration: {str(e)}")
            return False
