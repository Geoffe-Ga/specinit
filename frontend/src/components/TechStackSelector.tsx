import { TECH_OPTIONS, type TechStack } from '../types'

interface TechStackSelectorProps {
  value: TechStack
  onChange: (techStack: TechStack) => void
  platforms: string[]
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
      {/* Frontend */}
      {showFrontend && (
        <div>
          <h3 className="text-sm font-medium text-gray-700 mb-2">Frontend</h3>
          <div className="flex flex-wrap gap-2">
            {TECH_OPTIONS.frontend.map((tech) => (
              <button
                key={tech}
                type="button"
                onClick={() => toggleOption('frontend', tech)}
                className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  value.frontend.includes(tech)
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {tech}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Backend */}
      {showBackend && (
        <div>
          <h3 className="text-sm font-medium text-gray-700 mb-2">Backend</h3>
          <div className="flex flex-wrap gap-2">
            {TECH_OPTIONS.backend.map((tech) => (
              <button
                key={tech}
                type="button"
                onClick={() => toggleOption('backend', tech)}
                className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  value.backend.includes(tech)
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {tech}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Database */}
      <div>
        <h3 className="text-sm font-medium text-gray-700 mb-2">Database</h3>
        <div className="flex flex-wrap gap-2">
          {TECH_OPTIONS.database.map((tech) => (
            <button
              key={tech}
              type="button"
              onClick={() => toggleOption('database', tech)}
              className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                value.database.includes(tech)
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {tech}
            </button>
          ))}
        </div>
      </div>

      {/* Tools */}
      <div>
        <h3 className="text-sm font-medium text-gray-700 mb-2">Tools</h3>
        <div className="flex flex-wrap gap-2">
          {TECH_OPTIONS.tools.map((tech) => (
            <button
              key={tech}
              type="button"
              onClick={() => toggleOption('tools', tech)}
              className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                value.tools.includes(tech)
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {tech}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}
