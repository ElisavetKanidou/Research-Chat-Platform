// constants/statusOptions.ts - COMPLETE FILE
export const PAPER_STATUSES = [
  { 
    value: 'draft', 
    label: 'Draft', 
    description: 'Initial draft in progress',
    color: 'gray',
    bgColor: 'bg-gray-100',
    textColor: 'text-gray-700',
    progress: 10,
    icon: '📝',
    nextStatuses: ['in-progress']
  },
  { 
    value: 'in-progress', 
    label: 'In Progress', 
    description: 'Actively being worked on',
    color: 'blue',
    bgColor: 'bg-blue-100',
    textColor: 'text-blue-700',
    progress: 50,
    icon: '⏳',
    nextStatuses: ['in-review', 'completed']
  },
  { 
    value: 'in-review', 
    label: 'In Review', 
    description: 'Under review by peers or supervisors',
    color: 'yellow',
    bgColor: 'bg-yellow-100',
    textColor: 'text-yellow-700',
    progress: 80,
    icon: '👁️',
    nextStatuses: ['revision', 'completed']
  },
  { 
    value: 'revision', 
    label: 'Needs Revision', 
    description: 'Requires changes based on feedback',
    color: 'orange',
    bgColor: 'bg-orange-100',
    textColor: 'text-orange-700',
    progress: 70,
    icon: '✏️',
    nextStatuses: ['in-progress', 'in-review']
  },
  { 
    value: 'completed', 
    label: 'Completed', 
    description: 'Writing completed, ready for submission',
    color: 'green',
    bgColor: 'bg-green-100',
    textColor: 'text-green-700',
    progress: 100,
    icon: '✅',
    nextStatuses: ['published', 'archived']
  },
  { 
    value: 'published', 
    label: 'Published', 
    description: 'Successfully published or submitted',
    color: 'purple',
    bgColor: 'bg-purple-100',
    textColor: 'text-purple-700',
    progress: 100,
    icon: '📚',
    nextStatuses: ['archived']
  },
  { 
    value: 'archived', 
    label: 'Archived', 
    description: 'Moved to archive for long-term storage',
    color: 'gray',
    bgColor: 'bg-gray-100',
    textColor: 'text-gray-500',
    progress: 100,
    icon: '📦',
    nextStatuses: []
  },
] as const;

export const SECTION_STATUSES = [
  { 
    value: 'not-started', 
    label: 'Not Started', 
    description: 'Section has not been worked on yet',
    color: 'gray',
    bgColor: 'bg-gray-100',
    textColor: 'text-gray-600',
    progress: 0,
    icon: '○',
    nextStatuses: ['in-progress']
  },
  { 
    value: 'in-progress', 
    label: 'In Progress', 
    description: 'Currently being written or edited',
    color: 'blue',
    bgColor: 'bg-blue-100',
    textColor: 'text-blue-700',
    progress: 50,
    icon: '⏳',
    nextStatuses: ['completed', 'needs-review']
  },
  { 
    value: 'completed', 
    label: 'Completed', 
    description: 'Section is finished and ready',
    color: 'green',
    bgColor: 'bg-green-100',
    textColor: 'text-green-700',
    progress: 100,
    icon: '✓',
    nextStatuses: ['needs-review', 'in-progress']
  },
  { 
    value: 'needs-review', 
    label: 'Needs Review', 
    description: 'Requires feedback or revision',
    color: 'orange',
    bgColor: 'bg-orange-100',
    textColor: 'text-orange-700',
    progress: 80,
    icon: '⚠️',
    nextStatuses: ['in-progress', 'completed']
  },
] as const;

export const TASK_PRIORITIES = [
  { 
    value: 'high', 
    label: 'High Priority', 
    description: 'Urgent and important task',
    color: 'red',
    bgColor: 'bg-red-100',
    textColor: 'text-red-700',
    weight: 3,
    icon: '🔥',
    urgencyLevel: 'critical'
  },
  { 
    value: 'medium', 
    label: 'Medium Priority', 
    description: 'Important but not urgent',
    color: 'yellow',
    bgColor: 'bg-yellow-100',
    textColor: 'text-yellow-700',
    weight: 2,
    icon: '⚡',
    urgencyLevel: 'moderate'
  },
  { 
    value: 'low', 
    label: 'Low Priority', 
    description: 'Nice to have, when time permits',
    color: 'green',
    bgColor: 'bg-green-100',
    textColor: 'text-green-700',
    weight: 1,
    icon: '📋',
    urgencyLevel: 'low'
  },
] as const;

export const TASK_STATUSES = [
  { 
    value: 'pending', 
    label: 'Pending', 
    description: 'Task is waiting to be started',
    color: 'gray',
    bgColor: 'bg-gray-100',
    textColor: 'text-gray-600',
    progress: 0,
    icon: '⏸️',
    nextStatuses: ['in-progress']
  },
  { 
    value: 'in-progress', 
    label: 'In Progress', 
    description: 'Task is currently being worked on',
    color: 'blue',
    bgColor: 'bg-blue-100',
    textColor: 'text-blue-700',
    progress: 50,
    icon: '⏳',
    nextStatuses: ['completed', 'blocked', 'pending']
  },
  { 
    value: 'completed', 
    label: 'Completed', 
    description: 'Task has been finished successfully',
    color: 'green',
    bgColor: 'bg-green-100',
    textColor: 'text-green-700',
    progress: 100,
    icon: '✅',
    nextStatuses: ['in-progress']
  },
  { 
    value: 'blocked', 
    label: 'Blocked', 
    description: 'Task cannot proceed due to dependencies',
    color: 'red',
    bgColor: 'bg-red-100',
    textColor: 'text-red-700',
    progress: 0,
    icon: '🚫',
    nextStatuses: ['in-progress', 'pending']
  },
  { 
    value: 'cancelled', 
    label: 'Cancelled', 
    description: 'Task has been cancelled and will not be completed',
    color: 'gray',
    bgColor: 'bg-gray-100',
    textColor: 'text-gray-500',
    progress: 0,
    icon: '❌',
    nextStatuses: ['pending']
  },
] as const;

export const COLLABORATION_ROLES = [
  { 
    value: 'owner', 
    label: 'Owner', 
    description: 'Full control over the paper',
    permissions: ['read', 'write', 'delete', 'invite', 'manage'],
    icon: '👑',
    color: 'purple'
  },
  { 
    value: 'co-author', 
    label: 'Co-author', 
    description: 'Can edit content and invite others',
    permissions: ['read', 'write', 'invite'],
    icon: '✍️',
    color: 'blue'
  },
  { 
    value: 'editor', 
    label: 'Editor', 
    description: 'Can edit content but not invite others',
    permissions: ['read', 'write'],
    icon: '✏️',
    color: 'green'
  },
  { 
    value: 'reviewer', 
    label: 'Reviewer', 
    description: 'Can view and comment on content',
    permissions: ['read', 'comment'],
    icon: '👁️',
    color: 'yellow'
  },
  { 
    value: 'viewer', 
    label: 'Viewer', 
    description: 'Can only view the paper',
    permissions: ['read'],
    icon: '👀',
    color: 'gray'
  },
] as const;

// Helper functions
export const getStatusByValue = (statuses: readonly any[], value: string) => {
  return statuses.find(status => status.value === value);
};

export const getNextStatuses = (statuses: readonly any[], currentValue: string) => {
  const current = getStatusByValue(statuses, currentValue);
  return current?.nextStatuses || [];
};

export const canTransitionTo = (statuses: readonly any[], from: string, to: string): boolean => {
  const nextStatuses = getNextStatuses(statuses, from);
  return nextStatuses.includes(to);
};

export const getStatusColor = (statusValue: string, statusType: 'paper' | 'section' | 'task' | 'priority' = 'paper') => {
  let statuses;
  switch (statusType) {
    case 'section':
      statuses = SECTION_STATUSES;
      break;
    case 'task':
      statuses = TASK_STATUSES;
      break;
    case 'priority':
      statuses = TASK_PRIORITIES;
      break;
    default:
      statuses = PAPER_STATUSES;
  }
  
  const status = getStatusByValue(statuses, statusValue);
  return status ? `${status.bgColor} ${status.textColor}` : 'bg-gray-100 text-gray-600';
};

export const getStatusIcon = (statusValue: string, statusType: 'paper' | 'section' | 'task' = 'paper') => {
  let statuses;
  switch (statusType) {
    case 'section':
      statuses = SECTION_STATUSES;
      break;
    case 'task':
      statuses = TASK_STATUSES;
      break;
    default:
      statuses = PAPER_STATUSES;
  }
  
  const status = getStatusByValue(statuses, statusValue);
  return status?.icon || '📄';
};

export const formatStatusLabel = (statusValue: string) => {
  return statusValue
    .split('-')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
};

// Type exports
export type PaperStatus = typeof PAPER_STATUSES[number]['value'];
export type SectionStatus = typeof SECTION_STATUSES[number]['value'];
export type TaskPriority = typeof TASK_PRIORITIES[number]['value'];
export type TaskStatus = typeof TASK_STATUSES[number]['value'];
export type CollaborationRole = typeof COLLABORATION_ROLES[number]['value'];