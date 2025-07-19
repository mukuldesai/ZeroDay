import React from 'react'
import { DragDropContext, Droppable, Draggable } from '@hello-pangea/dnd'
import { motion } from 'framer-motion'
import { Square, PlayCircle, Eye, CheckCircle } from 'lucide-react'
import { Task } from '../../lib/types'
import { StatusBadge } from './StatusBadge'
import { AgentBadge } from './AgentBadge'
import { ProgressBar } from './ProgressBar'

interface KanbanBoardProps {
  kanbanColumns: Record<string, Task[]>
  onDragEnd: (result: any) => void
  userId?: string
}

interface KanbanTaskCardProps {
  task: Task
  index: number
  userId?: string
}

const KanbanTaskCard: React.FC<KanbanTaskCardProps> = ({ task, index, userId }) => {
  const userOwnsTask = !userId || task.userId === userId

  return (
    <Draggable draggableId={task.id} index={index}>
      {(provided, snapshot) => (
        <div
          ref={provided.innerRef}
          {...provided.draggableProps}
          {...provided.dragHandleProps}
        >
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className={`bg-gray-50 rounded-lg p-3 cursor-grab hover:shadow-md transition-all duration-200 mb-3 ${
              snapshot.isDragging
                ? 'shadow-2xl rotate-3 scale-105 bg-white border-2 border-orange-300'
                : 'hover:scale-102'
            } ${!userOwnsTask ? 'opacity-75' : ''}`}
            style={{
              ...provided.draggableProps.style,
              ...(snapshot.isDragging && {
                transform: `${provided.draggableProps.style?.transform} rotate(3deg)`,
              }),
            }}
          >
            <div className="flex items-start justify-between mb-2">
              <h4 className="font-medium text-gray-900 text-sm line-clamp-2">{task.title}</h4>
              <StatusBadge type="priority" value={task.priority} size="sm" />
            </div>

            <p className="text-xs text-gray-600 mb-3 line-clamp-2">{task.description}</p>

            <ProgressBar 
              progress={task.progress ?? 0}
              color="orange"
              size="sm"
              className="mb-3"
            />

            <div className="flex items-center justify-between mb-2">
              <AgentBadge agent={task.assignedAgent} size="sm" showIcon={false} />
              <span className="text-xs text-gray-500">{task.estimatedTime}</span>
            </div>

            <div className="flex flex-wrap gap-1 mb-2">
              {task.tags.slice(0, 2).map((tag, tagIndex) => (
                <span key={tagIndex} className="px-1.5 py-0.5 bg-gray-200 text-gray-600 text-xs rounded">
                  {tag}
                </span>
              ))}
              {task.tags.length > 2 && (
                <span className="px-1.5 py-0.5 bg-gray-200 text-gray-600 text-xs rounded">
                  +{task.tags.length - 2}
                </span>
              )}
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-1 text-xs text-gray-500">
                {task.difficulty === 'easy' && <span className="text-green-500">●</span>}
                {task.difficulty === 'medium' && <span className="text-yellow-500">●●</span>}
                {task.difficulty === 'hard' && <span className="text-red-500">●●●</span>}
                <span>{task.difficulty}</span>
              </div>
              <div className="text-xs text-gray-500">
                {task.subtasks?.filter(st => st.completed).length ?? 0}/{task.subtasks?.length ?? 0}
              </div>
            </div>
          </motion.div>
        </div>
      )}
    </Draggable>
  )
}

export const KanbanBoard: React.FC<KanbanBoardProps> = ({ kanbanColumns, onDragEnd, userId }) => {
  const getColumnIcon = (status: string) => {
    switch (status) {
      case 'todo': return <Square className="w-8 h-8 mx-auto" />
      case 'in-progress': return <PlayCircle className="w-8 h-8 mx-auto" />
      case 'review': return <Eye className="w-8 h-8 mx-auto" />
      case 'completed': return <CheckCircle className="w-8 h-8 mx-auto" />
      default: return <Square className="w-8 h-8 mx-auto" />
    }
  }

  const getColumnColor = (status: string) => {
    switch (status) {
      case 'todo': return 'bg-gray-100 text-gray-700'
      case 'in-progress': return 'bg-blue-100 text-blue-700'
      case 'review': return 'bg-yellow-100 text-yellow-700'
      case 'completed': return 'bg-green-100 text-green-700'
      default: return 'bg-gray-100 text-gray-700'
    }
  }

  const filterUserTasks = (tasks: Task[]) => {
    if (!userId) return tasks
    return tasks.filter(task => !task.userId || task.userId === userId)
  }

  return (
    <DragDropContext onDragEnd={onDragEnd}>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {Object.entries(kanbanColumns).map(([status, tasks]) => {
          const userTasks = filterUserTasks(tasks)
          
          return (
            <Droppable key={status} droppableId={status}>
              {(provided, snapshot) => (
                <div
                  ref={provided.innerRef}
                  {...provided.droppableProps}
                  className={`bg-white rounded-2xl shadow-lg border-2 p-4 transition-all duration-200 min-h-[400px] ${
                    snapshot.isDraggingOver 
                      ? 'border-orange-300 bg-orange-50 shadow-xl scale-105' 
                      : 'border-gray-100'
                  }`}
                >
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="font-semibold text-gray-900 capitalize">
                      {status.replace('-', ' ')}
                    </h3>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getColumnColor(status)}`}>
                      {userTasks.length}
                    </span>
                  </div>
                  
                  <div className="space-y-3 max-h-96 overflow-y-auto">
                    {userTasks.map((task, index) => (
                      <KanbanTaskCard key={task.id} task={task} index={index} userId={userId} />
                    ))}
                    {provided.placeholder}
                    
                    {userTasks.length === 0 && (
                      <div className={`border-2 border-dashed rounded-lg p-6 text-center transition-all duration-200 ${
                        snapshot.isDraggingOver 
                          ? 'border-orange-300 bg-orange-100' 
                          : 'border-gray-200 bg-gray-50'
                      }`}>
                        <div className="text-gray-400 mb-2">
                          {getColumnIcon(status)}
                        </div>
                        <p className="text-sm text-gray-500">
                          {snapshot.isDraggingOver ? 'Drop here!' : `No ${status.replace('-', ' ')} tasks`}
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </Droppable>
          )
        })}
      </div>
    </DragDropContext>
  )
}