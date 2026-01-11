export function LoadingState() {
  return (
    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
      <div className="flex items-center justify-center gap-2 text-blue-700">
        <span className="animate-spin" aria-hidden="true">
          🔄
        </span>
        <span>Generating tech stack recommendations...</span>
      </div>
    </div>
  )
}
