import React, { useMemo, useState } from 'react'
import { Play, Settings, Zap, Cpu, MonitorSmartphone } from 'lucide-react'

const MODEL_CONFIGS = {
  toy: {
    name: 'Toy Model',
    description: 'Tiny model for quick testing (~50M params)',
    icon: '🧸',
    estimatedTime: '1-2 minutes',
    memoryHint: '<4 GB VRAM'
  },
  base: {
    name: 'Base Model',
    description: 'Small but capable model (~150M params)',
    icon: '🚀',
    estimatedTime: '3-5 minutes',
    memoryHint: '~6 GB VRAM'
  },
  plus: {
    name: 'Plus Model',
    description: 'Larger model with better quality (~200M params)',
    icon: '⚡',
    estimatedTime: '8-12 minutes',
    memoryHint: '~8 GB VRAM'
  },
  '1b': {
    name: '1B Expert',
    description: '1B parameter class model for high quality outputs',
    icon: '🧠',
    estimatedTime: '20+ minutes',
    memoryHint: '≥12 GB VRAM (16 GB recommended)'
  }
}

const MODEL_ORDER = ['toy', 'base', 'plus', '1b']

const HARDWARE_OPTIONS = [
  {
    value: 'auto',
    label: 'Auto Detect',
    description: 'Let the trainer pick the best accelerator for you.',
    icon: '🤖'
  },
  {
    value: 'apple_silicon',
    label: 'Apple Silicon (MPS)',
    description: 'Optimised for M-series GPUs with Metal acceleration.',
    icon: '🍎'
  },
  {
    value: 'windows_nvidia',
    label: 'Windows + NVIDIA',
    description: 'Use CUDA acceleration on RTX/GTX GPUs.',
    icon: '🟩'
  },
  {
    value: 'cpu',
    label: 'CPU Only',
    description: 'Fallback mode if no accelerator is available.',
    icon: '🧮'
  }
]

const USE_CASES = {
  general: 'General conversation',
  storytelling: 'Creative storytelling',
  qa: 'Question answering',
  chat: 'Casual chat',
  assistant: 'Task assistance'
}

const TrainingWizard = ({ currentProject, onTrainingStarted, systemInfo }) => {
  const [config, setConfig] = useState({
    modelSize: 'toy',
    epochs: 1,
    learningRate: 5e-5,
    useCase: 'general',
    temperature: 0.7,
    hardwareProfile: 'auto'
  })
  const [isStarting, setIsStarting] = useState(false)
  const [showAdvanced, setShowAdvanced] = useState(false)

  const hardwareProfiles = systemInfo?.hardware_profiles || {}

  const selectedHardwareInfo = useMemo(() => {
    const selected = HARDWARE_OPTIONS.find(option => option.value === config.hardwareProfile)
    const availability = selected ? hardwareProfiles[selected.value] : undefined
    return {
      option: selected,
      available: availability ? availability.available : true,
      device: availability?.device,
      precision: systemInfo?.precision
    }
  }, [config.hardwareProfile, hardwareProfiles, systemInfo])

  const startTraining = async () => {
    if (!currentProject) {
      alert('Please select a project first')
      return
    }

    setIsStarting(true)

    try {
      const response = await fetch('/api/start-training', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          project_slug: currentProject,
          model_size: config.modelSize,
          epochs: config.epochs,
          learning_rate: config.learningRate,
          use_case: config.useCase,
          temperature: config.temperature,
          hardware_profile: config.hardwareProfile
        })
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Failed to start training')
      }

      onTrainingStarted()
    } catch (error) {
      console.error('Training start error:', error)
      alert('Failed to start training: ' + error.message)
    } finally {
      setIsStarting(false)
    }
  }

  const continueTraining = async () => {
    if (!currentProject) {
      alert('Please select a project first')
      return
    }

    setIsStarting(true)

    try {
      const response = await fetch('/api/continue-training', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          project_slug: currentProject,
          additional_epochs: 1,
          hardware_profile: config.hardwareProfile
        })
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Failed to continue training')
      }

      onTrainingStarted()
    } catch (error) {
      console.error('Continue training error:', error)
      alert('Failed to continue training: ' + error.message)
    } finally {
      setIsStarting(false)
    }
  }

  return (
    <div className="bg-white rounded-lg p-6 shadow-sm border">
      <h2 className="text-xl font-semibold mb-6">Training Configuration</h2>

      {!currentProject && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-md p-4 mb-6">
          <p className="text-yellow-800 text-sm">
            Please upload training data first to create a project.
          </p>
        </div>
      )}

      {/* Model Size Selection */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-3">
          Model Size
        </label>
        <div className="grid gap-3">
          {MODEL_ORDER.map((key) => {
            const modelConfig = MODEL_CONFIGS[key]
            const isSelected = config.modelSize === key
            return (
              <div
                key={key}
                onClick={() => setConfig(prev => ({ ...prev, modelSize: key }))}
                className={`
                  p-4 border rounded-lg cursor-pointer transition-colors
                  ${isSelected ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-gray-300'}
                `}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <span className="text-2xl mr-3">{modelConfig.icon}</span>
                    <div>
                      <h3 className="font-medium">{modelConfig.name}</h3>
                      <p className="text-sm text-gray-600">{modelConfig.description}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-xs text-gray-500">Est. training time</p>
                    <p className="text-sm font-medium">{modelConfig.estimatedTime}</p>
                    <p className="text-[11px] text-gray-400">{modelConfig.memoryHint}</p>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Hardware Profile */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-3">
          Hardware Profile
        </label>
        <div className="grid gap-3">
          {HARDWARE_OPTIONS.map(option => {
            const availability = hardwareProfiles[option.value]
            const isAvailable = availability ? availability.available : true
            const isActive = config.hardwareProfile === option.value
            return (
              <div
                key={option.value}
                onClick={() => setConfig(prev => ({ ...prev, hardwareProfile: option.value }))}
                className={`
                  p-4 border rounded-lg transition-all cursor-pointer
                  ${isActive ? 'border-indigo-500 bg-indigo-50 shadow-sm' : 'border-gray-200 hover:border-gray-300'}
                  ${!isAvailable && option.value !== 'cpu' ? 'opacity-60' : ''}
                `}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start">
                    <span className="text-2xl mr-3">{option.icon}</span>
                    <div>
                      <h3 className="font-medium text-sm">{option.label}</h3>
                      <p className="text-xs text-gray-600">{option.description}</p>
                    </div>
                  </div>
                  <div className="flex items-center text-xs text-gray-500">
                    {isAvailable ? (
                      <span className="flex items-center"><MonitorSmartphone className="w-3 h-3 mr-1" />Detected</span>
                    ) : (
                      <span className="flex items-center"><Cpu className="w-3 h-3 mr-1" />Fallback</span>
                    )}
                  </div>
                </div>
              </div>
            )
          })}
        </div>

        <div className="mt-3 text-xs text-gray-500">
          {selectedHardwareInfo.option && (
            <p>
              <span className="font-medium">Current selection:</span> {selectedHardwareInfo.option.label}
              {selectedHardwareInfo.device && ` • Target device: ${selectedHardwareInfo.device.toUpperCase()}`}
              {selectedHardwareInfo.precision && ` • Precision: ${selectedHardwareInfo.precision.toUpperCase()}`}
              {!selectedHardwareInfo.available && (
                <span className="text-yellow-600 ml-1">(will automatically fall back to the best available device)</span>
              )}
            </p>
          )}
        </div>
      </div>

      {/* Use Case */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Use Case
        </label>
        <select
          value={config.useCase}
          onChange={(e) => setConfig(prev => ({ ...prev, useCase: e.target.value }))}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          {Object.entries(USE_CASES).map(([key, label]) => (
            <option key={key} value={key}>{label}</option>
          ))}
        </select>
      </div>

      {/* Advanced Settings */}
      <div className="mb-6">
        <button
          className="flex items-center text-sm text-gray-600 hover:text-gray-800"
          onClick={() => setShowAdvanced(prev => !prev)}
          type="button"
        >
          <Settings className="w-4 h-4 mr-2" />
          Advanced Settings
          <span className="ml-2 text-[11px] text-gray-400">{showAdvanced ? '(hide)' : '(show)'}</span>
        </button>

        {showAdvanced && (
          <div className="mt-4 space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Epochs: {config.epochs}
              </label>
              <input
                type="range"
                min="1"
                max="5"
                value={config.epochs}
                onChange={(e) => setConfig(prev => ({ ...prev, epochs: parseInt(e.target.value) }))}
                className="w-full"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Temperature: {config.temperature.toFixed(1)}
              </label>
              <input
                type="range"
                min="0.1"
                max="1.0"
                step="0.1"
                value={config.temperature}
                onChange={(e) => setConfig(prev => ({ ...prev, temperature: parseFloat(e.target.value) }))}
                className="w-full"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Learning Rate
              </label>
              <select
                value={config.learningRate}
                onChange={(e) => setConfig(prev => ({ ...prev, learningRate: parseFloat(e.target.value) }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value={1e-5}>1e-5 (Conservative)</option>
                <option value={5e-5}>5e-5 (Recommended)</option>
                <option value={1e-4}>1e-4 (Aggressive)</option>
              </select>
            </div>
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <div className="flex gap-3">
        <button
          onClick={startTraining}
          disabled={isStarting || !currentProject}
          className="flex-1 bg-blue-600 text-white py-3 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
        >
          <Play className="w-4 h-4 mr-2" />
          {isStarting ? 'Starting...' : 'Start Training'}
        </button>

        <button
          onClick={continueTraining}
          disabled={isStarting || !currentProject}
          className="flex-1 bg-green-600 text-white py-3 px-4 rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
        >
          <Zap className="w-4 h-4 mr-2" />
          Continue Training (+1 epoch)
        </button>
      </div>

      {/* Training Info */}
      <div className="mt-6 p-4 bg-gray-50 rounded-lg">
        <h3 className="text-sm font-medium text-gray-700 mb-2">What happens during training?</h3>
        <ul className="text-xs text-gray-600 space-y-1">
          <li>• Your text data is tokenized and prepared for training</li>
          <li>• The model learns patterns and styles from your content</li>
          <li>• Progress is tracked with loss curves and system metrics</li>
          <li>• The trained model is automatically saved for chat</li>
        </ul>
        {systemInfo?.warnings && systemInfo.warnings.length > 0 && (
          <div className="mt-3 p-2 bg-yellow-50 border border-yellow-200 rounded text-xs text-yellow-800">
            <p className="font-medium">Hardware notes:</p>
            <ul className="list-disc list-inside">
              {systemInfo.warnings.map((warning, index) => (
                <li key={index}>{warning}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  )
}

export default TrainingWizard
