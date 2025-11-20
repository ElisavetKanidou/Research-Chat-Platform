// components/CollaboratorsList.tsx - FINAL FIXED
import React, { useState, useEffect } from 'react';
import { Users, Mail, MoreVertical, Trash2, Edit } from 'lucide-react';
import { useGlobalContext } from '../contexts/GlobalContext';

interface Collaborator {
  id: string;
  name: string;
  email: string;
  role: 'viewer' | 'editor' | 'co-author' | 'owner';
  avatar?: string;
  status: 'active' | 'pending' | 'inactive';
  joinedAt?: string;
}

interface CollaboratorsListProps {
  paperId?: string;
  compact?: boolean;
}

const CollaboratorsList: React.FC<CollaboratorsListProps> = ({ paperId, compact = false }) => {
  const { addNotification } = useGlobalContext();
  const [collaborators, setCollaborators] = useState<Collaborator[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCollaborator, setSelectedCollaborator] = useState<string | null>(null);

  useEffect(() => {
    fetchCollaborators();
  }, [paperId]);

  const fetchCollaborators = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('auth_token');
      
      // ✅ If no paperId, fetch ALL collaborators across all papers
      const url = paperId 
        ? `http://127.0.0.1:8000/api/v1/collaborations/paper/${paperId}`
        : `http://127.0.0.1:8000/api/v1/collaborations/all`;
      
      console.log('🤝 Fetching collaborators from:', url);
      
      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        console.log('✅ Collaborators data:', data);
        setCollaborators(data.collaborators || []);
      } else {
        console.error('❌ Failed to fetch collaborators:', response.status);
      }
    } catch (error) {
      console.error('💥 Error fetching collaborators:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRemoveCollaborator = async (collaboratorId: string) => {
    if (!confirm('Are you sure you want to remove this collaborator?')) return;

    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(
        `http://127.0.0.1:8000/api/v1/collaborations/${collaboratorId}`,
        {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      if (response.ok) {
        setCollaborators(collaborators.filter(c => c.id !== collaboratorId));
        addNotification({
          type: 'success',
          title: 'Collaborator Removed',
          message: 'Collaborator has been removed successfully',
          autoRemove: true,
        });
      }
    } catch (error) {
      console.error('Error removing collaborator:', error);
      addNotification({
        type: 'error',
        title: 'Failed to Remove',
        message: 'Could not remove collaborator. Please try again.',
      });
    }
  };

  const getRoleBadgeColor = (role: string) => {
    switch (role) {
      case 'owner': return 'bg-purple-100 text-purple-700';
      case 'co-author': return 'bg-blue-100 text-blue-700';
      case 'editor': return 'bg-green-100 text-green-700';
      case 'viewer': return 'bg-gray-100 text-gray-700';
      default: return 'bg-gray-100 text-gray-700';
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'active': return <span className="text-green-600">●</span>;
      case 'pending': return <span className="text-yellow-600">●</span>;
      case 'inactive': return <span className="text-gray-400">●</span>;
      default: return null;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-2 border-blue-600 border-t-transparent" />
      </div>
    );
  }

  if (collaborators.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <Users size={32} className="mx-auto mb-2 opacity-50" />
        <p className="text-sm">No collaborators yet</p>
        <p className="text-xs mt-1">Invite people to collaborate on your research</p>
      </div>
    );
  }

  if (compact) {
    // Compact view for Dashboard/Analytics
    return (
      <div className="space-y-2">
        {collaborators.slice(0, 5).map((collab) => (
          <div key={collab.id} className="flex items-center justify-between p-2 hover:bg-gray-50 rounded-lg transition-colors">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-400 to-purple-500 flex items-center justify-center text-white text-sm font-medium">
                {collab.name.charAt(0).toUpperCase()}
              </div>
              <div className="min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">{collab.name}</p>
                <p className="text-xs text-gray-500 truncate">{collab.email}</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              {getStatusBadge(collab.status)}
              <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${getRoleBadgeColor(collab.role)}`}>
                {collab.role}
              </span>
            </div>
          </div>
        ))}
        {collaborators.length > 5 && (
          <p className="text-xs text-gray-500 text-center pt-2">
            +{collaborators.length - 5} more collaborators
          </p>
        )}
      </div>
    );
  }

  // Full view
  return (
    <div className="space-y-3">
      {collaborators.map((collab) => (
        <div
          key={collab.id}
          className="bg-white border rounded-lg p-4 hover:shadow-md transition-shadow"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              {/* Avatar */}
              <div className="w-12 h-12 rounded-full bg-gradient-to-br from-blue-400 to-purple-500 flex items-center justify-center text-white text-lg font-medium">
                {collab.name.charAt(0).toUpperCase()}
              </div>

              {/* Info */}
              <div>
                <div className="flex items-center gap-2">
                  <p className="font-medium text-gray-900">{collab.name}</p>
                  {getStatusBadge(collab.status)}
                  {collab.status === 'pending' && (
                    <span className="text-xs text-yellow-600">(Pending)</span>
                  )}
                </div>
                <div className="flex items-center gap-2 mt-1">
                  <Mail size={12} className="text-gray-400" />
                  <p className="text-sm text-gray-600">{collab.email}</p>
                </div>
                {collab.joinedAt && (
                  <p className="text-xs text-gray-500 mt-1">
                    Joined {new Date(collab.joinedAt).toLocaleDateString()}
                  </p>
                )}
              </div>
            </div>

            {/* Actions */}
            <div className="flex items-center gap-2">
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${getRoleBadgeColor(collab.role)}`}>
                {collab.role}
              </span>
              
              {collab.role !== 'owner' && (
                <div className="relative">
                  <button
                    onClick={() => setSelectedCollaborator(
                      selectedCollaborator === collab.id ? null : collab.id
                    )}
                    className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                  >
                    <MoreVertical size={16} className="text-gray-500" />
                  </button>

                  {selectedCollaborator === collab.id && (
                    <div className="absolute right-0 mt-1 w-48 bg-white border rounded-lg shadow-lg z-10">
                      <button
                        onClick={() => {
                          // Handle role change
                          setSelectedCollaborator(null);
                        }}
                        className="w-full text-left px-4 py-2 text-sm hover:bg-gray-50 flex items-center gap-2"
                      >
                        <Edit size={14} />
                        Change Role
                      </button>
                      <button
                        onClick={() => {
                          handleRemoveCollaborator(collab.id);
                          setSelectedCollaborator(null);
                        }}
                        className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 flex items-center gap-2 border-t"
                      >
                        <Trash2 size={14} />
                        Remove Access
                      </button>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default CollaboratorsList;