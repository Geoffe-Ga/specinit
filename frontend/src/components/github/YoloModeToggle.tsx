interface YoloModeToggleProps {
  enabled: boolean
  onChange: (enabled: boolean) => void
}

export function YoloModeToggle({ enabled, onChange }: YoloModeToggleProps) {
  return (
    <div className="pt-3 border-t border-gray-200">
      <label className="flex items-start gap-2 cursor-pointer">
        <input
          type="checkbox"
          checked={enabled}
          onChange={(e) => onChange(e.target.checked)}
          className="w-4 h-4 text-blue-600 rounded mt-0.5"
        />
        <div>
          <span className="font-medium">Enable YOLO Mode</span>
          <p className="text-sm text-gray-500">
            Auto-resolve CI failures and review feedback (recursively iterate until all checks pass)
          </p>
        </div>
      </label>
    </div>
  )
}
