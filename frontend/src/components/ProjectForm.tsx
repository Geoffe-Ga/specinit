import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { PlatformSelector } from './PlatformSelector'
import { UserStoryInput } from './UserStoryInput'
import { FeatureList } from './FeatureList'
import { TechStackSelector } from './TechStackSelector'
import { AestheticsSelector } from './AestheticsSelector'
import { GitHubSetup } from './GitHubSetup'
import type { ProjectConfig } from '../types'

const projectSchema = z.object({
  name: z.string().min(1, 'Project name is required').max(50),
  platforms: z.array(z.string()).min(1, 'Select at least one platform'),
  userStory: z.object({
    role: z.string().min(3, 'Role must be at least 3 characters'),
    action: z.string().min(3, 'Action must be at least 3 characters'),
    outcome: z.string().min(3, 'Outcome must be at least 3 characters'),
  }),
  features: z
    .array(
      z
        .string()
        .min(1, 'Feature cannot be empty')
        .max(2000, 'Feature description must be less than 2000 characters')
    )
    .min(1, 'Add at least one feature')
    .max(20, 'Maximum 20 features allowed'),
  techStack: z.object({
    frontend: z.array(z.string()),
    backend: z.array(z.string()),
    database: z.array(z.string()),
    tools: z.array(z.string()),
  }),
  aesthetics: z.array(z.string()).max(3, 'Select up to 3 aesthetics'),
  github: z.object({
    enabled: z.boolean(),
    repoUrl: z.string(),
    createRepo: z.boolean(),
    yoloMode: z.boolean(),
    tokenConfigured: z.boolean(),
  }),
})

type FormData = z.infer<typeof projectSchema>

interface ProjectFormProps {
  onSubmit: (config: ProjectConfig) => void
}

export function ProjectForm({ onSubmit }: ProjectFormProps) {
  const [step, setStep] = useState(1)
  const totalSteps = 6

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors },
  } = useForm<FormData>({
    resolver: zodResolver(projectSchema),
    defaultValues: {
      name: '',
      platforms: [],
      userStory: { role: '', action: '', outcome: '' },
      features: [''],
      techStack: { frontend: [], backend: [], database: [], tools: [] },
      aesthetics: [],
      github: {
        enabled: false,
        repoUrl: '',
        createRepo: true,
        yoloMode: false,
        tokenConfigured: false,
      },
    },
  })

  const currentValues = watch()

  const handleFormSubmit = (data: FormData) => {
    onSubmit(data)
  }

  const nextStep = () => setStep((s) => Math.min(s + 1, totalSteps))
  const prevStep = () => setStep((s) => Math.max(s - 1, 1))

  return (
    <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-6">
      {/* Progress indicator */}
      <div className="flex items-center justify-between mb-8">
        {Array.from({ length: totalSteps }, (_, i) => (
          <div
            key={i}
            className={`flex items-center ${i < totalSteps - 1 ? 'flex-1' : ''}`}
          >
            <div
              className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium
                ${step > i + 1 ? 'bg-green-500 text-white' : ''}
                ${step === i + 1 ? 'bg-blue-600 text-white' : ''}
                ${step < i + 1 ? 'bg-gray-200 text-gray-600' : ''}`}
            >
              {i + 1}
            </div>
            {i < totalSteps - 1 && (
              <div
                className={`h-1 flex-1 mx-2 ${
                  step > i + 1 ? 'bg-green-500' : 'bg-gray-200'
                }`}
              />
            )}
          </div>
        ))}
      </div>

      {/* Step 1: Project Name & Platforms */}
      {step === 1 && (
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

          <PlatformSelector
            selected={currentValues.platforms}
            onChange={(platforms) => setValue('platforms', platforms)}
            error={errors.platforms?.message}
          />
        </div>
      )}

      {/* Step 2: User Story */}
      {step === 2 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">User Story</h2>
          <p className="text-gray-600 mb-4">
            Describe your project's main purpose using the classic user story format.
          </p>

          <UserStoryInput
            value={currentValues.userStory}
            onChange={(userStory) => setValue('userStory', userStory)}
            errors={errors.userStory}
          />
        </div>
      )}

      {/* Step 3: Features */}
      {step === 3 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Features</h2>
          <p className="text-gray-600 mb-4">
            Add up to 20 features for your project.
          </p>

          <FeatureList
            features={currentValues.features}
            onChange={(features) => setValue('features', features)}
            error={errors.features?.message}
          />
        </div>
      )}

      {/* Step 4: Tech Stack */}
      {step === 4 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Tech Stack</h2>
          <p className="text-gray-600 mb-4">
            Select the technologies for your project.
          </p>

          <TechStackSelector
            value={currentValues.techStack}
            onChange={(techStack) => setValue('techStack', techStack)}
            platforms={currentValues.platforms}
          />
        </div>
      )}

      {/* Step 5: Aesthetics */}
      {step === 5 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">UX Aesthetics</h2>
          <p className="text-gray-600 mb-4">
            Select up to 3 aesthetic principles for your project.
          </p>

          <AestheticsSelector
            selected={currentValues.aesthetics}
            onChange={(aesthetics) => setValue('aesthetics', aesthetics)}
            error={errors.aesthetics?.message}
          />
        </div>
      )}

      {/* Step 6: GitHub Integration */}
      {step === 6 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">GitHub Integration</h2>
          <p className="text-gray-600 mb-4">
            Choose how you want SpecInit to generate your project. GitHub Mode creates
            issues, branches, and PRs for better tracking and accuracy.
          </p>

          <GitHubSetup
            value={currentValues.github}
            onChange={(github) => setValue('github', github)}
            projectName={currentValues.name}
          />
        </div>
      )}

      {/* Navigation buttons */}
      <div className="flex justify-between">
        <button
          type="button"
          onClick={prevStep}
          disabled={step === 1}
          className="px-4 py-2 text-gray-600 hover:text-gray-900 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Previous
        </button>

        {step < totalSteps ? (
          <button
            type="button"
            onClick={nextStep}
            className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Next
          </button>
        ) : (
          <button
            type="submit"
            className="px-6 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
          >
            Generate Project
          </button>
        )}
      </div>
    </form>
  )
}
