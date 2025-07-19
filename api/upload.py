from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import tempfile
import shutil
import asyncio
from pathlib import Path
from loguru import logger
import json
import hashlib
from datetime import datetime

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from data_sources.code_parser import CodeParser
from data_sources.doc_ingestor import DocIngestor
from data_sources.slack_parser import SlackParser
from data_sources.pr_fetcher import PRFetcher
from data_sources.ticket_fetcher import TicketFetcher
from vector_store.index_builder import IndexBuilder

from dotenv import load_dotenv
load_dotenv()

router = APIRouter(prefix="/api/upload", tags=["upload"])


class GitHubRepoRequest(BaseModel):
    repo_url: str
    fetch_prs: bool = True
    fetch_issues: bool = True
    demo_mode: Optional[bool] = False
    user_id: Optional[str] = "current_user"
    auto_index: Optional[bool] = True  

class ProcessRequest(BaseModel):
    action: str = "build_index"
    demo_mode: Optional[bool] = False
    user_id: Optional[str] = "current_user"

class DocumentMetadata(BaseModel):
    """Metadata for tracking uploaded documents"""
    id: str
    filename: str
    file_type: str
    size: int
    upload_time: str
    processing_status: str  
    document_count: int
    user_id: str
    source_type: str  


user_documents: Dict[str, List[DocumentMetadata]] = {}

def generate_document_id(filename: str, user_id: str) -> str:
    """Generate unique document ID"""
    content = f"{filename}_{user_id}_{datetime.now().isoformat()}"
    return hashlib.md5(content.encode()).hexdigest()[:12]

def save_document_metadata(user_id: str, metadata: DocumentMetadata):
    """Save document metadata for user tracking"""
    if user_id not in user_documents:
        user_documents[user_id] = []
    user_documents[user_id].append(metadata)

async def auto_index_documents(documents: List[Dict], user_id: str, doc_metadata: DocumentMetadata) -> Dict[str, Any]:
    """Automatically index documents to vector store"""
    try:
        logger.info(f"Auto-indexing {len(documents)} documents for user {user_id}")
        
        
        for doc in documents:
            doc["user_id"] = user_id
            doc["document_id"] = doc_metadata.id
            doc["source_file"] = doc_metadata.filename
            doc["upload_time"] = doc_metadata.upload_time
        
     
        index_builder = IndexBuilder()
        result = index_builder.add_documents(documents)
        
        
        doc_metadata.processing_status = "indexed"
        
        logger.info(f"Successfully indexed {len(documents)} documents")
        return {
            "indexed": True,
            "documents_count": len(documents),
            "index_stats": result
        }
        
    except Exception as e:
        logger.error(f"Auto-indexing failed: {str(e)}")
        doc_metadata.processing_status = "failed"
        return {
            "indexed": False,
            "error": str(e)
        }

@router.post("/github")
async def upload_github_data(request: GitHubRepoRequest):
    try:
        logger.info(f"Processing GitHub repo for user {request.user_id}: {request.repo_url}")
        
     
        doc_id = generate_document_id(request.repo_url, request.user_id)
        doc_metadata = DocumentMetadata(
            id=doc_id,
            filename=request.repo_url.split('/')[-1],
            file_type="github_repo",
            size=0,  
            upload_time=datetime.now().isoformat(),
            processing_status="processing",
            document_count=0,
            user_id=request.user_id,
            source_type="github"
        )
        
        if request.demo_mode:
            return await _generate_demo_github_data(request, doc_metadata)
        
        documents = []
        
       
        if request.fetch_prs:
            pr_fetcher = PRFetcher()
            pr_docs = await pr_fetcher.fetch_pull_requests(request.repo_url, limit=50)
            documents.extend(pr_docs)
            logger.info(f"Fetched {len(pr_docs)} PR documents")
        
      
        if request.fetch_issues:
            ticket_fetcher = TicketFetcher()
            issue_docs = await ticket_fetcher.fetch_tickets("github", limit=50)
            documents.extend(issue_docs)
            logger.info(f"Fetched {len(issue_docs)} issue documents")
        
   
        doc_metadata.document_count = len(documents)
        doc_metadata.size = sum(len(str(doc)) for doc in documents)
        
       
        temp_dir = Path("./temp_data/github")
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        with open(temp_dir / f"github_data_{doc_id}.json", "w", encoding="utf-8") as f:
            json.dump(documents, f, indent=2, default=str)

       
        save_document_metadata(request.user_id, doc_metadata)
        
        
        index_result = {}
        if request.auto_index and documents:
            index_result = await auto_index_documents(documents, request.user_id, doc_metadata)
        
        response = {
            "success": True,
            "message": f"Processed {len(documents)} documents from GitHub",
            "document_id": doc_id,
            "documents_count": len(documents),
            "user_id": request.user_id,
            "demo_mode": request.demo_mode,
            "metadata": doc_metadata.dict()
        }
        
        if index_result:
            response["indexing"] = index_result
            
        return response
        
    except Exception as e:
        logger.error(f"Error processing GitHub data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/files")
async def upload_files(
    files: List[UploadFile] = File(...), 
    file_type: str = Form(...),  
    demo_mode: Optional[str] = Form("false"),
    user_id: Optional[str] = Form("current_user"),
    auto_index: Optional[str] = Form("true") 
):
    try:
        is_demo = demo_mode.lower() == "true"
        should_auto_index = auto_index.lower() == "true"
        
        logger.info(f"Processing {len(files)} files of type: {file_type} for user {user_id} (demo: {is_demo})")
        
        
        doc_id = generate_document_id(f"batch_{len(files)}_files", user_id)
        doc_metadata = DocumentMetadata(
            id=doc_id,
            filename=f"{len(files)} files ({file_type})",
            file_type=file_type,
            size=0,  
            upload_time=datetime.now().isoformat(),
            processing_status="processing",
            document_count=0,
            user_id=user_id,
            source_type="file_upload"
        )
        
        if is_demo:
            return await _generate_demo_file_data(files, file_type, user_id, doc_metadata)
        
        
        temp_dir = Path(f"./temp_data/{file_type}")
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        documents = []
        total_size = 0

    
        for file in files:
            file_path = temp_dir / file.filename
            
          
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
                total_size += len(content)

           
            file_type_lower = file_type.lower()
            
            try:
                if file_type_lower in {"docs", "documentation"}:
                    doc_ingestor = DocIngestor(user_id=user_id)
                    file_docs = await doc_ingestor.ingest_single_file(str(file_path))
                    documents.extend(file_docs)

                elif file_type_lower == "slack":
                    slack_parser = SlackParser()
                    file_docs = await slack_parser.parse_slack_export(str(file_path))
                    documents.extend(file_docs)

                elif file_type_lower == "codebase":
                    code_parser = CodeParser()
                    file_docs = await code_parser.parse_codebase(str(file_path))
                    documents.extend(file_docs)

                else:
                    logger.warning(f"Unsupported file type: {file_type}")
                    
                    documents.append({
                        "content": f"File: {file.filename}",
                        "metadata": {
                            "filename": file.filename,
                            "type": file_type,
                            "size": len(content)
                        }
                    })
                    
            except Exception as file_error:
                logger.error(f"Error processing file {file.filename}: {str(file_error)}")
              
                documents.append({
                    "content": f"Error processing file: {file.filename}",
                    "metadata": {
                        "filename": file.filename,
                        "type": file_type,
                        "error": str(file_error),
                        "status": "failed"
                    }
                })
        
       
        doc_metadata.document_count = len(documents)
        doc_metadata.size = total_size
        
     
        with open(temp_dir / f"{file_type}_data_{doc_id}.json", "w", encoding="utf-8") as f:
            json.dump(documents, f, indent=2, default=str)

        
        save_document_metadata(user_id, doc_metadata)
        
        
        index_result = {}
        if should_auto_index and documents:
            index_result = await auto_index_documents(documents, user_id, doc_metadata)
        
        response = {
            "success": True,
            "message": f"Processed {len(documents)} documents from {len(files)} files",
            "document_id": doc_id,
            "documents_count": len(documents),
            "file_count": len(files),
            "user_id": user_id,
            "demo_mode": is_demo,
            "metadata": doc_metadata.dict()
        }
        
        if index_result:
            response["indexing"] = index_result
            
        return response
        
    except Exception as e:
        logger.error(f"Error processing files: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/process")
async def process_data(request: ProcessRequest):
    """Process and index all uploaded data"""
    try:
        logger.info(f"Building vector index from uploaded data for user {request.user_id} (demo: {request.demo_mode})")
        
        if request.demo_mode:
            return await _generate_demo_processing_result(request)
        
        all_documents = []
        temp_base = Path("./temp_data")
        processed_files = []
        
        
        if temp_base.exists():
            for data_type_dir in temp_base.iterdir():
                if data_type_dir.is_dir():
                    for json_file in data_type_dir.glob("*.json"):
                        try:
                            with open(json_file, "r", encoding="utf-8") as f:
                                docs = json.load(f)
                                
                                
                                for doc in docs:
                                    doc["user_id"] = request.user_id
                                    doc["source_file"] = json_file.name
                                    doc["data_type"] = data_type_dir.name
                                
                                all_documents.extend(docs)
                                processed_files.append(str(json_file))
                                logger.info(f"Loaded {len(docs)} documents from {json_file}")
                                
                        except Exception as e:
                            logger.warning(f"Error loading {json_file}: {str(e)}")
        
       
        if not all_documents:
            logger.info("No uploaded data found, generating sample data...")
            
            ticket_fetcher = TicketFetcher()
            sample_tickets = await ticket_fetcher.fetch_tickets("mock", limit=20)
            all_documents.extend(sample_tickets)
            
            try:
                code_parser = CodeParser()
                code_docs = await code_parser.parse_codebase(".")
                all_documents.extend(code_docs[:10])
            except:
                pass
        
        
        index_builder = IndexBuilder()
        result = index_builder.add_documents(all_documents)
        
        
        for user_id, docs in user_documents.items():
            if user_id == request.user_id:
                for doc in docs:
                    if doc.processing_status == "processing":
                        doc.processing_status = "indexed"
        
        
        try:
            if temp_base.exists():
                shutil.rmtree(temp_base)
        except:
            pass
        
        return {
            "success": True,
            "message": f"Successfully indexed {len(all_documents)} documents",
            "documents_indexed": len(all_documents),
            "files_processed": processed_files,
            "index_stats": result,
            "user_id": request.user_id,
            "demo_mode": request.demo_mode
        }
        
    except Exception as e:
        logger.error(f"Error processing data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_upload_status(user_id: Optional[str] = "current_user"):
    """Get upload and indexing status for user"""
    try:
        
        try:
            from vector_store.retriever import ContextualRetriever
            retriever = ContextualRetriever()
            vector_status = "ready"
            document_count = 0  
        except:
            vector_status = "empty"
            document_count = 0
        
        
        user_docs = user_documents.get(user_id, [])
        
        
        temp_data = {}
        temp_base = Path("./temp_data")
        if temp_base.exists():
            for data_type_dir in temp_base.iterdir():
                if data_type_dir.is_dir():
                    temp_data[data_type_dir.name] = len(list(data_type_dir.glob("*.json")))
        
        return {
            "vector_store_status": vector_status,
            "documents_indexed": document_count,
            "user_documents": [doc.dict() for doc in user_docs],
            "user_document_count": len(user_docs),
            "temp_data": temp_data,
            "upload_directory": str(temp_base.absolute()),
            "ready_for_use": vector_status == "ready" and len(user_docs) > 0,
            "user_id": user_id
        }
        
    except Exception as e:
        logger.error(f"Error getting upload status: {str(e)}")
        return {
            "vector_store_status": "error",
            "documents_indexed": 0,
            "user_documents": [],
            "user_document_count": 0,
            "temp_data": {},
            "ready_for_use": False,
            "error": str(e),
            "user_id": user_id
        }

@router.get("/documents")
async def get_user_documents(user_id: Optional[str] = "current_user"):
    """Get list of user's uploaded documents"""
    try:
        user_docs = user_documents.get(user_id, [])
        
        return {
            "success": True,
            "documents": [doc.dict() for doc in user_docs],
            "count": len(user_docs),
            "user_id": user_id
        }
        
    except Exception as e:
        logger.error(f"Error getting user documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/documents/{document_id}")
async def delete_document(document_id: str, user_id: Optional[str] = "current_user"):
    """Delete a specific document"""
    try:
        user_docs = user_documents.get(user_id, [])
        
        
        doc_to_remove = None
        for i, doc in enumerate(user_docs):
            if doc.id == document_id:
                doc_to_remove = user_docs.pop(i)
                break
        
        if not doc_to_remove:
            raise HTTPException(status_code=404, detail="Document not found")
        
       
        
        return {
            "success": True,
            "message": f"Document {document_id} deleted successfully",
            "deleted_document": doc_to_remove.dict(),
            "user_id": user_id
        }
        
    except Exception as e:
        logger.error(f"Error deleting document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/clear")
async def clear_uploaded_data(user_id: Optional[str] = "current_user"):
    """Clear all uploaded data for user"""
    try:
       
        temp_base = Path("./temp_data")
        if temp_base.exists():
            shutil.rmtree(temp_base)
        
        
        if user_id in user_documents:
            del user_documents[user_id]
        
       
        try:
            from vector_store.index_builder import IndexBuilder
            index_builder = IndexBuilder()
          
        except:
            pass
        
        return {
            "success": True,
            "message": "All uploaded data cleared successfully",
            "user_id": user_id
        }
        
    except Exception as e:
        logger.error(f"Error clearing data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def _generate_demo_github_data(request: GitHubRepoRequest, doc_metadata: DocumentMetadata):
    await asyncio.sleep(0.5)
    
    demo_documents = [
        {
            "type": "pull_request",
            "title": "Add user authentication system",
            "description": "Implements JWT-based authentication with login/logout",
            "author": "demo_developer",
            "status": "merged",
            "files_changed": ["auth.py", "login.tsx", "middleware.py"]
        },
        {
            "type": "issue",
            "title": "Fix responsive design on mobile",
            "description": "Navigation menu breaks on screens smaller than 768px",
            "priority": "high",
            "labels": ["bug", "frontend", "mobile"]
        }
    ]
    
 
    doc_metadata.document_count = len(demo_documents)
    doc_metadata.processing_status = "indexed" if request.auto_index else "processed"
    save_document_metadata(request.user_id, doc_metadata)
    
    return {
        "success": True,
        "message": f"[DEMO] Generated {len(demo_documents)} sample documents from GitHub",
        "document_id": doc_metadata.id,
        "documents_count": len(demo_documents),
        "user_id": request.user_id,
        "demo_mode": True,
        "metadata": doc_metadata.dict(),
        "demo_data": demo_documents,
        "indexing": {"indexed": True, "documents_count": len(demo_documents)} if request.auto_index else {}
    }

async def _generate_demo_file_data(files, file_type, user_id, doc_metadata: DocumentMetadata):
    await asyncio.sleep(0.3)
    
    demo_documents = []
    for file in files:
        demo_documents.append({
            "type": file_type,
            "filename": file.filename,
            "size": file.size or 1024,
            "content_preview": f"Demo content for {file.filename}",
            "processed": True
        })
    
   
    doc_metadata.document_count = len(demo_documents)
    doc_metadata.processing_status = "indexed"
    save_document_metadata(user_id, doc_metadata)
    
    return {
        "success": True,
        "message": f"[DEMO] Processed {len(demo_documents)} demo files",
        "document_id": doc_metadata.id,
        "documents_count": len(demo_documents),
        "file_count": len(files),
        "user_id": user_id,
        "demo_mode": True,
        "metadata": doc_metadata.dict(),
        "demo_data": demo_documents,
        "indexing": {"indexed": True, "documents_count": len(demo_documents)}
    }

async def _generate_demo_processing_result(request: ProcessRequest):
    await asyncio.sleep(1.0)
    
    return {
        "success": True,
        "message": "[DEMO] Successfully indexed demo documents",
        "documents_indexed": 45,
        "files_processed": ["demo_file1.json", "demo_file2.json"],
        "index_stats": {
            "total_chunks": 120,
            "vector_dimensions": 1536,
            "index_size": "2.1 MB",
            "processing_time": "1.2 seconds"
        },
        "user_id": request.user_id,
        "demo_mode": True
    }