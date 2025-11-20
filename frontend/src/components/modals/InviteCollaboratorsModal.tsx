// components/modals/InviteCollaboratorsModal.tsx
import React, { useState } from 'react';
import { X, Mail, UserPlus, Check, AlertCircle } from 'lucide-react';
import { useGlobalContext } from '../../contexts/GlobalContext';

interface InviteCollaboratorsModalProps {
  isOpen: boolean;
  onClose: () => void;
  paperId?: string;
  paperTitle?: string;
}

interface InviteForm {
  email: string;
  role: 'viewer' | 'editor' | 'co-author';
  message: string;
}

const InviteCollaboratorsModal: React.FC<InviteCollaboratorsModalProps> = ({
  isOpen,
  onClose,
  paperId,
  paperTitle
}) => {
  const { addNotification } = useGlobalContext();
  const [invites, setInvites] = useState<InviteForm[]>([
    { email: '', role: 'editor', message: '' }
  ]);
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!isOpen) return null;

  const handleAddInvite = () => {
    setInvites([...invites, { email: '', role: 'editor', message: '' }]);
  };

  const handleRemoveInvite = (index: number) => {
    setInvites(invites.filter((_, i) => i !== index));
  };

  const handleInviteChange = (index: number, field: keyof InviteForm, value: string) => {
    const newInvites = [...invites];
    newInvites[index] = { ...newInvites[index], [field]: value };
    setInvites(newInvites);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate emails
    const validInvites = invites.filter(inv => inv.email.trim() !== '');
    if (validInvites.length === 0) {
      addNotification({
        type: 'error',
        title: 'No invites to send',
        message: 'Please add at least one email address',
      });
      return;
    }

    setIsSubmitting(true);

    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch('http://127.0.0.1:8000/api/v1/collaborations/invite', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          invites: validInvites,
          paper_id: paperId || null,
          paper_title: paperTitle || null
        })
      });

      if (!response.ok) {
        throw new Error('Failed to send invitations');
      }

      const data = await response.json();

      addNotification({
        type: 'success',
        title: 'Invitations Sent!',
        message: `Successfully sent ${validInvites.length} invitation${validInvites.length > 1 ? 's' : ''}`,
        autoRemove: true,
      });

      onClose();
      
    } catch (error) {
      console.error('Error sending invitations:', error);
      addNotification({
        type: 'error',
        title: 'Failed to Send Invitations',
        message: error instanceof Error ? error.message : 'Please try again',
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">Invite Collaborators</h2>
            {paperTitle && (
              <p className="text-sm text-gray-600 mt-1">For paper: {paperTitle}</p>
            )}
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X size={20} className="text-gray-500" />
          </button>
        </div>

        {/* Content */}
        <form onSubmit={handleSubmit} className="overflow-y-auto max-h-[calc(90vh-200px)]">
          <div className="p-6 space-y-4">
            {/* Info Box */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 flex gap-3">
              <AlertCircle size={20} className="text-blue-600 flex-shrink-0 mt-0.5" />
              <div className="text-sm text-blue-800">
                <p className="font-medium mb-1">How collaboration works:</p>
                <ul className="list-disc list-inside space-y-1 text-blue-700">
                  <li><strong>Viewer:</strong> Can read the paper and leave comments</li>
                  <li><strong>Editor:</strong> Can edit content and manage sections</li>
                  <li><strong>Co-author:</strong> Full access including paper settings</li>
                </ul>
              </div>
            </div>

            {/* Invite Forms */}
            <div className="space-y-4">
              {invites.map((invite, index) => (
                <div key={index} className="border rounded-lg p-4 space-y-3">
                  <div className="flex items-center justify-between">
                    <label className="text-sm font-medium text-gray-700">
                      Collaborator {index + 1}
                    </label>
                    {invites.length > 1 && (
                      <button
                        type="button"
                        onClick={() => handleRemoveInvite(index)}
                        className="text-red-600 hover:text-red-700 text-sm"
                      >
                        Remove
                      </button>
                    )}
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {/* Email */}
                    <div className="md:col-span-1">
                      <label className="block text-sm text-gray-600 mb-1">
                        Email Address *
                      </label>
                      <div className="relative">
                        <Mail size={16} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                        <input
                          type="email"
                          value={invite.email}
                          onChange={(e) => handleInviteChange(index, 'email', e.target.value)}
                          placeholder="colleague@university.edu"
                          className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                          required
                        />
                      </div>
                    </div>

                    {/* Role */}
                    <div>
                      <label className="block text-sm text-gray-600 mb-1">
                        Role *
                      </label>
                      <select
                        value={invite.role}
                        onChange={(e) => handleInviteChange(index, 'role', e.target.value as any)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      >
                        <option value="viewer">Viewer</option>
                        <option value="editor">Editor</option>
                        <option value="co-author">Co-author</option>
                      </select>
                    </div>
                  </div>

                  {/* Optional Message */}
                  <div>
                    <label className="block text-sm text-gray-600 mb-1">
                      Personal Message (Optional)
                    </label>
                    <textarea
                      value={invite.message}
                      onChange={(e) => handleInviteChange(index, 'message', e.target.value)}
                      placeholder="Add a personal note to your invitation..."
                      rows={2}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                    />
                  </div>
                </div>
              ))}
            </div>

            {/* Add Another Button */}
            <button
              type="button"
              onClick={handleAddInvite}
              className="w-full py-2 border-2 border-dashed border-gray-300 rounded-lg text-gray-600 hover:border-blue-500 hover:text-blue-600 transition-colors flex items-center justify-center gap-2"
            >
              <UserPlus size={16} />
              <span>Add Another Collaborator</span>
            </button>
          </div>

          {/* Footer */}
          <div className="border-t p-6 bg-gray-50 flex items-center justify-between">
            <div className="text-sm text-gray-600">
              {invites.filter(inv => inv.email.trim()).length} invitation{invites.filter(inv => inv.email.trim()).length !== 1 ? 's' : ''} ready to send
            </div>
            <div className="flex gap-3">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
                disabled={isSubmitting}
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isSubmitting || invites.filter(inv => inv.email.trim()).length === 0}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
              >
                {isSubmitting ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent" />
                    <span>Sending...</span>
                  </>
                ) : (
                  <>
                    <Check size={16} />
                    <span>Send Invitations</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};

export default InviteCollaboratorsModal;