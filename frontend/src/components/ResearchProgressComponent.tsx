import React, { useState } from 'react';
import { BarChart, TrendingUp, Clock, Target, CheckCircle, AlertCircle, BookOpen, Users, Calendar, Download, FileText } from 'lucide-react';

interface ResearchPhase {
  id: string;
  name: string;
  status: 'completed' | 'in-progress' | 'pending' | 'overdue';
  progress: number;
  startDate: Date;
  dueDate: Date;
  estimatedHours: number;
  actualHours: number;
  tasks: Task[];
}

interface Task {
  id: string;
  name: string;
  status: 'completed' | 'in-progress' | 'pending';
  priority: 'high' | 'medium' | 'low';
  dueDate: Date;
  assignee?: string;
  notes?: string;
}

interface Milestone {
  id: string;
  title: string;
  date: Date;
  status: 'completed' | 'upcoming' | 'overdue';
  description: string;
}

interface ResearchMetrics {
  papersReviewed: number;
  referencesCollected: number;
  experimentsCompleted: number;
  dataPointsGathered: number;
  collaborations: number;
  presentationsMade: number;
}

const ResearchProgressComponent = () => {
  const [activeTab, setActiveTab] = useState<'overview' | 'phases' | 'tasks' | 'metrics'>('overview');
  
  // Sample data - in a real app, this would come from your backend
  const [researchPhases] = useState<ResearchPhase[]>([
    {
      id: '1',
      name: 'Literature Review',
      status: 'completed',
      progress: 100,
      startDate: new Date('2024-01-15'),
      dueDate: new Date('2024-02-28'),
      estimatedHours: 80,
      actualHours: 85,
      tasks: [
        { id: '1', name: 'Systematic review of AI papers', status: 'completed', priority: 'high', dueDate: new Date('2024-02-15') },
        { id: '2', name: 'Analysis of methodology trends', status: 'completed', priority: 'medium', dueDate: new Date('2024-02-28') }
      ]
    },
    {
      id: '2',
      name: 'Hypothesis Formation',
      status: 'completed',
      progress: 100,
      startDate: new Date('2024-02-20'),
      dueDate: new Date('2024-03-15'),
      estimatedHours: 40,
      actualHours: 45,
      tasks: [
        { id: '3', name: 'Define research questions', status: 'completed', priority: 'high', dueDate: new Date('2024-03-01') },
        { id: '4', name: 'Formulate testable hypotheses', status: 'completed', priority: 'high', dueDate: new Date('2024-03-15') }
      ]
    },
    {
      id: '3',
      name: 'Methodology Design',
      status: 'in-progress',
      progress: 75,
      startDate: new Date('2024-03-10'),
      dueDate: new Date('2024-04-30'),
      estimatedHours: 120,
      actualHours: 90,
      tasks: [
        { id: '5', name: 'Design experimental framework', status: 'completed', priority: 'high', dueDate: new Date('2024-04-01') },
        { id: '6', name: 'Prepare data collection protocols', status: 'in-progress', priority: 'high', dueDate: new Date('2024-04-30') },
        { id: '7', name: 'Ethics approval submission', status: 'pending', priority: 'medium', dueDate: new Date('2024-04-15') }
      ]
    },
    {
      id: '4',
      name: 'Data Collection',
      status: 'pending',
      progress: 0,
      startDate: new Date('2024-05-01'),
      dueDate: new Date('2024-07-31'),
      estimatedHours: 200,
      actualHours: 0,
      tasks: [
        { id: '8', name: 'Conduct experiments', status: 'pending', priority: 'high', dueDate: new Date('2024-07-15') },
        { id: '9', name: 'Data validation and cleaning', status: 'pending', priority: 'medium', dueDate: new Date('2024-07-31') }
      ]
    },
    {
      id: '5',
      name: 'Analysis & Results',
      status: 'pending',
      progress: 0,
      startDate: new Date('2024-08-01'),
      dueDate: new Date('2024-10-31'),
      estimatedHours: 150,
      actualHours: 0,
      tasks: [
        { id: '10', name: 'Statistical analysis', status: 'pending', priority: 'high', dueDate: new Date('2024-09-30') },
        { id: '11', name: 'Results interpretation', status: 'pending', priority: 'high', dueDate: new Date('2024-10-31') }
      ]
    },
    {
      id: '6',
      name: 'Paper Writing',
      status: 'pending',
      progress: 0,
      startDate: new Date('2024-11-01'),
      dueDate: new Date('2024-12-31'),
      estimatedHours: 100,
      actualHours: 0,
      tasks: [
        { id: '12', name: 'Draft manuscript', status: 'pending', priority: 'high', dueDate: new Date('2024-12-15') },
        { id: '13', name: 'Peer review and revisions', status: 'pending', priority: 'medium', dueDate: new Date('2024-12-31') }
      ]
    }
  ]);

  const [milestones] = useState<Milestone[]>([
    { id: '1', title: 'Literature Review Complete', date: new Date('2024-02-28'), status: 'completed', description: 'Comprehensive review of 150+ papers completed' },
    { id: '2', title: 'Research Proposal Approved', date: new Date('2024-03-15'), status: 'completed', description: 'Thesis committee approved research proposal' },
    { id: '3', title: 'Ethics Approval Received', date: new Date('2024-04-30'), status: 'upcoming', description: 'IRB approval for human subjects research' },
    { id: '4', title: 'Data Collection Complete', date: new Date('2024-07-31'), status: 'upcoming', description: 'All experimental data collected and validated' },
    { id: '5', title: 'First Draft Submission', date: new Date('2024-12-31'), status: 'upcoming', description: 'Complete first draft of thesis submitted' }
  ]);

  const [metrics] = useState<ResearchMetrics>({
    papersReviewed: 187,
    referencesCollected: 342,
    experimentsCompleted: 24,
    dataPointsGathered: 15420,
    collaborations: 8,
    presentationsMade: 5
  });

  const getPhaseStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-700 border-green-200';
      case 'in-progress': return 'bg-blue-100 text-blue-700 border-blue-200';
      case 'pending': return 'bg-gray-100 text-gray-600 border-gray-200';
      case 'overdue': return 'bg-red-100 text-red-700 border-red-200';
      default: return 'bg-gray-100 text-gray-600 border-gray-200';
    }
  };

  const getTaskPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'bg-red-100 text-red-700';
      case 'medium': return 'bg-yellow-100 text-yellow-700';
      case 'low': return 'bg-green-100 text-green-700';
      default: return 'bg-gray-100 text-gray-600';
    }
  };

  const calculateOverallProgress = () => {
    const totalEstimatedHours = researchPhases.reduce((sum, phase) => sum + phase.estimatedHours, 0);
    const completedHours = researchPhases.reduce((sum, phase) => 
      sum + (phase.estimatedHours * phase.progress / 100), 0
    );
    return Math.round((completedHours / totalEstimatedHours) * 100);
  };

  const exportProgressReport = () => {
    console.log('Exporting progress report...');
    alert('Progress report exported successfully!');
  };

  const OverviewTab = () => (
    <div className="space-y-6">
      {/* Overall Progress */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-6 rounded-lg border">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-semibold text-gray-900">Overall Research Progress</h3>
          <span className="text-3xl font-bold text-blue-600">{calculateOverallProgress()}%</span>
        </div>
        <div className="w-full bg-white rounded-full h-4 mb-4">
          <div
            className="bg-gradient-to-r from-blue-500 to-indigo-600 h-4 rounded-full transition-all duration-500"
            style={{ width: `${calculateOverallProgress()}%` }}
          />
        </div>
        <div className="grid grid-cols-3 gap-4 text-center">
          <div>
            <div className="text-2xl font-bold text-green-600">
              {researchPhases.filter(p => p.status === 'completed').length}
            </div>
            <div className="text-sm text-gray-600">Phases Complete</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-blue-600">
              {researchPhases.filter(p => p.status === 'in-progress').length}
            </div>
            <div className="text-sm text-gray-600">In Progress</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-gray-600">
              {researchPhases.reduce((sum, phase) => sum + phase.actualHours, 0)}
            </div>
            <div className="text-sm text-gray-600">Hours Logged</div>
          </div>
        </div>
      </div>

      {/* Upcoming Milestones */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <Target size={18} />
          Upcoming Milestones
        </h3>
        <div className="space-y-3">
          {milestones.filter(m => m.status !== 'completed').slice(0, 3).map((milestone) => (
            <div key={milestone.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div>
                <h4 className="font-medium text-gray-900">{milestone.title}</h4>
                <p className="text-sm text-gray-600">{milestone.description}</p>
              </div>
              <div className="text-right">
                <div className="text-sm font-medium text-gray-900">
                  {milestone.date.toLocaleDateString()}
                </div>
                <div className="text-xs text-gray-500">
                  {Math.ceil((milestone.date.getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24))} days
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Current Tasks */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Current Priority Tasks</h3>
        <div className="space-y-2">
          {researchPhases
            .flatMap(phase => phase.tasks)
            .filter(task => task.status !== 'completed')
            .sort((a, b) => a.priority === 'high' ? -1 : b.priority === 'high' ? 1 : 0)
            .slice(0, 5)
            .map((task) => (
              <div key={task.id} className="flex items-center justify-between p-3 border rounded-lg">
                <div className="flex items-center gap-3">
                  <span className={`px-2 py-1 rounded-full text-xs ${getTaskPriorityColor(task.priority)}`}>
                    {task.priority}
                  </span>
                  <span className="font-medium">{task.name}</span>
                </div>
                <span className="text-sm text-gray-600">
                  Due: {task.dueDate.toLocaleDateString()}
                </span>
              </div>
            ))}
        </div>
      </div>
    </div>
  );

  const PhasesTab = () => (
    <div className="space-y-4">
      {researchPhases.map((phase) => (
        <div key={phase.id} className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-lg font-semibold text-gray-900">{phase.name}</h3>
              <p className="text-sm text-gray-600">
                {phase.startDate.toLocaleDateString()} - {phase.dueDate.toLocaleDateString()}
              </p>
            </div>
            <div className="text-right">
              <span className={`px-3 py-1 rounded-full text-sm border ${getPhaseStatusColor(phase.status)}`}>
                {phase.status.replace('-', ' ').toUpperCase()}
              </span>
              <div className="text-sm text-gray-600 mt-1">
                {phase.actualHours}h / {phase.estimatedHours}h
              </div>
            </div>
          </div>
          
          <div className="mb-4">
            <div className="flex justify-between text-sm text-gray-600 mb-1">
              <span>Progress</span>
              <span>{phase.progress}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${phase.progress}%` }}
              />
            </div>
          </div>

          <div className="space-y-2">
            <h4 className="font-medium text-gray-700">Tasks:</h4>
            {phase.tasks.map((task) => (
              <div key={task.id} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                <div className="flex items-center gap-2">
                  {task.status === 'completed' ? (
                    <CheckCircle size={16} className="text-green-600" />
                  ) : task.status === 'in-progress' ? (
                    <Clock size={16} className="text-blue-600" />
                  ) : (
                    <AlertCircle size={16} className="text-gray-400" />
                  )}
                  <span className={task.status === 'completed' ? 'line-through text-gray-500' : ''}>{task.name}</span>
                </div>
                <span className={`px-2 py-1 rounded text-xs ${getTaskPriorityColor(task.priority)}`}>
                  {task.priority}
                </span>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );

  const TasksTab = () => {
    const allTasks = researchPhases.flatMap(phase => 
      phase.tasks.map(task => ({ ...task, phaseName: phase.name }))
    );
    
    const pendingTasks = allTasks.filter(task => task.status !== 'completed');
    const completedTasks = allTasks.filter(task => task.status === 'completed');

    return (
      <div className="space-y-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Pending Tasks ({pendingTasks.length})</h3>
          <div className="space-y-3">
            {pendingTasks.map((task) => (
              <div key={task.id} className="flex items-center justify-between p-4 border rounded-lg">
                <div>
                  <h4 className="font-medium text-gray-900">{task.name}</h4>
                  <p className="text-sm text-gray-600">{task.phaseName}</p>
                </div>
                <div className="flex items-center gap-3">
                  <span className={`px-2 py-1 rounded-full text-xs ${getTaskPriorityColor(task.priority)}`}>
                    {task.priority}
                  </span>
                  <span className="text-sm text-gray-600">
                    Due: {task.dueDate.toLocaleDateString()}
                  </span>
                  <span className={`px-2 py-1 rounded text-xs ${
                    task.status === 'in-progress' ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-600'
                  }`}>
                    {task.status.replace('-', ' ')}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Completed Tasks ({completedTasks.length})</h3>
          <div className="space-y-2">
            {completedTasks.map((task) => (
              <div key={task.id} className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                <div className="flex items-center gap-2">
                  <CheckCircle size={16} className="text-green-600" />
                  <span className="line-through text-gray-600">{task.name}</span>
                  <span className="text-sm text-gray-500">({task.phaseName})</span>
                </div>
                <span className="text-sm text-green-600">Completed</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  };

  const MetricsTab = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border text-center">
          <BookOpen size={32} className="mx-auto text-blue-600 mb-3" />
          <div className="text-3xl font-bold text-gray-900">{metrics.papersReviewed}</div>
          <div className="text-sm text-gray-600">Papers Reviewed</div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border text-center">
          <FileText size={32} className="mx-auto text-green-600 mb-3" />
          <div className="text-3xl font-bold text-gray-900">{metrics.referencesCollected}</div>
          <div className="text-sm text-gray-600">References Collected</div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border text-center">
          <BarChart size={32} className="mx-auto text-purple-600 mb-3" />
          <div className="text-3xl font-bold text-gray-900">{metrics.experimentsCompleted}</div>
          <div className="text-sm text-gray-600">Experiments Completed</div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border text-center">
          <TrendingUp size={32} className="mx-auto text-orange-600 mb-3" />
          <div className="text-3xl font-bold text-gray-900">{metrics.dataPointsGathered.toLocaleString()}</div>
          <div className="text-sm text-gray-600">Data Points</div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border text-center">
          <Users size={32} className="mx-auto text-indigo-600 mb-3" />
          <div className="text-3xl font-bold text-gray-900">{metrics.collaborations}</div>
          <div className="text-sm text-gray-600">Collaborations</div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border text-center">
          <Calendar size={32} className="mx-auto text-red-600 mb-3" />
          <div className="text-3xl font-bold text-gray-900">{metrics.presentationsMade}</div>
          <div className="text-sm text-gray-600">Presentations Made</div>
        </div>
      </div>

      {/* Time Distribution Chart Placeholder */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Time Distribution by Phase</h3>
        <div className="space-y-3">
          {researchPhases.map((phase) => (
            <div key={phase.id}>
              <div className="flex justify-between text-sm text-gray-600 mb-1">
                <span>{phase.name}</span>
                <span>{phase.actualHours}h ({Math.round((phase.actualHours / researchPhases.reduce((sum, p) => sum + p.actualHours, 0)) * 100)}%)</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full"
                  style={{ 
                    width: `${(phase.actualHours / researchPhases.reduce((sum, p) => sum + p.actualHours, 0)) * 100}%` 
                  }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Weekly Progress Trend */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Research Activity Timeline</h3>
        <div className="text-center py-8 text-gray-500">
          <BarChart size={48} className="mx-auto mb-3 opacity-50" />
          <p>Interactive timeline chart would be displayed here</p>
          <p className="text-sm">Showing daily/weekly research activities and progress</p>
        </div>
      </div>
    </div>
  );

  return (
    <div className="space-y-6">
      {/* Header with Export Button */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Research Progress Dashboard</h2>
          <p className="text-gray-600">Track your research journey and milestones</p>
        </div>
        <button
          onClick={exportProgressReport}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          <Download size={18} />
          Export Report
        </button>
      </div>

      {/* Tab Navigation */}
      <div className="bg-white p-1 rounded-lg shadow-sm border">
        <div className="flex space-x-1">
          {[
            { id: 'overview', label: 'Overview', icon: BarChart },
            { id: 'phases', label: 'Research Phases', icon: Target },
            { id: 'tasks', label: 'Tasks', icon: CheckCircle },
            { id: 'metrics', label: 'Metrics', icon: TrendingUp }
          ].map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              onClick={() => setActiveTab(id as any)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors ${
                activeTab === id
                  ? 'bg-blue-100 text-blue-700'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
              }`}
            >
              <Icon size={18} />
              {label}
            </button>
          ))}
        </div>
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' && <OverviewTab />}
      {activeTab === 'phases' && <PhasesTab />}
      {activeTab === 'tasks' && <TasksTab />}
      {activeTab === 'metrics' && <MetricsTab />}
    </div>
  );
};

export default ResearchProgressComponent;