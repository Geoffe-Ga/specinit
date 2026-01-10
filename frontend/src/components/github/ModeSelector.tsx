interface ModeSelectorProps {
  enabled: boolean
  onModeChange: (enabled: boolean) => void
}

export function ModeSelector({ enabled, onModeChange }: ModeSelectorProps) {
  return (
    <>
      <div className="flex items-center gap-4">
        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="radio"
            name="github-mode"
            checked={!enabled}
            onChange={() => onModeChange(false)}
            className="w-4 h-4 text-blue-600"
          />
          <span className="font-medium">Local Mode</span>
        </label>
        <span className="text-sm text-gray-500">Generate files without GitHub</span>
      </div>

      <div className="flex items-center gap-4">
        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="radio"
            name="github-mode"
            checked={enabled}
            onChange={() => onModeChange(true)}
            className="w-4 h-4 text-blue-600"
          />
          <span className="font-medium">GitHub Mode</span>
        </label>
        <span className="text-sm text-gray-500">Issue-driven development with PRs</span>
      </div>
    </>
  )
}
