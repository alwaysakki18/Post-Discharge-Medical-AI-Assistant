"""
Script to initialize and populate the database.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.database.database import get_db_manager
from backend.utils.logger import system_logger


def main():
    """Initialize database and load patient data."""
    try:
        print("=" * 60)
        print("Post Discharge Medical AI Assistant - Database Setup")
        print("=" * 60)
        print()
        
        # Initialize database manager
        print("📊 Initializing database...")
        db_manager = get_db_manager()
        print("✅ Database initialized")
        print()
        
        # Load patient data
        print("👥 Loading patient data...")
        patient_file = Path(__file__).parent.parent / "data" / "patient_reports.json"
        
        if not patient_file.exists():
            print(f"❌ Error: Patient data file not found: {patient_file}")
            return
        
        db_manager.load_patient_data(str(patient_file))
        print("✅ Patient data loaded")
        print()
        
        # Verify data
        patients = db_manager.get_all_patients()
        print(f"📈 Database Statistics:")
        print(f"   - Total patients: {len(patients)}")
        print()
        
        # Show sample patients
        print("📋 Sample Patients:")
        for i, patient in enumerate(patients[:5], 1):
            print(f"   {i}. {patient['patient_name']} - {patient['primary_diagnosis']}")
        
        if len(patients) > 5:
            print(f"   ... and {len(patients) - 5} more")
        
        print()
        print("=" * 60)
        print("✅ Database setup complete!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error during database setup: {str(e)}")
        system_logger.log_error("DatabaseSetupError", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
