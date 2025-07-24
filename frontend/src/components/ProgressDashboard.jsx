import React from 'react'
import { VictoryChart, VictoryLine, VictoryAxis, VictoryLabel } from 'victory'
import { Clock, Zap, Target, TrendingDown } from 'lucide-react'

const ProgressDashboard = ({ trainingStatus, onTrainingComplete }) => {
  if (!trainingStatus?.is_training && !trainingStatus?.progress) {
    return (
      <div className="bg-white rounded-lg p-6 shadow-sm border">
        <div className="text-center text-gray-500">
          <p>No training in progress</p>
        </div>
      </div>
    )
  }

  const progress = trainingStatus.progress || {}
  const isCompleted = !trainingStatus.is_training && progress.completed
  
  // Mock loss data for visualization
  const lossData = progress.recent_logs || [
    { step: 0, loss: 3.2 },
    { step: 10, loss: 2.8 },
    { step: 20, loss: 2.4 },
    { step: 30, loss: 2.1 },
    { step: 40, loss: 1.9 }
  ]

  const formatTime = (minutes) => {
    if (minutes < 1) return `${Math.round(minutes * 60)}s`
    if (minutes < 60) return `${Math.round(minutes)}m`
    return `${Math.round(minutes / 60)}h ${Math.round(minutes % 60)}m`
  }

  const progressPercent = Math.round(progress.progress_percent || 0)
  const currentEpoch = progress.current_epoch || 0
  const totalEpochs = progress.total_epochs || 1
  const currentStep = progress.current_step || 0
  const totalSteps = progress.total_steps || 100

  React.useEffect(() => {
    if (isCompleted && onTrainingComplete) {
      onTrainingComplete()
    }
  }, [isCompleted, onTrainingComplete])

  return (
    <div className="space-y-6">
      {/* Status Header */}
      <div className="bg-white rounded-lg p-6 shadow-sm border">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold">
            {isCompleted ? 'Training Completed!' : 'Training in Progress'}
          </h2>
          <div className={`px-3 py-1 rounded-full text-sm font-medium ${
            isCompleted ? 'bg-green-100 text-green-800' : 'bg-blue-100 text-blue-800'
          }`}>
            {isCompleted ? 'Completed' : 'Running'}
          </div>
        </div>

        {/* Progress Bar */}
        <div className="mb-6">
          <div className="flex justify-between text-sm text-gray-600 mb-2">
            <span>Overall Progress</span>
            <span>{progressPercent}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${progressPercent}%` }}
            />
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="flex items-center justify-center w-8 h-8 bg-blue-100 rounded-full mx-auto mb-2">
              <Target className="w-4 h-4 text-blue-600" />
            </div>
            <div className="text-2xl font-bold text-gray-900">{currentEpoch}</div>
            <div className="text-xs text-gray-500">Epoch {currentEpoch}/{totalEpochs}</div>
          </div>
          
          <div className="text-center">
            <div className="flex items-center justify-center w-8 h-8 bg-green-100 rounded-full mx-auto mb-2">
              <Zap className="w-4 h-4 text-green-600" />
            </div>
            <div className="text-2xl font-bold text-gray-900">{currentStep}</div>
            <div className="text-xs text-gray-500">Steps {currentStep}/{totalSteps}</div>
          </div>
          
          <div className="text-center">
            <div className="flex items-center justify-center w-8 h-8 bg-purple-100 rounded-full mx-auto mb-2">
              <TrendingDown className="w-4 h-4 text-purple-600" />
            </div>
            <div className="text-2xl font-bold text-gray-900">
              {lossData.length > 0 ? lossData[lossData.length - 1].loss.toFixed(2) : '0.00'}
            </div>
            <div className="text-xs text-gray-500">Current Loss</div>
          </div>
          
          <div className="text-center">
            <div className="flex items-center justify-center w-8 h-8 bg-orange-100 rounded-full mx-auto mb-2">
              <Clock className="w-4 h-4 text-orange-600" />
            </div>
            <div className="text-2xl font-bold text-gray-900">
              {progress.eta_minutes ? formatTime(progress.eta_minutes) : '--'}
            </div>
            <div className="text-xs text-gray-500">ETA</div>
          </div>
        </div>
      </div>

      {/* Loss Chart */}
      <div className="bg-white rounded-lg p-6 shadow-sm border">
        <h3 className="text-lg font-medium mb-4">Training Loss</h3>
        
        {lossData.length > 0 ? (
          <div className="h-64">
            <VictoryChart
              width={600}
              height={250}
              padding={{ left: 70, top: 20, right: 50, bottom: 50 }}
            >
              <VictoryAxis dependentAxis />
              <VictoryAxis />
              <VictoryLine
                data={lossData}
                x="step"
                y="loss"
                style={{
                  data: { stroke: "#3b82f6", strokeWidth: 2 }
                }}
                animate={{
                  duration: 1000,
                  onLoad: { duration: 500 }
                }}
              />
            </VictoryChart>
          </div>
        ) : (
          <div className="h-64 flex items-center justify-center text-gray-500">
            Waiting for training data...
          </div>
        )}
      </div>

      {/* Training Logs */}
      <div className="bg-white rounded-lg p-6 shadow-sm border">
        <h3 className="text-lg font-medium mb-4">Training Logs</h3>
        <div className="bg-gray-900 text-green-400 p-4 rounded-lg font-mono text-sm max-h-48 overflow-y-auto">
          {trainingStatus.is_training ? (
            <div className="space-y-1">
              <div>[INFO] Training started for project: {trainingStatus.project}</div>
              <div>[INFO] Model size: {progress.model_size || 'unknown'}</div>
              <div>[INFO] Current epoch: {currentEpoch}/{totalEpochs}</div>
              <div>[INFO] Current step: {currentStep}/{totalSteps}</div>
              <div>[INFO] Progress: {progressPercent}%</div>
              {progress.eta_minutes && (
                <div>[INFO] Estimated time remaining: {formatTime(progress.eta_minutes)}</div>
              )}
              <div className="animate-pulse">[INFO] Training in progress...</div>
            </div>
          ) : isCompleted ? (
            <div className="space-y-1">
              <div>[INFO] Training completed successfully!</div>
              <div>[INFO] Model saved to checkpoint</div>
              <div>[INFO] Ready for inference</div>
              <div className="text-blue-400">[INFO] You can now chat with your model</div>
            </div>
          ) : (
            <div>[INFO] Waiting for training to start...</div>
          )}
        </div>
      </div>

      {isCompleted && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <h4 className="font-medium text-green-800 mb-2">Training Complete!</h4>
          <p className="text-green-700 text-sm">
            Your model has been successfully trained and saved. You can now switch to the Chat tab to start conversing with your custom LLM.
          </p>
        </div>
      )}
    </div>
  )
}

export default ProgressDashboard