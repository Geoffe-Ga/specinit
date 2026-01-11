import { zodResolver } from '@hookform/resolvers/zod'
import { useEffect, useState } from 'react'
import { useForm } from 'react-hook-form'

import { useSuggestionContext } from '../contexts/SuggestionContext'
import { projectSchema, type ProjectFormData } from '../schemas/projectSchema'
import type { ProjectConfig } from '../types'

import {
  StepAesthetics,
  StepBasics,
  StepContext,
  StepFeatures,
  StepGitHub,
  StepTechStack,
  StepUserStory,
} from './form-steps'
import { FormNavigation } from './FormNavigation'
import { FormProgressIndicator } from './FormProgressIndicator'

const TOTAL_STEPS = 7

const DEFAULT_VALUES: ProjectFormData = {
  name: '',
  projectDescription: '',
  enableSuggestions: false,
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
  additionalContext: '',
}

interface ProjectFormProps {
  onSubmit: (config: ProjectConfig) => void
}

interface StepRendererProps {
  step: number
  values: ProjectFormData
  errors: ReturnType<typeof useForm<ProjectFormData>>['formState']['errors']
  register: ReturnType<typeof useForm<ProjectFormData>>['register']
  setValue: ReturnType<typeof useForm<ProjectFormData>>['setValue']
}

/**
 * Custom hook to watch all form fields individually for optimized re-rendering
 * Returns both individual fields and a combined ProjectFormData object
 */
function useWatchedFormFields(watch: ReturnType<typeof useForm<ProjectFormData>>['watch']) {
  const name = watch('name')
  const projectDescription = watch('projectDescription')
  const platforms = watch('platforms')
  const userStory = watch('userStory')
  const features = watch('features')
  const techStack = watch('techStack')
  const aesthetics = watch('aesthetics')
  const additionalContext = watch('additionalContext')
  const enableSuggestions = watch('enableSuggestions')
  const github = watch('github')

  const currentValues: ProjectFormData = {
    name,
    projectDescription: projectDescription || '',
    enableSuggestions: enableSuggestions ?? false,
    platforms,
    userStory,
    features,
    techStack,
    aesthetics,
    github,
    additionalContext: additionalContext || '',
  }

  return {
    name,
    projectDescription,
    platforms,
    userStory,
    features,
    techStack,
    aesthetics,
    additionalContext,
    enableSuggestions,
    github,
    currentValues,
  }
}

function StepRenderer({ step, values, errors, register, setValue }: StepRendererProps) {
  const stepComponents = {
    1: (
      <StepBasics
        register={register}
        errors={errors}
        platforms={values.platforms}
        projectDescription={values.projectDescription || ''}
        enableSuggestions={values.enableSuggestions || false}
        onPlatformsChange={(platforms) => setValue('platforms', platforms)}
        onSuggestionsToggle={() => setValue('enableSuggestions', !values.enableSuggestions)}
      />
    ),
    2: (
      <StepUserStory
        value={values.userStory}
        onChange={(userStory) => setValue('userStory', userStory)}
        errors={errors.userStory}
      />
    ),
    3: (
      <StepFeatures
        features={values.features}
        onChange={(features) => setValue('features', features)}
        error={errors.features?.message}
      />
    ),
    4: (
      <StepTechStack
        value={values.techStack}
        onChange={(techStack) => setValue('techStack', techStack)}
        platforms={values.platforms}
      />
    ),
    5: (
      <StepAesthetics
        selected={values.aesthetics}
        onChange={(aesthetics) => setValue('aesthetics', aesthetics)}
        error={errors.aesthetics?.message}
      />
    ),
    6: (
      <StepGitHub
        value={values.github}
        onChange={(github) => setValue('github', github)}
        projectName={values.name}
      />
    ),
    7: (
      <StepContext
        register={register}
        errors={errors}
        additionalContext={values.additionalContext || ''}
      />
    ),
  }

  return stepComponents[step as keyof typeof stepComponents] || null
}

export function ProjectForm({ onSubmit }: ProjectFormProps) {
  const [step, setStep] = useState(1)
  const { updateContext, setSuggestionsEnabled } = useSuggestionContext()

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors },
  } = useForm<ProjectFormData>({
    resolver: zodResolver(projectSchema),
    defaultValues: DEFAULT_VALUES,
  })

  // Watch individual fields instead of entire form to optimize dependency tracking
  const { name, projectDescription, platforms, userStory, features, techStack, aesthetics, additionalContext, enableSuggestions, currentValues } = useWatchedFormFields(watch)

  // Update suggestion context with debouncing to prevent excessive re-renders
  // Dependencies are individual fields, NOT currentValues, to avoid recreating timeout on every render
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      updateContext('projectName', name)
      updateContext('projectDescription', projectDescription)
      updateContext('platforms', platforms)
      updateContext('userStory', userStory)
      updateContext('features', features)
      updateContext('techStack', techStack)
      updateContext('aesthetics', aesthetics)
      updateContext('additionalContext', additionalContext)
    }, 300) // 300ms debounce to avoid updates on every keystroke

    return () => clearTimeout(timeoutId)
  }, [name, projectDescription, platforms, userStory, features, techStack, aesthetics, additionalContext, updateContext])

  // Update suggestions enabled state
  useEffect(() => {
    setSuggestionsEnabled(enableSuggestions ?? false)
  }, [enableSuggestions, setSuggestionsEnabled])

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <FormProgressIndicator currentStep={step} totalSteps={TOTAL_STEPS} />
      <StepRenderer step={step} values={currentValues} errors={errors} register={register} setValue={setValue} />
      <FormNavigation
        currentStep={step}
        totalSteps={TOTAL_STEPS}
        onPrevious={() => setStep((s) => Math.max(s - 1, 1))}
        onNext={() => setStep((s) => Math.min(s + 1, TOTAL_STEPS))}
      />
    </form>
  )
}
