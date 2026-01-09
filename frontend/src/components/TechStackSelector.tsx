import { TECH_OPTIONS, type TechStack } from '../types'

interface TechStackSelectorProps {
  value: TechStack
  onChange: (techStack: TechStack) => void
  platforms: string[]
}

// Shared className constants for tech selection buttons
const SELECTED_CLASS = 'bg-blue-600 text-white'
const UNSELECTED_CLASS = 'bg-gray-100 text-gray-700 hover:bg-gray-200'

interface CategorySectionProps {
  title: string
  category: keyof TechStack
  options: string[]
  selectedOptions: string[]
  onToggle: (category: keyof TechStack, option: string) => void
}

function CategorySection({
  title,
  category,
  options,
  selectedOptions,
  onToggle,
}: CategorySectionProps) {
  return (
    <div>
      <h3 className="text-sm font-medium text-gray-700 mb-2">{title}</h3>
      <div className="flex flex-wrap gap-2">
        {options.map((tech) => (
          <button
            key={tech}
            type="button"
            onClick={() => onToggle(category, tech)}
            className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
              selectedOptions.includes(tech) ? SELECTED_CLASS : UNSELECTED_CLASS
            }`}
          >
            {tech}
          </button>
        ))}
      </div>
    </div>
  )
}

export function TechStackSelector({ value, onChange, platforms }: TechStackSelectorProps) {
  const toggleOption = (category: keyof TechStack, option: string) => {
    const current = value[category]
    const updated = current.includes(option)
      ? current.filter((o) => o !== option)
      : [...current, option]
    onChange({ ...value, [category]: updated })
  }

  const showFrontend = platforms.some((p) => ['web', 'ios', 'android', 'desktop'].includes(p))
  const showBackend = !platforms.every((p) => p === 'cli')

  return (
    <div className="space-y-6">
      {showFrontend && (
        <CategorySection
          title="Frontend"
          category="frontend"
          options={TECH_OPTIONS.frontend}
          selectedOptions={value.frontend}
          onToggle={toggleOption}
        />
      )}

      {showBackend && (
        <CategorySection
          title="Backend"
          category="backend"
          options={TECH_OPTIONS.backend}
          selectedOptions={value.backend}
          onToggle={toggleOption}
        />
      )}

      <CategorySection
        title="Database"
        category="database"
        options={TECH_OPTIONS.database}
        selectedOptions={value.database}
        onToggle={toggleOption}
      />

      <CategorySection
        title="Tools"
        category="tools"
        options={TECH_OPTIONS.tools}
        selectedOptions={value.tools}
        onToggle={toggleOption}
      />
    </div>
  )
}
