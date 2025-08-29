// utils/statusHelpers.ts
export const getStatusColor = (status: string): string => {
  const colors = {
    'draft': 'bg-gray-100 text-gray-700',
    'in-progress': 'bg-blue-100 text-blue-700',
    'in-review': 'bg-yellow-100 text-yellow-700',
    'revision': 'bg-orange-100 text-orange-700',
    'completed': 'bg-green-100 text-green-700',
    'published': 'bg-purple-100 text-purple-700',
    'archived': 'bg-gray-100 text-gray-500',
    'not-started': 'bg-gray-100 text-gray-600',
    'needs-review': 'bg-orange-100 text-orange-700',
    'pending': 'bg-gray-100 text-gray-600',
    'overdue': 'bg-red-100 text-red-700',
    'upcoming': 'bg-blue-100 text-blue-700',
    'high': 'bg-red-100 text-red-700',
    'medium': 'bg-yellow-100 text-yellow-700',
    'low': 'bg-green-100 text-green-700',
  };
  return colors[status as keyof typeof colors] || 'bg-gray-100 text-gray-600';
};

export const getStatusIcon = (status: string): string => {
  const icons = {
    'draft': '📝',
    'in-progress': '⏳',
    'in-review': '👁️',
    'revision': '✏️',
    'completed': '✅',
    'published': '📚',
    'archived': '📦',
    'not-started': '○',
    'needs-review': '⚠️',
    'pending': '⏸️',
    'overdue': '🚨',
    'upcoming': '📅',
    'high': '🔥',
    'medium': '⚡',
    'low': '📋',
  };
  return icons[status as keyof typeof icons] || '📄';
};

export const formatStatus = (status: string): string => {
  return status.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase());
};

export const getStatusProgress = (status: string): number => {
  const progressMap = {
    'not-started': 0,
    'draft': 10,
    'in-progress': 50,
    'in-review': 80,
    'revision': 70,
    'completed': 100,
    'published': 100,
    'archived': 100,
  };
  return progressMap[status as keyof typeof progressMap] || 0;
};

export const getNextStatus = (currentStatus: string): string[] => {
  const statusFlow = {
    'draft': ['in-progress'],
    'in-progress': ['in-review', 'completed'],
    'in-review': ['revision', 'completed'],
    'revision': ['in-review', 'completed'],
    'completed': ['published', 'archived'],
    'published': ['archived'],
  };
  return statusFlow[currentStatus as keyof typeof statusFlow] || [];
};

export const canTransitionTo = (from: string, to: string): boolean => {
  const allowedTransitions = getNextStatus(from);
  return allowedTransitions.includes(to);
};

export const getStatusWeight = (status: string): number => {
  const weights = {
    'not-started': 0,
    'draft': 1,
    'in-progress': 2,
    'in-review': 3,
    'revision': 3,
    'completed': 4,
    'published': 5,
    'archived': 6,
  };
  return weights[status as keyof typeof weights] || 0;
};