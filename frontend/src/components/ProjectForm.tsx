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

interface StepRendererProps {
  step: number
  values: ProjectFormData
  errors: ReturnType<typeof useForm<ProjectFormData>>['formState']['errors']
  register: ReturnType<typeof useForm<ProjectFormData>>['register']
  setValue: ReturnType<typeof useForm<ProjectFormData>>['setValue']
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

      <StepRenderer
        step={step}
        values={currentValues}
        errors={errors}
        register={register}
        setValue={setValue}
      />

      <FormNavigation
        currentStep={step}
        totalSteps={TOTAL_STEPS}
        onPrevious={prevStep}
        onNext={nextStep}
      />
    </form>
  )
}
