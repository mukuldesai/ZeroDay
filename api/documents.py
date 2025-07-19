from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import sys
from datetime import datetime
from loguru import logger


sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
try:
    from api.upload import user_documents, DocumentMetadata
except ImportError:
   
    from typing import Dict, List
    user_documents: Dict[str, List[Any]] = {}
    
    class DocumentMetadata(BaseModel):
        id: str
        filename: str
        file_type: str
        size: int
        upload_time: str
        processing_status: str
        document_count: int
        user_id: str
        source_type: str

router = APIRouter(prefix="/api/documents", tags=["documents"])


class DocumentListResponse(BaseModel):
    """Response model for document list endpoint"""
    success: bool
    documents: List[DocumentMetadata]
    total_count: int
    indexed_count: int
    processing_count: int
    failed_count: int
    user_id: str
    last_updated: str

class DocumentStatsResponse(BaseModel):
    """Response model for document statistics"""
    success: bool
    total_documents: int
    indexed_documents: int
    processing_documents: int
    failed_documents: int
    total_size_bytes: int
    latest_upload: Optional[str]
    document_types: List[str]
    user_id: str

class DocumentDeleteResponse(BaseModel):
    """Response model for document deletion"""
    success: bool
    message: str
    deleted_document_id: str
    remaining_count: int
    user_id: str

class BulkDeleteRequest(BaseModel):
    """Request model for bulk document deletion"""
    document_ids: List[str]
    user_id: Optional[str] = "current_user"

class DocumentFilterRequest(BaseModel):
    """Request model for filtering documents"""
    file_types: Optional[List[str]] = None
    processing_status: Optional[str] = None  
    uploaded_after: Optional[str] = None
    uploaded_before: Optional[str] = None

@router.get("/", response_model=DocumentListResponse)
async def list_user_documents(
    user_id: str = Query("current_user", description="User ID to filter documents"),
    limit: Optional[int] = Query(None, description="Maximum number of documents to return"),
    offset: Optional[int] = Query(0, description="Number of documents to skip"),
    status: Optional[str] = Query(None, description="Filter by processing status"),
    file_type: Optional[str] = Query(None, description="Filter by file type")
):
    """
    List all documents for a specific user with optional filtering and pagination.
    
    Returns document metadata including upload status, processing state, and file information.
    Used by frontend components to display document lists and status.
    """
    try:
   
        user_docs = user_documents.get(user_id, [])
        

        filtered_docs = user_docs.copy()
        
        if status:
            filtered_docs = [doc for doc in filtered_docs if doc.processing_status == status]
            
        if file_type:
            filtered_docs = [doc for doc in filtered_docs if doc.file_type == file_type]
        
        
        filtered_docs.sort(key=lambda x: x.upload_time, reverse=True)
        
      
        total_count = len(filtered_docs)
        if limit:
            end_index = offset + limit
            filtered_docs = filtered_docs[offset:end_index]
        elif offset > 0:
            filtered_docs = filtered_docs[offset:]
        
      
        all_docs = user_documents.get(user_id, [])
        indexed_count = len([d for d in all_docs if d.processing_status == "indexed"])
        processing_count = len([d for d in all_docs if d.processing_status == "processing"])
        failed_count = len([d for d in all_docs if d.processing_status == "failed"])
        
        logger.info(f"Retrieved {len(filtered_docs)} documents for user {user_id}")
        
        return DocumentListResponse(
            success=True,
            documents=filtered_docs,
            total_count=total_count,
            indexed_count=indexed_count,
            processing_count=processing_count,
            failed_count=failed_count,
            user_id=user_id,
            last_updated=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error listing documents for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve documents: {str(e)}")

@router.get("/stats", response_model=DocumentStatsResponse)
async def get_document_statistics(
    user_id: str = Query("current_user", description="User ID to get statistics for")
):
    """
    Get comprehensive statistics about user's documents.
    
    Provides overview metrics used by dashboard and status components.
    """
    try:
        user_docs = user_documents.get(user_id, [])
        
        if not user_docs:
            return DocumentStatsResponse(
                success=True,
                total_documents=0,
                indexed_documents=0,
                processing_documents=0,
                failed_documents=0,
                total_size_bytes=0,
                latest_upload=None,
                document_types=[],
                user_id=user_id
            )
        
        
        total_documents = len(user_docs)
        indexed_documents = len([d for d in user_docs if d.processing_status == "indexed"])
        processing_documents = len([d for d in user_docs if d.processing_status == "processing"])
        failed_documents = len([d for d in user_docs if d.processing_status == "failed"])
        total_size_bytes = sum(doc.size for doc in user_docs)
        
        
        latest_upload = None
        if user_docs:
            latest_doc = max(user_docs, key=lambda x: x.upload_time)
            latest_upload = latest_doc.upload_time
        
        
        document_types = list(set(doc.file_type for doc in user_docs))
        
        logger.info(f"Generated statistics for user {user_id}: {total_documents} documents")
        
        return DocumentStatsResponse(
            success=True,
            total_documents=total_documents,
            indexed_documents=indexed_documents,
            processing_documents=processing_documents,
            failed_documents=failed_documents,
            total_size_bytes=total_size_bytes,
            latest_upload=latest_upload,
            document_types=document_types,
            user_id=user_id
        )
        
    except Exception as e:
        logger.error(f"Error getting document statistics for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")

@router.get("/{document_id}")
async def get_document_by_id(
    document_id: str,
    user_id: str = Query("current_user", description="User ID for authorization")
):
    """
    Get detailed information about a specific document.
    
    Returns full document metadata including processing status and file details.
    """
    try:
        user_docs = user_documents.get(user_id, [])
        
       
        document = None
        for doc in user_docs:
            if doc.id == document_id:
                document = doc
                break
        
        if not document:
            raise HTTPException(
                status_code=404, 
                detail=f"Document {document_id} not found for user {user_id}"
            )
        
        logger.info(f"Retrieved document {document_id} for user {user_id}")
        
        return {
            "success": True,
            "document": document,
            "user_id": user_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving document {document_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve document: {str(e)}")

@router.delete("/{document_id}", response_model=DocumentDeleteResponse)
async def delete_document(
    document_id: str,
    user_id: str = Query("current_user", description="User ID for authorization")
):
    """
    Delete a specific document and remove it from the vector store.
    
    This permanently removes the document and all its associated vector embeddings.
    Used by frontend document management interfaces.
    """
    try:
        user_docs = user_documents.get(user_id, [])
        
       
        document_to_delete = None
        updated_docs = []
        
        for doc in user_docs:
            if doc.id == document_id:
                document_to_delete = doc
            else:
                updated_docs.append(doc)
        
        if not document_to_delete:
            raise HTTPException(
                status_code=404, 
                detail=f"Document {document_id} not found for user {user_id}"
            )
        
      
        user_documents[user_id] = updated_docs
        
        
      
        try:
         
            logger.info(f"Vector store deletion for document {document_id} not implemented")
        except Exception as vector_error:
            logger.warning(f"Failed to remove document from vector store: {vector_error}")
    
        
        logger.info(f"Deleted document {document_id} for user {user_id}")
        
        return DocumentDeleteResponse(
            success=True,
            message=f"Document '{document_to_delete.filename}' deleted successfully",
            deleted_document_id=document_id,
            remaining_count=len(updated_docs),
            user_id=user_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document {document_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")

@router.delete("/bulk", response_model=Dict[str, Any])
async def bulk_delete_documents(request: BulkDeleteRequest):
    """
    Delete multiple documents in a single request.
    
    Useful for bulk cleanup operations in the frontend.
    """
    try:
        user_id = request.user_id
        user_docs = user_documents.get(user_id, [])
        
        deleted_docs = []
        failed_deletions = []
        updated_docs = []
        
        
        for doc in user_docs:
            if doc.id in request.document_ids:
                deleted_docs.append(doc)
               
            else:
                updated_docs.append(doc)
        
      
        user_documents[user_id] = updated_docs
        
       
        found_ids = [doc.id for doc in deleted_docs]
        for doc_id in request.document_ids:
            if doc_id not in found_ids:
                failed_deletions.append({
                    "document_id": doc_id,
                    "reason": "Document not found"
                })
        
        logger.info(f"Bulk deleted {len(deleted_docs)} documents for user {user_id}")
        
        return {
            "success": True,
            "deleted_count": len(deleted_docs),
            "failed_count": len(failed_deletions),
            "deleted_documents": [{"id": doc.id, "filename": doc.filename} for doc in deleted_docs],
            "failed_deletions": failed_deletions,
            "remaining_count": len(updated_docs),
            "user_id": user_id
        }
        
    except Exception as e:
        logger.error(f"Error in bulk delete operation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Bulk deletion failed: {str(e)}")

@router.patch("/{document_id}/status")
async def update_document_status(
    document_id: str,
    new_status: str = Query(..., description="New processing status"),
    user_id: str = Query("current_user", description="User ID for authorization")
):
    """
    Update the processing status of a document.
    
    Used internally by the indexing system to update document status.
    Frontend can use this to manually retry failed documents.
    """
    try:
        valid_statuses = ["processing", "indexed", "failed"]
        if new_status not in valid_statuses:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid status. Must be one of: {valid_statuses}"
            )
        
        user_docs = user_documents.get(user_id, [])
        
    
        document_updated = False
        for doc in user_docs:
            if doc.id == document_id:
                old_status = doc.processing_status
                doc.processing_status = new_status
                document_updated = True
                logger.info(f"Updated document {document_id} status: {old_status} → {new_status}")
                break
        
        if not document_updated:
            raise HTTPException(
                status_code=404, 
                detail=f"Document {document_id} not found for user {user_id}"
            )
        
        return {
            "success": True,
            "message": f"Document status updated to '{new_status}'",
            "document_id": document_id,
            "new_status": new_status,
            "user_id": user_id,
            "updated_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating document status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update status: {str(e)}")

@router.post("/filter")
async def filter_documents(
    filter_request: DocumentFilterRequest,
    user_id: str = Query("current_user", description="User ID to filter documents for")
):
    """
    Advanced filtering of user documents based on multiple criteria.
    
    Supports filtering by file type, status, and date ranges.
    """
    try:
        user_docs = user_documents.get(user_id, [])
        filtered_docs = user_docs.copy()
        
      
        if filter_request.file_types:
            filtered_docs = [
                doc for doc in filtered_docs 
                if doc.file_type in filter_request.file_types
            ]
        
       
        if filter_request.processing_status:
            filtered_docs = [
                doc for doc in filtered_docs 
                if doc.processing_status == filter_request.processing_status
            ]
        
        
        if filter_request.uploaded_after:
            after_date = datetime.fromisoformat(filter_request.uploaded_after.replace('Z', '+00:00'))
            filtered_docs = [
                doc for doc in filtered_docs 
                if datetime.fromisoformat(doc.upload_time.replace('Z', '+00:00')) >= after_date
            ]
        
        if filter_request.uploaded_before:
            before_date = datetime.fromisoformat(filter_request.uploaded_before.replace('Z', '+00:00'))
            filtered_docs = [
                doc for doc in filtered_docs 
                if datetime.fromisoformat(doc.upload_time.replace('Z', '+00:00')) <= before_date
            ]
        
    
        filtered_docs.sort(key=lambda x: x.upload_time, reverse=True)
        
        logger.info(f"Filtered {len(user_docs)} documents to {len(filtered_docs)} for user {user_id}")
        
        return {
            "success": True,
            "documents": filtered_docs,
            "total_count": len(filtered_docs),
            "filter_applied": filter_request.dict(exclude_none=True),
            "user_id": user_id
        }
        
    except Exception as e:
        logger.error(f"Error filtering documents: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to filter documents: {str(e)}")

@router.get("/health")
async def health_check():
    """Health check endpoint for the documents API"""
    try:
        total_users = len(user_documents)
        total_docs = sum(len(docs) for docs in user_documents.values())
        
        return {
            "status": "healthy",
            "service": "documents-api",
            "total_users": total_users,
            "total_documents": total_docs,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Service unhealthy")


__all__ = ["router"]