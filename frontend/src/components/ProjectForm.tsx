import { zodResolver } from '@hookform/resolvers/zod'
import { useState } from 'react'
import { useForm } from 'react-hook-form'

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

export function ProjectForm({ onSubmit }: ProjectFormProps) {
  const [step, setStep] = useState(1)

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

  const currentValues = watch()

  const handleFormSubmit = (data: ProjectFormData) => {
    onSubmit(data)
  }

  const nextStep = () => setStep((s) => Math.min(s + 1, TOTAL_STEPS))
  const prevStep = () => setStep((s) => Math.max(s - 1, 1))

  return (
    <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-6">
      <FormProgressIndicator currentStep={step} totalSteps={TOTAL_STEPS} />

      {step === 1 && (
        <StepBasics
          register={register}
          errors={errors}
          platforms={currentValues.platforms}
          projectDescription={currentValues.projectDescription || ''}
          enableSuggestions={currentValues.enableSuggestions || false}
          onPlatformsChange={(platforms) => setValue('platforms', platforms)}
          onSuggestionsToggle={() => setValue('enableSuggestions', !currentValues.enableSuggestions)}
        />
      )}

      {step === 2 && (
        <StepUserStory
          value={currentValues.userStory}
          onChange={(userStory) => setValue('userStory', userStory)}
          errors={errors.userStory}
        />
      )}

      {step === 3 && (
        <StepFeatures
          features={currentValues.features}
          onChange={(features) => setValue('features', features)}
          error={errors.features?.message}
        />
      )}

      {step === 4 && (
        <StepTechStack
          value={currentValues.techStack}
          onChange={(techStack) => setValue('techStack', techStack)}
          platforms={currentValues.platforms}
        />
      )}

      {step === 5 && (
        <StepAesthetics
          selected={currentValues.aesthetics}
          onChange={(aesthetics) => setValue('aesthetics', aesthetics)}
          error={errors.aesthetics?.message}
        />
      )}

      {step === 6 && (
        <StepGitHub
          value={currentValues.github}
          onChange={(github) => setValue('github', github)}
          projectName={currentValues.name}
        />
      )}

      {step === 7 && (
        <StepContext
          register={register}
          errors={errors}
          additionalContext={currentValues.additionalContext || ''}
        />
      )}

      <FormNavigation
        currentStep={step}
        totalSteps={TOTAL_STEPS}
        onPrevious={prevStep}
        onNext={nextStep}
      />
    </form>
  )
}
