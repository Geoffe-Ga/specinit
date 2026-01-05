export interface UserStory {
  role: string
  action: string
  outcome: string
}

export interface TechStack {
  frontend: string[]
  backend: string[]
  database: string[]
  tools: string[]
}

export interface GitHubConfig {
  enabled: boolean
  repoUrl: string
  createRepo: boolean
  yoloMode: boolean
  tokenConfigured: boolean
}

export interface ProjectConfig {
  name: string
  projectDescription?: string
  platforms: string[]
  userStory: UserStory
  features: string[]
  techStack: TechStack
  aesthetics: string[]
  github: GitHubConfig
  additionalContext?: string
}

export interface GenerationResult {
  path: string
  totalCost: number
  generationTime: number
}

export interface StepProgress {
  step: string
  status: 'pending' | 'in_progress' | 'completed' | 'error'
  details?: {
    name?: string
    cost?: number
    message?: string
  }
}

export interface IssueProgress {
  issueNumber: number
  title: string
  status: 'queued' | 'in_progress' | 'pr_created' | 'ci_running' | 'ci_failed' | 'in_review' | 'changes_requested' | 'approved' | 'merged' | 'blocked' | 'failed'
  prNumber?: number
  prUrl?: string
  branch?: string
  commentsResolved?: number
}

export const PLATFORMS = [
  { id: 'web', label: 'Web', icon: '🌐' },
  { id: 'ios', label: 'iOS', icon: '📱' },
  { id: 'android', label: 'Android', icon: '🤖' },
  { id: 'desktop', label: 'Desktop', icon: '🖥️' },
  { id: 'cli', label: 'CLI', icon: '⌨️' },
  { id: 'api', label: 'API/Backend', icon: '🔌' },
]

export const TECH_OPTIONS = {
  frontend: [
    'React', 'Vue', 'Svelte', 'Next.js', 'React Native', 'TypeScript'
  ],
  backend: [
    'FastAPI', 'Express', 'Django', 'Node.js', 'Python'
  ],
  database: [
    'PostgreSQL', 'MongoDB', 'SQLite', 'Supabase', 'Firebase'
  ],
  tools: [
    'ESLint', 'Prettier', 'Jest', 'pytest', 'Docker'
  ],
}

export const AESTHETICS = [
  { id: 'minimalist', label: 'Minimalist' },
  { id: 'professional', label: 'Professional' },
  { id: 'playful', label: 'Playful' },
  { id: 'accessible', label: 'Accessible-First' },
  { id: 'modern', label: 'Modern' },
  { id: 'retro', label: 'Retro' },
]
