// components/CommentSection.tsx - Comment component for paper sections
import React, { useState, useEffect } from 'react';
import { MessageCircle, Send, Check, X, Trash2, User, Quote } from 'lucide-react';
import { useWebSocket } from '../hooks/useWebSocket';

interface Comment {
  id: string;
  content: string;
  author: {
    id: string;
    name: string;
    email: string;
  };
  created_at: string;
  is_resolved: boolean;
  resolved_by: {
    id: string;
    name: string;
  } | null;
  replies_count: number;
  selected_text?: string;
  selection_start?: number;
  selection_end?: number;
}

interface CommentSectionProps {
  paperId: string;
  sectionId: string;
  sectionTitle: string;
  currentUserId: string;
  isEditMode?: boolean;
  onCommentAdded?: () => void;
}

const CommentSection: React.FC<CommentSectionProps> = ({
  paperId,
  sectionId,
  sectionTitle,
  currentUserId,
  isEditMode = false,
  onCommentAdded,
}) => {
  const [comments, setComments] = useState<Comment[]>([]);
  const [newComment, setNewComment] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showComments, setShowComments] = useState(false);
  const [includeResolved, setIncludeResolved] = useState(false);
  const [selectedText, setSelectedText] = useState<string>('');
  const [selectionStart, setSelectionStart] = useState<number | null>(null);
  const [selectionEnd, setSelectionEnd] = useState<number | null>(null);

  // WebSocket connection for real-time comment updates
  const { lastMessage } = useWebSocket();

  // Fetch comments for this section
  const fetchComments = async () => {
    try {
      const response = await fetch(
        `http://127.0.0.1:8000/api/v1/papers/${paperId}/sections/${sectionId}/comments?include_resolved=${includeResolved}`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
          },
        }
      );

      if (response.ok) {
        const data = await response.json();
        setComments(data.comments || []);
      }
    } catch (error) {
      console.error('Failed to fetch comments:', error);
    }
  };

  useEffect(() => {
    if (showComments) {
      fetchComments();
    }
  }, [showComments, includeResolved]);

  // Fetch comments count on mount to show correct badge
  useEffect(() => {
    fetchComments();
  }, [sectionId]); // Refetch when section changes

  // Listen for WebSocket comment notifications and refresh comments
  useEffect(() => {
    if (lastMessage && (lastMessage.type === 'comment' || lastMessage.type === 'comment_updated')) {
      // Check if this notification is for the current paper/section
      const data = lastMessage.data || {};
      if (data.paper_id === paperId && data.section_id === sectionId) {
        const action = lastMessage.type === 'comment' ? 'New comment' : `Comment ${data.action || 'updated'}`;
        console.log(`🔔 ${action} notification received, refreshing comments...`);
        fetchComments();
      }
    }
  }, [lastMessage, paperId, sectionId]);

  // Add new comment
  const handleAddComment = async () => {
    if (!newComment.trim()) return;

    setIsLoading(true);
    try {
      const commentData: any = {
        content: newComment,
        section_id: sectionId,
      };

      // Include text selection if available
      if (selectedText && selectionStart !== null && selectionEnd !== null) {
        commentData.selected_text = selectedText;
        commentData.selection_start = selectionStart;
        commentData.selection_end = selectionEnd;
      }

      const response = await fetch(
        `http://127.0.0.1:8000/api/v1/papers/${paperId}/comments`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
          },
          body: JSON.stringify(commentData),
        }
      );

      if (response.ok) {
        setNewComment('');
        setSelectedText('');
        setSelectionStart(null);
        setSelectionEnd(null);
        await fetchComments();
        onCommentAdded?.();
      }
    } catch (error) {
      console.error('Failed to add comment:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Resolve/unresolve comment
  const handleToggleResolve = async (commentId: string, isResolved: boolean) => {
    try {
      const response = await fetch(
        `http://127.0.0.1:8000/api/v1/papers/${paperId}/comments/${commentId}`,
        {
          method: 'PATCH',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
          },
          body: JSON.stringify({
            is_resolved: !isResolved,
          }),
        }
      );

      if (response.ok) {
        await fetchComments();
      }
    } catch (error) {
      console.error('Failed to toggle resolve:', error);
    }
  };

  // Delete comment
  const handleDeleteComment = async (commentId: string) => {
    if (!confirm('Are you sure you want to delete this comment?')) return;

    try {
      const response = await fetch(
        `http://127.0.0.1:8000/api/v1/papers/${paperId}/comments/${commentId}`,
        {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
          },
        }
      );

      if (response.ok) {
        await fetchComments();
      }
    } catch (error) {
      console.error('Failed to delete comment:', error);
    }
  };

  // Handle text selection (for commenting on specific text)
  const handleTextSelection = () => {
    const selection = window.getSelection();
    const text = selection?.toString().trim();

    if (text && text.length > 0) {
      setSelectedText(text);
      // Store approximate positions (simplified for now)
      setSelectionStart(0);
      setSelectionEnd(text.length);
      setShowComments(true); // Auto-open comments when text is selected
    }
  };

  // Listen for text selection
  useEffect(() => {
    document.addEventListener('mouseup', handleTextSelection);
    return () => {
      document.removeEventListener('mouseup', handleTextSelection);
    };
  }, []);

  // Format date
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`;
    return date.toLocaleDateString();
  };

  const unresolvedCount = comments.filter(c => !c.is_resolved).length;

  return (
    <div className="border-t border-gray-200 mt-4 pt-4">
      {/* Comments Header */}
      <div className="flex items-center justify-between mb-3">
        <button
          onClick={() => setShowComments(!showComments)}
          className="flex items-center gap-2 text-sm font-medium text-gray-700 hover:text-blue-600"
        >
          <MessageCircle size={16} />
          <span>
            Comments ({unresolvedCount})
            {unresolvedCount > 0 && <span className="ml-1 text-orange-600">●</span>}
          </span>
        </button>

        {showComments && (
          <label className="flex items-center gap-2 text-xs text-gray-600">
            <input
              type="checkbox"
              checked={includeResolved}
              onChange={(e) => setIncludeResolved(e.target.checked)}
              className="rounded"
            />
            Show resolved
          </label>
        )}
      </div>

      {/* Comments List */}
      {showComments && (
        <div className="space-y-3">
          {/* Selected Text Display */}
          {selectedText && (
            <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2 text-sm font-medium text-blue-900">
                  <Quote size={14} />
                  Selected text:
                </div>
                <button
                  onClick={() => {
                    setSelectedText('');
                    setSelectionStart(null);
                    setSelectionEnd(null);
                  }}
                  className="text-blue-600 hover:text-blue-800"
                  title="Clear selection"
                >
                  <X size={14} />
                </button>
              </div>
              <p className="text-sm text-gray-700 italic border-l-2 border-blue-400 pl-2">
                "{selectedText}"
              </p>
            </div>
          )}

          {/* New Comment Input */}
          <div className="flex gap-2">
            <textarea
              value={newComment}
              onChange={(e) => setNewComment(e.target.value)}
              placeholder={selectedText ? "Comment on selected text..." : "Add a comment..."}
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              rows={2}
            />
            <button
              onClick={handleAddComment}
              disabled={!newComment.trim() || isLoading}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-1"
            >
              <Send size={16} />
            </button>
          </div>

          {/* Comment Items */}
          <div className="space-y-2">
            {comments.length === 0 ? (
              <p className="text-sm text-gray-500 italic py-2">No comments yet</p>
            ) : (
              comments.map((comment) => (
                <div
                  key={comment.id}
                  className={`p-3 rounded-lg border ${
                    comment.is_resolved
                      ? 'bg-gray-50 border-gray-200'
                      : 'bg-white border-blue-200'
                  }`}
                >
                  {/* Comment Header */}
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <div className="w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-xs font-semibold">
                        {comment.author?.name?.[0]?.toUpperCase() || <User size={14} />}
                      </div>
                      <div>
                        <div className="text-sm font-medium text-gray-900">
                          {comment.author?.name || 'Unknown'}
                        </div>
                        <div className="text-xs text-gray-500">
                          {formatDate(comment.created_at)}
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-1">
                      {/* Resolve/Unresolve Button */}
                      <button
                        onClick={() => handleToggleResolve(comment.id, comment.is_resolved)}
                        className={`p-1 rounded hover:bg-gray-200 ${
                          comment.is_resolved ? 'text-green-600' : 'text-gray-400'
                        }`}
                        title={comment.is_resolved ? 'Unresolve' : 'Resolve'}
                      >
                        <Check size={16} />
                      </button>

                      {/* Delete Button (only for comment author) */}
                      {comment.author?.id === currentUserId && (
                        <button
                          onClick={() => handleDeleteComment(comment.id)}
                          className="p-1 rounded hover:bg-red-100 text-red-600"
                          title="Delete"
                        >
                          <Trash2 size={16} />
                        </button>
                      )}
                    </div>
                  </div>

                  {/* Selected Text Quote (if exists) */}
                  {comment.selected_text && (
                    <div className="mb-2 p-2 bg-gray-100 border-l-2 border-gray-400 rounded">
                      <div className="flex items-center gap-1 text-xs text-gray-600 mb-1">
                        <Quote size={12} />
                        <span>Commented on:</span>
                      </div>
                      <p className="text-xs text-gray-600 italic">
                        "{comment.selected_text}"
                      </p>
                    </div>
                  )}

                  {/* Comment Content */}
                  <p className="text-sm text-gray-700 whitespace-pre-wrap">
                    {comment.content}
                  </p>

                  {/* Resolved Badge */}
                  {comment.is_resolved && comment.resolved_by && (
                    <div className="mt-2 text-xs text-green-600 flex items-center gap-1">
                      <Check size={12} />
                      Resolved by {comment.resolved_by.name}
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default CommentSection;
