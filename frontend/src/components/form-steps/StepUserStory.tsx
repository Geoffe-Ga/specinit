import type { FieldErrors } from 'react-hook-form'

import type { ProjectFormData } from '../../schemas/projectSchema'
import type { UserStory } from '../../types'
import { UserStoryInput } from '../UserStoryInput'

interface StepUserStoryProps {
  value: UserStory
  onChange: (userStory: UserStory) => void
  errors?: FieldErrors<ProjectFormData>['userStory']
}

export function StepUserStory({ value, onChange, errors }: StepUserStoryProps) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold mb-4">User Story</h2>
      <p className="text-gray-600 mb-4">
        Describe your project's main purpose using the classic user story format.
      </p>

      <UserStoryInput
        value={value}
        onChange={onChange}
        errors={errors}
      />
    </div>
  )
}
