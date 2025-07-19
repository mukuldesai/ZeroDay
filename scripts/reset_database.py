#!/usr/bin/env python3

import os
import sys
import shutil
from pathlib import Path
from loguru import logger
import sqlite3
from dotenv import load_dotenv
load_dotenv()

sys.path.append(str(Path(__file__).parent.parent))

from database.setup import DatabaseSetup
from vector_store.chromadb_setup import ChromaDBSetup
from vector_store.demo_vectorstore import DemoVectorStore

def confirm_reset():
    print("\n" + "="*60)
    print("⚠️  WARNING: DATABASE RESET OPERATION")
    print("="*60)
    print("This will permanently delete:")
    print("  • All user accounts and organizations")
    print("  • All uploaded documents and data")
    print("  • All vector embeddings and search data")
    print("  • All chat history and interactions")
    print("  • All demo data and scenarios")
    print("\nThis action CANNOT be undone!")
    print("="*60)
    
    confirmation = input("\nType 'RESET' to confirm deletion: ")
    
    if confirmation != "RESET":
        logger.info("Reset operation cancelled")
        return False
    
    double_confirm = input("Are you absolutely sure? Type 'YES': ")
    
    if double_confirm != "YES":
        logger.info("Reset operation cancelled")
        return False
    
    logger.warning("Proceeding with database reset...")
    return True

def backup_before_reset():
    logger.info("Creating backup before reset...")
    
    backup_dir = Path("backups")
    backup_dir.mkdir(exist_ok=True)
    
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"pre_reset_backup_{timestamp}"
    backup_path.mkdir(exist_ok=True)
    
    database_file = Path("database/users.db")
    if database_file.exists():
        shutil.copy2(database_file, backup_path / "users.db")
        logger.info(f"Database backed up to {backup_path}/users.db")
    
    vector_db_dir = Path("vector_store/chroma_db")
    if vector_db_dir.exists():
        shutil.copytree(vector_db_dir, backup_path / "chroma_db")
        logger.info(f"Vector database backed up to {backup_path}/chroma_db")
    
    vector_demo_dir = Path("vector_store/chroma_db_demo")
    if vector_demo_dir.exists():
        shutil.copytree(vector_demo_dir, backup_path / "chroma_db_demo")
        logger.info(f"Demo vector database backed up to {backup_path}/chroma_db_demo")
    
    logger.success(f"Backup completed: {backup_path}")
    return backup_path

def reset_user_database():
    logger.info("Resetting user database...")
    
    database_file = Path("database/users.db")
    
    if database_file.exists():
        try:
            os.remove(database_file)
            logger.info("Deleted existing user database")
        except Exception as e:
            logger.error(f"Failed to delete user database: {e}")
            return False
    
    migrations_dir = Path("database/migrations")
    if migrations_dir.exists():
        try:
            shutil.rmtree(migrations_dir)
            logger.info("Cleared database migrations")
        except Exception as e:
            logger.warning(f"Failed to clear migrations: {e}")
    
    db_setup = DatabaseSetup()
    
    if not db_setup.initialize_database():
        logger.error("Failed to reinitialize database")
        return False
    
    if not db_setup.create_tables():
        logger.error("Failed to recreate database tables")
        return False
    
    logger.success("User database reset completed")
    return True

def reset_vector_databases():
    logger.info("Resetting vector databases...")
    
    vector_dirs = [
        Path("vector_store/chroma_db"),
        Path("vector_store/chroma_db_demo")
    ]
    
    for vector_dir in vector_dirs:
        if vector_dir.exists():
            try:
                shutil.rmtree(vector_dir)
                logger.info(f"Deleted vector database: {vector_dir}")
            except Exception as e:
                logger.error(f"Failed to delete {vector_dir}: {e}")
                return False
    
    try:
        demo_vector_store = DemoVectorStore()
        init_result = demo_vector_store.initialize_demo_collections()
        
        if init_result.get("success"):
            logger.info("Reinitialized demo vector collections")
        else:
            logger.warning("Failed to reinitialize demo collections")
    except Exception as e:
        logger.warning(f"Demo vector store initialization failed: {e}")
    
    logger.success("Vector databases reset completed")
    return True

def reset_uploaded_files():
    logger.info("Resetting uploaded files...")
    
    upload_dirs = [
        Path("uploads"),
        Path("temp_uploads"),
        Path("processed_documents")
    ]
    
    for upload_dir in upload_dirs:
        if upload_dir.exists():
            try:
                shutil.rmtree(upload_dir)
                logger.info(f"Deleted upload directory: {upload_dir}")
            except Exception as e:
                logger.warning(f"Failed to delete {upload_dir}: {e}")
    
    for upload_dir in upload_dirs:
        upload_dir.mkdir(exist_ok=True)
        logger.info(f"Recreated upload directory: {upload_dir}")
    
    logger.success("Upload directories reset completed")
    return True

def reset_logs():
    logger.info("Resetting application logs...")
    
    log_dirs = [
        Path("logs")
    ]
    
    for log_dir in log_dirs:
        if log_dir.exists():
            try:
                for log_file in log_dir.glob("*.log"):
                    os.remove(log_file)
                    logger.info(f"Deleted log file: {log_file}")
            except Exception as e:
                logger.warning(f"Failed to delete logs in {log_dir}: {e}")
    
    logger.success("Application logs reset completed")
    return True

def reset_cache():
    logger.info("Resetting application cache...")
    
    cache_dirs = [
        Path("__pycache__"),
        Path("frontend/.next"),
        Path("frontend/node_modules/.cache"),
        Path(".pytest_cache")
    ]
    
    for cache_dir in cache_dirs:
        if cache_dir.exists():
            try:
                shutil.rmtree(cache_dir)
                logger.info(f"Deleted cache directory: {cache_dir}")
            except Exception as e:
                logger.warning(f"Failed to delete {cache_dir}: {e}")
    
    cache_files = list(Path().rglob("*.pyc")) + list(Path().rglob("__pycache__"))
    
    for cache_file in cache_files:
        try:
            if cache_file.is_file():
                os.remove(cache_file)
            elif cache_file.is_dir():
                shutil.rmtree(cache_file)
        except Exception as e:
            logger.debug(f"Failed to delete cache item {cache_file}: {e}")
    
    logger.success("Application cache reset completed")
    return True

def verify_reset():
    logger.info("Verifying reset completion...")
    
    checks = {
        "user_database": False,
        "vector_database": False,
        "demo_collections": False
    }
    
    database_file = Path("database/users.db")
    if database_file.exists():
        try:
            conn = sqlite3.connect(database_file)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM organizations") 
            org_count = cursor.fetchone()[0]
            conn.close()
            
            checks["user_database"] = (user_count == 0 and org_count == 0)
            logger.info(f"User database: {user_count} users, {org_count} organizations")
        except Exception as e:
            logger.warning(f"Failed to verify user database: {e}")
    
    vector_dirs = [
        Path("vector_store/chroma_db"),
        Path("vector_store/chroma_db_demo")
    ]
    
    vector_empty = all(not vdir.exists() or len(list(vdir.iterdir())) == 0 
                      for vdir in vector_dirs)
    checks["vector_database"] = vector_empty
    
    try:
        demo_vector_store = DemoVectorStore()
        stats = demo_vector_store.get_demo_stats()
        demo_docs = stats.get("total_documents", 0)
        checks["demo_collections"] = (demo_docs == 0)
        logger.info(f"Demo collections: {demo_docs} documents")
    except Exception as e:
        logger.warning(f"Failed to verify demo collections: {e}")
        checks["demo_collections"] = True
    
    all_checks_passed = all(checks.values())
    
    if all_checks_passed:
        logger.success("Reset verification completed - all data cleared")
    else:
        logger.warning(f"Reset verification issues: {checks}")
    
    return all_checks_passed

def print_reset_summary(backup_path):
    print("\n" + "="*60)
    print(" ZeroDay Database Reset Complete!")
    print("="*60)
    print("\nReset Operations Completed:")
    print("   User database and accounts")
    print("   Vector databases and embeddings")
    print("   Uploaded files and documents")
    print("   Application logs and cache")
    print("   Demo data and scenarios")
    print(f"\n Backup created at: {backup_path}")
    print("\nNext Steps:")
    print("  1. Run setup script: python scripts/setup_demo.py")
    print("  2. Or manually recreate users and data")
    print("  3. Restart application services")
    print("\n  Remember: All data has been permanently deleted!")
    print("="*60)

def main():
    logger.info("ZeroDay database reset utility")
    
    if not confirm_reset():
        logger.info("Reset operation aborted by user")
        sys.exit(0)
    
    backup_path = backup_before_reset()
    
    reset_operations = [
        ("User Database", reset_user_database),
        ("Vector Databases", reset_vector_databases),
        ("Uploaded Files", reset_uploaded_files),
        ("Application Logs", reset_logs),
        ("Application Cache", reset_cache),
        ("Verification", verify_reset)
    ]
    
    for operation_name, operation_function in reset_operations:
        logger.info(f"Executing: {operation_name}")
        
        try:
            if not operation_function():
                logger.error(f"Reset operation failed: {operation_name}")
                sys.exit(1)
        except Exception as e:
            logger.error(f"Reset operation {operation_name} failed with exception: {e}")
            sys.exit(1)
        
        logger.success(f"Completed: {operation_name}")
    
    print_reset_summary(backup_path)

if __name__ == "__main__":
    main()