import { useState, useEffect, useCallback, useRef } from 'react';


export interface DocumentMetadata {
  id: string;
  filename: string;
  file_type: string;
  size: number;
  upload_time: string;
  processing_status: 'processing' | 'indexed' | 'failed';
  document_count: number;
  user_id: string;
  source_type: string;
}

export interface DocumentStats {
  total_documents: number;
  indexed_documents: number;
  processing_documents: number;
  failed_documents: number;
  total_size_bytes: number;
  latest_upload?: string;
  document_types: string[];
}

export interface DocumentListResponse {
  success: boolean;
  documents: DocumentMetadata[];
  total_count: number;
  indexed_count: number;
  processing_count: number;
  failed_count: number;
  user_id: string;
  last_updated: string;
}

export interface DocumentDeleteResponse {
  success: boolean;
  message: string;
  deleted_document_id: string;
  remaining_count: number;
  user_id: string;
}


export interface UseDocumentsOptions {
  user_id?: string;
  auto_refresh_interval?: number; 
  auto_refresh_on_status_change?: boolean;
  enable_polling?: boolean;
}


export interface UseDocumentsReturn {
  
  documents: DocumentMetadata[];
  stats: DocumentStats | null;
  
  loading: boolean;
  refreshing: boolean;
  deleting: string | null;
  
 
  error: string | null;
  deleteError: string | null;
  
  
  refreshDocuments: () => Promise<void>;
  deleteDocument: (documentId: string) => Promise<boolean>;
  bulkDeleteDocuments: (documentIds: string[]) => Promise<boolean>;
  updateDocumentStatus: (documentId: string, status: 'processing' | 'indexed' | 'failed') => Promise<boolean>;
  clearError: () => void;
  
  
  indexedDocuments: DocumentMetadata[];
  processingDocuments: DocumentMetadata[];
  failedDocuments: DocumentMetadata[];
  hasDocuments: boolean;
  hasIndexedDocuments: boolean;
  
  // Filter helpers
  getDocumentsByType: (fileType: string) => DocumentMetadata[];
  getDocumentsByStatus: (status: 'processing' | 'indexed' | 'failed') => DocumentMetadata[];
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Custom React hook for managing document state and operations.
 * 
 * Provides comprehensive document management functionality including:
 * - Fetching and refreshing document lists
 * - Document deletion (single and bulk)
 * - Status updates and monitoring
 * - Auto-refresh capabilities
 * - Error handling and loading states
 * 
 * @param options
 * @returns 
 */
export const useDocuments = (options: UseDocumentsOptions = {}): UseDocumentsReturn => {
  const {
    user_id = 'current_user',
    auto_refresh_interval = 30000, 
    auto_refresh_on_status_change = true,
    enable_polling = true
  } = options;

  const [documents, setDocuments] = useState<DocumentMetadata[]>([]);
  const [stats, setStats] = useState<DocumentStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [deleting, setDeleting] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [deleteError, setDeleteError] = useState<string | null>(null);


  const mountedRef = useRef(true);
  const refreshIntervalRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    return () => {
      mountedRef.current = false;
      if (refreshIntervalRef.current) {
        clearInterval(refreshIntervalRef.current);
      }
    };
  }, []);

 
  const apiRequest = useCallback(async <T>(
    url: string, 
    options: RequestInit = {}
  ): Promise<T> => {
    try {
      const response = await fetch(`${API_BASE}${url}`, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers
        },
        ...options
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`API Error ${response.status}: ${errorText}`);
      }

      return await response.json();
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown API error';
      console.error(`API request failed for ${url}:`, errorMessage);
      throw new Error(errorMessage);
    }
  }, []);

  
  const fetchDocuments = useCallback(async (isRefresh = false) => {
    if (!mountedRef.current) return;

    try {
      if (isRefresh) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }
      
      setError(null);

     
      const documentsResponse = await apiRequest<DocumentListResponse>(
        `/api/documents/?user_id=${encodeURIComponent(user_id)}`
      );

      
      const statsResponse = await apiRequest<{ success: boolean } & DocumentStats>(
        `/api/documents/stats?user_id=${encodeURIComponent(user_id)}`
      );

      if (!mountedRef.current) return;

      if (documentsResponse.success) {
        setDocuments(documentsResponse.documents);
      }

      if (statsResponse.success) {
        setStats({
          total_documents: statsResponse.total_documents,
          indexed_documents: statsResponse.indexed_documents,
          processing_documents: statsResponse.processing_documents,
          failed_documents: statsResponse.failed_documents,
          total_size_bytes: statsResponse.total_size_bytes,
          latest_upload: statsResponse.latest_upload,
          document_types: statsResponse.document_types
        });
      }

    } catch (err) {
      if (!mountedRef.current) return;
      
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch documents';
      setError(errorMessage);
      console.error('Error fetching documents:', errorMessage);
    
      setDocuments([]);
      setStats(null);
    } finally {
      if (mountedRef.current) {
        setLoading(false);
        setRefreshing(false);
      }
    }
  }, [user_id, apiRequest]);

  
  const refreshDocuments = useCallback(async () => {
    await fetchDocuments(true);
  }, [fetchDocuments]);

  
  const deleteDocument = useCallback(async (documentId: string): Promise<boolean> => {
    if (!mountedRef.current) return false;

    try {
      setDeleting(documentId);
      setDeleteError(null);

      const response = await apiRequest<DocumentDeleteResponse>(
        `/api/documents/${documentId}?user_id=${encodeURIComponent(user_id)}`,
        { method: 'DELETE' }
      );

      if (!mountedRef.current) return false;

      if (response.success) {
      
        setDocuments(prev => prev.filter(doc => doc.id !== documentId));
        
     
        if (stats) {
          setStats(prev => prev ? {
            ...prev,
            total_documents: prev.total_documents - 1,
            
          } : null);
        }

       
        setTimeout(() => refreshDocuments(), 1000);
        
        return true;
      }

      return false;
    } catch (err) {
      if (!mountedRef.current) return false;
      
      const errorMessage = err instanceof Error ? err.message : 'Failed to delete document';
      setDeleteError(errorMessage);
      console.error('Error deleting document:', errorMessage);
      return false;
    } finally {
      if (mountedRef.current) {
        setDeleting(null);
      }
    }
  }, [user_id, apiRequest, refreshDocuments, stats]);

  const bulkDeleteDocuments = useCallback(async (documentIds: string[]): Promise<boolean> => {
    if (!mountedRef.current || documentIds.length === 0) return false;

    try {
      setDeleteError(null);

      const response = await apiRequest<{
        success: boolean;
        deleted_count: number;
        failed_count: number;
        remaining_count: number;
      }>('/api/documents/bulk', {
        method: 'DELETE',
        body: JSON.stringify({
          document_ids: documentIds,
          user_id
        })
      });

      if (!mountedRef.current) return false;

      if (response.success) {
       
        setDocuments(prev => prev.filter(doc => !documentIds.includes(doc.id)));
        
    
        setTimeout(() => refreshDocuments(), 1000);
        
        return response.failed_count === 0;
      }

      return false;
    } catch (err) {
      if (!mountedRef.current) return false;
      
      const errorMessage = err instanceof Error ? err.message : 'Failed to delete documents';
      setDeleteError(errorMessage);
      console.error('Error bulk deleting documents:', errorMessage);
      return false;
    }
  }, [user_id, apiRequest, refreshDocuments]);

 
  const updateDocumentStatus = useCallback(async (
    documentId: string, 
    status: 'processing' | 'indexed' | 'failed'
  ): Promise<boolean> => {
    if (!mountedRef.current) return false;

    try {
      const response = await apiRequest<{ success: boolean }>(
        `/api/documents/${documentId}/status?new_status=${status}&user_id=${encodeURIComponent(user_id)}`,
        { method: 'PATCH' }
      );

      if (!mountedRef.current) return false;

      if (response.success) {
    
        setDocuments(prev => prev.map(doc => 
          doc.id === documentId 
            ? { ...doc, processing_status: status }
            : doc
        ));

        return true;
      }

      return false;
    } catch (err) {
      if (!mountedRef.current) return false;
      
      console.error('Error updating document status:', err);
      return false;
    }
  }, [user_id, apiRequest]);

 
  const clearError = useCallback(() => {
    setError(null);
    setDeleteError(null);
  }, []);


  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);


  useEffect(() => {
    if (!enable_polling || auto_refresh_interval <= 0) return;

    refreshIntervalRef.current = setInterval(() => {
     
      if (!loading && !deleting && !refreshing) {
        fetchDocuments(true);
      }
    }, auto_refresh_interval);

    return () => {
      if (refreshIntervalRef.current) {
        clearInterval(refreshIntervalRef.current);
      }
    };
  }, [enable_polling, auto_refresh_interval, loading, deleting, refreshing, fetchDocuments]);

  
  useEffect(() => {
    if (!auto_refresh_on_status_change) return;

    const processingDocs = documents.filter(doc => doc.processing_status === 'processing');
    
    if (processingDocs.length > 0) {
    
      const processingInterval = setInterval(() => {
        if (!loading && !deleting && !refreshing) {
          fetchDocuments(true);
        }
      }, 5000); 

      return () => clearInterval(processingInterval);
    }
  }, [documents, auto_refresh_on_status_change, loading, deleting, refreshing, fetchDocuments]);

  
  const indexedDocuments = documents.filter(doc => doc.processing_status === 'indexed');
  const processingDocuments = documents.filter(doc => doc.processing_status === 'processing');
  const failedDocuments = documents.filter(doc => doc.processing_status === 'failed');
  const hasDocuments = documents.length > 0;
  const hasIndexedDocuments = indexedDocuments.length > 0;


  const getDocumentsByType = useCallback((fileType: string) => {
    return documents.filter(doc => doc.file_type === fileType);
  }, [documents]);

  const getDocumentsByStatus = useCallback((status: 'processing' | 'indexed' | 'failed') => {
    return documents.filter(doc => doc.processing_status === status);
  }, [documents]);

  return {
 
    documents,
    stats,
    
   
    loading,
    refreshing,
    deleting,
    
  
    error,
    deleteError,
    
 
    refreshDocuments,
    deleteDocument,
    bulkDeleteDocuments,
    updateDocumentStatus,
    clearError,
    
 
    indexedDocuments,
    processingDocuments,
    failedDocuments,
    hasDocuments,
    hasIndexedDocuments,
    
    
    getDocumentsByType,
    getDocumentsByStatus
  };
};

export default useDocuments;
