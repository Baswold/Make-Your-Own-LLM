import React from 'react'
import { Cpu, HardDrive, Zap, Monitor } from 'lucide-react'

const SystemMonitor = ({ systemInfo }) => {
  if (!systemInfo) {
    return (
      <div className="bg-white rounded-lg p-4 shadow-sm border">
        <h3 className="font-medium text-sm mb-3">System Status</h3>
        <div className="text-xs text-gray-500">Loading...</div>
      </div>
    )
  }

  const formatMemory = (mb) => {
    if (mb > 1024) {
      return `${(mb / 1024).toFixed(1)} GB`
    }
    return `${mb} MB`
  }

  const getStatusColor = (percent) => {
    if (percent > 80) return 'text-red-600 bg-red-100'
    if (percent > 60) return 'text-yellow-600 bg-yellow-100'
    return 'text-green-600 bg-green-100'
  }

  return (
    <div className="bg-white rounded-lg p-4 shadow-sm border">
      <h3 className="font-medium text-sm mb-3">System Status</h3>
      
      <div className="space-y-3">
        {/* Device Type */}
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <Monitor className="w-3 h-3 text-gray-400 mr-2" />
            <span className="text-xs text-gray-600">Device</span>
          </div>
          <div className="text-xs font-medium">
            {systemInfo.device.toUpperCase()}
          </div>
        </div>

        {/* CPU Usage */}
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <Cpu className="w-3 h-3 text-gray-400 mr-2" />
            <span className="text-xs text-gray-600">CPU</span>
          </div>
          <div className={`text-xs px-2 py-1 rounded ${getStatusColor(systemInfo.cpu_percent)}`}>
            {Math.round(systemInfo.cpu_percent)}%
          </div>
        </div>

        {/* Memory Usage */}
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <HardDrive className="w-3 h-3 text-gray-400 mr-2" />
            <span className="text-xs text-gray-600">Memory</span>
          </div>
          <div className={`text-xs px-2 py-1 rounded ${getStatusColor(systemInfo.memory_percent)}`}>
            {Math.round(systemInfo.memory_percent)}%
          </div>
        </div>

        {/* GPU Info */}
        {systemInfo.gpu_available && (
          <>
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <Zap className="w-3 h-3 text-gray-400 mr-2" />
                <span className="text-xs text-gray-600">GPU</span>
              </div>
              <div className="text-xs font-medium text-green-600">
                Available
              </div>
            </div>
            
            {systemInfo.gpu_memory_used && (
              <>
                <div className="flex items-center justify-between">
                  <span className="text-xs text-gray-600 ml-5">VRAM</span>
                  <div className="text-xs">
                    {formatMemory(systemInfo.gpu_memory_used)} / {formatMemory(systemInfo.gpu_memory_total)}
                  </div>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-xs text-gray-600 ml-5">Util</span>
                  <div className={`text-xs px-2 py-1 rounded ${getStatusColor(systemInfo.gpu_utilization)}`}>
                    {Math.round(systemInfo.gpu_utilization)}%
                  </div>
                </div>
              </>
            )}
          </>
        )}

        {!systemInfo.gpu_available && (
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <Zap className="w-3 h-3 text-gray-400 mr-2" />
              <span className="text-xs text-gray-600">GPU</span>
            </div>
            <div className="text-xs text-gray-500">
              CPU only
            </div>
          </div>
        )}
      </div>

      {/* Warning for CPU-only mode */}
      {!systemInfo.gpu_available && (
        <div className="mt-3 p-2 bg-yellow-50 border border-yellow-200 rounded text-xs">
          <p className="text-yellow-800">
            Training on CPU will be slower. Consider using a GPU-enabled environment for better performance.
          </p>
        </div>
      )}
    </div>
  )
}

export default SystemMonitor