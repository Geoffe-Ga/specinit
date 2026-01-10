import type { FieldErrors, UseFormRegister } from 'react-hook-form'

import type { ProjectFormData } from '../../schemas/projectSchema'
import { PlatformSelector } from '../PlatformSelector'

interface StepBasicsProps {
  register: UseFormRegister<ProjectFormData>
  errors: FieldErrors<ProjectFormData>
  platforms: string[]
  projectDescription: string
  enableSuggestions: boolean
  onPlatformsChange: (platforms: string[]) => void
  onSuggestionsToggle: () => void
}

export function StepBasics({
  register,
  errors,
  platforms,
  projectDescription,
  enableSuggestions,
  onPlatformsChange,
  onSuggestionsToggle,
}: StepBasicsProps) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold mb-4">Project Basics</h2>

      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Project Name
        </label>
        <input
          {...register('name')}
          type="text"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="my-awesome-app"
        />
        {errors.name && (
          <p className="mt-1 text-sm text-red-600">{errors.name.message}</p>
        )}
      </div>

      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          What are you building? <span className="text-gray-500 font-normal">(Optional)</span>
        </label>
        <textarea
          {...register('projectDescription')}
          rows={3}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
          placeholder="e.g., A mobile app for tracking daily research notes and progress"
          maxLength={500}
        />
        <div className="flex justify-between items-start mt-1">
          <p className="text-sm text-gray-500">
            Provide a brief description of your project idea. This will help us suggest relevant user stories and features.
          </p>
          <p className="text-xs text-gray-400 ml-2 whitespace-nowrap">
            {projectDescription?.length || 0}/500
          </p>
        </div>
        {errors.projectDescription && (
          <p className="mt-1 text-sm text-red-600">{errors.projectDescription.message}</p>
        )}
      </div>

      <SuggestionsToggle
        enabled={enableSuggestions}
        onToggle={onSuggestionsToggle}
      />

      <PlatformSelector
        selected={platforms}
        onChange={onPlatformsChange}
        error={errors.platforms?.message}
      />
    </div>
  )
}

interface SuggestionsToggleProps {
  enabled: boolean
  onToggle: () => void
}

function SuggestionsToggle({ enabled, onToggle }: SuggestionsToggleProps) {
  return (
    <div className="mb-6 p-4 border border-gray-200 rounded-lg">
      <div className="flex items-center justify-between mb-3">
        <label className="text-sm font-medium text-gray-700">
          Enable Auto-Suggestions
        </label>
        <button
          type="button"
          role="switch"
          aria-checked={enabled}
          onClick={onToggle}
          className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${
            enabled ? 'bg-blue-600' : 'bg-gray-200'
          }`}
        >
          <span
            className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
              enabled ? 'translate-x-6' : 'translate-x-1'
            }`}
          />
        </button>
      </div>

      {!enabled ? (
        <SuggestionsInfoPanel />
      ) : (
        <SuggestionsActivePanel />
      )}
    </div>
  )
}

function SuggestionsInfoPanel() {
  return (
    <div className="space-y-3">
      <p className="text-sm text-gray-600">
        Get AI-powered suggestions for user stories, features, tech stack, and more as you fill out the form.
      </p>

      <div className="space-y-1">
        <p className="text-sm font-medium text-gray-700">Benefits:</p>
        <ul className="text-sm text-gray-600 space-y-1">
          <li className="flex items-start">
            <span className="mr-2">&#10024;</span>
            <span>Faster project setup</span>
          </li>
          <li className="flex items-start">
            <span className="mr-2">&#127919;</span>
            <span>Comprehensive feature suggestions</span>
          </li>
          <li className="flex items-start">
            <span className="mr-2">&#128295;</span>
            <span>Proven tech stack recommendations</span>
          </li>
        </ul>
      </div>

      <div className="pt-2 border-t border-gray-200">
        <p className="text-sm text-gray-700">
          <span className="font-medium">Estimated cost:</span>{' '}
          <span className="text-gray-600">$0.05 - $0.15 per session</span>
        </p>
        <p className="text-xs text-gray-500 mt-1">
          Uses your configured Claude API key
        </p>
      </div>
    </div>
  )
}

function SuggestionsActivePanel() {
  return (
    <div className="space-y-2">
      <div className="flex items-center gap-2">
        <span className="text-sm font-medium text-blue-600">&#10024; Auto-Suggestions Active</span>
      </div>
      <p className="text-sm text-gray-600">
        Session cost so far: <span className="font-medium">$0.00</span>
      </p>
      <p className="text-xs text-gray-500">
        Suggestions will use your Claude API key
      </p>
    </div>
  )
}
