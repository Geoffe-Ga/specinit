import { z } from 'zod'

export const projectSchema = z.object({
  name: z.string().min(1, 'Project name is required').max(50),
  projectDescription: z
    .string()
    .max(500, 'Project description must be less than 500 characters')
    .optional(),
  enableSuggestions: z.boolean().optional(),
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
        .trim()
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
  additionalContext: z
    .string()
    .max(10000, 'Additional context must be less than 10,000 characters')
    .optional(),
})

export type ProjectFormData = z.infer<typeof projectSchema>
