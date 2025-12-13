import type { UserStory } from '../types'
import type { FieldErrors } from 'react-hook-form'

interface UserStoryInputProps {
  value: UserStory
  onChange: (userStory: UserStory) => void
  errors?: FieldErrors<UserStory>
}

export function UserStoryInput({ value, onChange, errors }: UserStoryInputProps) {
  const updateField = (field: keyof UserStory, fieldValue: string) => {
    onChange({ ...value, [field]: fieldValue })
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 text-lg text-gray-600">
        <span>As</span>
        <input
          type="text"
          value={value.role}
          onChange={(e) => updateField('role', e.target.value)}
          className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="a developer"
        />
      </div>
      {errors?.role && (
        <p className="text-sm text-red-600">{errors.role.message}</p>
      )}

      <div className="flex items-center gap-2 text-lg text-gray-600">
        <span>I want to</span>
        <input
          type="text"
          value={value.action}
          onChange={(e) => updateField('action', e.target.value)}
          className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="quickly bootstrap new projects"
        />
      </div>
      {errors?.action && (
        <p className="text-sm text-red-600">{errors.action.message}</p>
      )}

      <div className="flex items-center gap-2 text-lg text-gray-600">
        <span>So that</span>
        <input
          type="text"
          value={value.outcome}
          onChange={(e) => updateField('outcome', e.target.value)}
          className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="I can focus on building features"
        />
      </div>
      {errors?.outcome && (
        <p className="text-sm text-red-600">{errors.outcome.message}</p>
      )}
    </div>
  )
}
