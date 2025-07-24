import React, { useState, useCallback } from 'react'
import { Upload, FileText, X } from 'lucide-react'

const DataUpload = ({ currentProject, onProjectChange, onDataUploaded }) => {
  const [dragActive, setDragActive] = useState(false)
  const [files, setFiles] = useState([])
  const [uploading, setUploading] = useState(false)
  const [projectSlug, setProjectSlug] = useState(currentProject || '')

  const handleDrag = useCallback((e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true)
    } else if (e.type === "dragleave") {
      setDragActive(false)
    }
  }, [])

  const handleDrop = useCallback((e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    
    const droppedFiles = Array.from(e.dataTransfer.files)
    const validFiles = droppedFiles.filter(file => {
      const ext = file.name.split('.').pop().toLowerCase()
      return ['txt', 'jsonl', 'csv', 'pdf'].includes(ext)
    })
    
    setFiles(prev => [...prev, ...validFiles])
  }, [])

  const handleFileInput = (e) => {
    const selectedFiles = Array.from(e.target.files)
    setFiles(prev => [...prev, ...selectedFiles])
  }

  const removeFile = (index) => {
    setFiles(prev => prev.filter((_, i) => i !== index))
  }

  const uploadFiles = async () => {
    if (!projectSlug.trim()) {
      alert('Please enter a project name')
      return
    }

    if (files.length === 0) {
      alert('Please select files to upload')
      return
    }

    setUploading(true)

    try {
      for (const file of files) {
        const formData = new FormData()
        formData.append('file', file)

        const response = await fetch(`/api/upload-data?project_slug=${encodeURIComponent(projectSlug)}`, {
          method: 'POST',
          body: formData
        })

        if (!response.ok) {
          const error = await response.json()
          throw new Error(error.detail || 'Upload failed')
        }
      }

      onProjectChange(projectSlug)
      onDataUploaded()
      setFiles([])
      alert('Files uploaded successfully!')
      
    } catch (error) {
      console.error('Upload error:', error)
      alert('Upload failed: ' + error.message)
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="bg-white rounded-lg p-6 shadow-sm border">
      <h2 className="text-xl font-semibold mb-4">Upload Training Data</h2>
      
      {/* Project Name Input */}
      <div className="mb-6">
        <label htmlFor="project-name" className="block text-sm font-medium text-gray-700 mb-2">
          Project Name
        </label>
        <input
          id="project-name"
          type="text"
          value={projectSlug}
          onChange={(e) => setProjectSlug(e.target.value)}
          placeholder="my-awesome-model"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {/* File Drop Zone */}
      <div
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        className={`
          relative border-2 border-dashed rounded-lg p-8 text-center transition-colors
          ${dragActive 
            ? 'border-blue-500 bg-blue-50' 
            : 'border-gray-300 hover:border-gray-400'
          }
        `}
      >
        <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <p className="text-lg font-medium text-gray-900 mb-2">
          Drop files here or click to browse
        </p>
        <p className="text-sm text-gray-500 mb-4">
          Supports .txt, .jsonl, .csv, and .pdf files
        </p>
        
        <input
          type="file"
          multiple
          accept=".txt,.jsonl,.csv,.pdf"
          onChange={handleFileInput}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
        />
      </div>

      {/* File List */}
      {files.length > 0 && (
        <div className="mt-6">
          <h3 className="text-sm font-medium text-gray-700 mb-3">Selected Files</h3>
          <div className="space-y-2">
            {files.map((file, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                <div className="flex items-center">
                  <FileText className="w-4 h-4 text-gray-400 mr-3" />
                  <span className="text-sm font-medium">{file.name}</span>
                  <span className="text-xs text-gray-500 ml-2">
                    ({(file.size / 1024).toFixed(1)} KB)
                  </span>
                </div>
                <button
                  onClick={() => removeFile(index)}
                  className="p-1 hover:bg-gray-200 rounded"
                >
                  <X className="w-4 h-4 text-gray-400" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Upload Button */}
      <div className="mt-6">
        <button
          onClick={uploadFiles}
          disabled={uploading || !projectSlug.trim() || files.length === 0}
          className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {uploading ? 'Uploading...' : 'Upload Files'}
        </button>
      </div>

      {/* Help Text */}
      <div className="mt-4 text-xs text-gray-500">
        <p><strong>Supported formats:</strong></p>
        <ul className="list-disc list-inside mt-1 space-y-1">
          <li><strong>Text files (.txt):</strong> Plain text content</li>
          <li><strong>JSONL (.jsonl):</strong> JSON lines with 'text' or 'content' fields</li>
          <li><strong>CSV (.csv):</strong> Tables with text/content/story/message columns</li>
          <li><strong>PDF (.pdf):</strong> Extracted text from PDF documents</li>
        </ul>
      </div>
    </div>
  )
}

export default DataUpload