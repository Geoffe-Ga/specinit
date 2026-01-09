import type { FieldErrors, UseFormRegister } from 'react-hook-form'

import type { ProjectFormData } from '../../schemas/projectSchema'

interface StepContextProps {
  register: UseFormRegister<ProjectFormData>
  errors: FieldErrors<ProjectFormData>
  additionalContext: string
}

export function StepContext({ register, errors, additionalContext }: StepContextProps) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold mb-4">Additional Context (Optional)</h2>
      <p className="text-gray-600 mb-4">
        Provide any additional context, requirements, or constraints for your project.
        This can include detailed specifications, architectural preferences, or domain-specific information.
      </p>

      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Additional Context
        </label>
        <textarea
          {...register('additionalContext')}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-y min-h-[200px]"
          placeholder="Example: This project should follow Clean Architecture principles. The authentication system must support OAuth2 and JWT tokens. All API responses should follow the JSON:API specification..."
        />
        <p className="mt-1 text-sm text-gray-500">
          {additionalContext?.length || 0} / 10,000 characters
          {additionalContext && additionalContext.length > 5000 && (
            <span className="ml-2 text-amber-600">
              Note: Large amounts of context may increase generation costs
            </span>
          )}
        </p>
        {errors.additionalContext && (
          <p className="mt-1 text-sm text-red-600">{errors.additionalContext.message}</p>
        )}
      </div>
    </div>
  )
}
