# src/rag_system.py
"""
Vendor RAG System - Single Database

Author: US Bank AI Security Team
Date: January 2025
"""

import json
import shutil
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path


class VendorRAG:
    """RAG system with single vendor database"""
    
    def __init__(self, db_path: str = "data/vendors.json"):
        """Initialize RAG system"""
        self.db_path = Path(db_path)
        self.vendors = []
        self.activity_log = []
        self.search_log = []
    
    
    def load_vendors(self) -> bool:
        """Load vendors from JSON file"""
        try:
            with open(self.db_path, 'r') as f:
                data = json.load(f)
            
            self.vendors = data['vendors']
            print(f"✅ Loaded {len(self.vendors)} vendors")
            
            # Check for duplicates
            names = [v['name'] for v in self.vendors]
            duplicates = [n for n in set(names) if names.count(n) > 1]
            
            if duplicates:
                print(f"⚠️  Duplicate vendors: {duplicates}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

    def add_vendor(self, vendor_data: Dict) -> bool:
        """Add vendor to database (simulates attack)"""
        try:
            # Add to memory
            self.vendors.append(vendor_data)
            
            # Save to file
            with open(self.db_path, 'w') as f:
                json.dump({'vendors': self.vendors}, f, indent=2)
            
            print(f"✅ Added vendor: {vendor_data['name']}")
            return True
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

    def search(self, query: str, n_results: int = 3) -> Dict:
        """Search vendors using keyword matching"""
        
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        results = []
        search_details = []  # For telemetry
        
        for vendor in self.vendors:
            # Create searchable text
            searchable = f"{vendor['name']} {vendor.get('notes', '')}"
            searchable_lower = searchable.lower()
            
            # Calculate score
            score = 0.0
            score_breakdown = {}
            
            # Rule 1: Name match (+10)
            if query_lower in vendor['name'].lower():
                score += 10.0
                score_breakdown['name_match'] = 10.0
            
            # Rule 2: Word matches (+1 each)
            word_score = 0
            for word in query_words:
                if word in searchable_lower:
                    word_score += 1.0
            score += word_score
            score_breakdown['word_matches'] = word_score
            
            # Rule 3: Full phrase (+5)
            if query_lower in searchable_lower:
                score += 5.0
                score_breakdown['phrase_match'] = 5.0
            
            # Rule 4: Question format (+3)
            notes = vendor.get('notes', '').lower()
            if '?' in notes and any(w in notes for w in query_words):
                score += 3.0
                score_breakdown['question_format'] = 3.0
            
            # Rule 5: Word frequency (+0.5 per occurrence)
            freq_score = 0
            for word in query_words:
                count = searchable_lower.count(word)
                freq_score += count * 0.5
            score += freq_score
            score_breakdown['word_frequency'] = freq_score
            
            if score > 0:
                results.append({
                    "vendor_id": vendor['vendor_id'],
                    "similarity": min(score / 50.0, 1.0),
                    "raw_score": score,
                    "score_breakdown": score_breakdown,
                    "metadata": vendor
                })
                
                search_details.append({
                    "vendor": vendor['name'],
                    "score": score,
                    "breakdown": score_breakdown
                })
        
        # Sort by score
        results.sort(key=lambda x: x['similarity'], reverse=True)
        results = results[:n_results]
        
        # Log search for telemetry
        self.search_log.append({
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "results_count": len(results),
            "top_result": results[0]['metadata']['name'] if results else None,
            "all_scores": search_details
        })
        
        return {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "results": results,
            "search_details": search_details
        }

    def get_vendor_by_id(self, vendor_id: str) -> Optional[Dict]:
        """Get vendor by ID"""
        for vendor in self.vendors:
            if vendor['vendor_id'] == vendor_id:
                return vendor
        return None
    
    
    def get_all_vendors(self) -> List[Dict]:
        """Get all vendors"""
        return self.vendors
    
    
    def get_search_log(self) -> List[Dict]:
        """Get search history for telemetry"""
        return self.search_log