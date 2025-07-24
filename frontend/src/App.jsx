import React, { useState } from 'react'
import { useQuery } from 'react-query'
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs'
import DataUpload from './components/DataUpload'
import TrainingWizard from './components/TrainingWizard'
import ProgressDashboard from './components/ProgressDashboard'
import ChatInterface from './components/ChatInterface'
import ProjectSelector from './components/ProjectSelector'
import SystemMonitor from './components/SystemMonitor'

function App() {
  const [currentProject, setCurrentProject] = useState('')
  const [activeTab, setActiveTab] = useState('upload')
  const [isTraining, setIsTraining] = useState(false)

  const { data: systemInfo } = useQuery(
    'system-info',
    () => fetch('/api/system-info').then(res => res.json()),
    { refetchInterval: 5000 }
  )

  const { data: trainingStatus } = useQuery(
    'training-status',
    () => fetch('/api/training-status').then(res => res.json()),
    { 
      refetchInterval: isTraining ? 1000 : 5000,
      onSuccess: (data) => {
        setIsTraining(data.is_training)
        if (data.is_training === false && data.progress?.completed) {
          setActiveTab('chat')
        }
      }
    }
  )

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        <header className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Make Your Own LLM
          </h1>
          <p className="text-lg text-gray-600">
            Train and chat with your custom language model
          </p>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Main Content */}
          <div className="lg:col-span-3">
            <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
              <TabsList className="grid w-full grid-cols-4">
                <TabsTrigger value="upload">Upload Data</TabsTrigger>
                <TabsTrigger value="train">Train Model</TabsTrigger>
                <TabsTrigger value="progress" disabled={!isTraining}>
                  Progress
                </TabsTrigger>
                <TabsTrigger value="chat" disabled={!currentProject}>
                  Chat
                </TabsTrigger>
              </TabsList>

              <TabsContent value="upload" className="mt-6">
                <DataUpload 
                  currentProject={currentProject}
                  onProjectChange={setCurrentProject}
                  onDataUploaded={() => setActiveTab('train')}
                />
              </TabsContent>

              <TabsContent value="train" className="mt-6">
                <TrainingWizard
                  currentProject={currentProject}
                  onTrainingStarted={() => {
                    setIsTraining(true)
                    setActiveTab('progress')
                  }}
                />
              </TabsContent>

              <TabsContent value="progress" className="mt-6">
                <ProgressDashboard
                  trainingStatus={trainingStatus}
                  onTrainingComplete={() => setActiveTab('chat')}
                />
              </TabsContent>

              <TabsContent value="chat" className="mt-6">
                <ChatInterface currentProject={currentProject} />
              </TabsContent>
            </Tabs>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            <ProjectSelector
              currentProject={currentProject}
              onProjectChange={setCurrentProject}
            />
            
            <SystemMonitor systemInfo={systemInfo} />
            
            {trainingStatus?.is_training && (
              <div className="bg-white rounded-lg p-4 shadow-sm border">
                <h3 className="font-medium text-sm mb-2">Training Status</h3>
                <div className="text-xs text-gray-600">
                  <div>Project: {trainingStatus.project}</div>
                  <div>
                    Epoch: {trainingStatus.progress?.current_epoch || 0}/
                    {trainingStatus.progress?.total_epochs || 0}
                  </div>
                  <div>
                    Progress: {Math.round(trainingStatus.progress?.progress_percent || 0)}%
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default App