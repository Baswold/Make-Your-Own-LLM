import React from 'react'
import { useQuery } from 'react-query'
import { Folder, Calendar } from 'lucide-react'

const ProjectSelector = ({ currentProject, onProjectChange }) => {
  const { data: projectsData, isLoading } = useQuery(
    'projects',
    () => fetch('/api/projects').then(res => res.json()),
    { refetchInterval: 10000 }
  )

  const projects = projectsData?.projects || []

  return (
    <div className="bg-white rounded-lg p-4 shadow-sm border">
      <h3 className="font-medium text-sm mb-3">Projects</h3>
      
      {isLoading ? (
        <div className="text-xs text-gray-500">Loading projects...</div>
      ) : projects.length === 0 ? (
        <div className="text-xs text-gray-500">
          No projects yet. Upload data to create your first project.
        </div>
      ) : (
        <div className="space-y-2">
          {projects.map((project) => (
            <div
              key={project}
              onClick={() => onProjectChange(project)}
              className={`
                p-2 rounded cursor-pointer transition-colors text-xs
                ${currentProject === project 
                  ? 'bg-blue-50 border border-blue-200' 
                  : 'hover:bg-gray-50 border border-transparent'
                }
              `}
            >
              <div className="flex items-center">
                <Folder className="w-3 h-3 text-gray-400 mr-2" />
                <span className="font-medium truncate">{project}</span>
              </div>
            </div>
          ))}
        </div>
      )}
      
      {currentProject && (
        <div className="mt-4 pt-3 border-t">
          <div className="text-xs text-gray-500">
            <div className="font-medium">Current Project:</div>
            <div className="truncate">{currentProject}</div>
          </div>
        </div>
      )}
    </div>
  )
}

export default ProjectSelector