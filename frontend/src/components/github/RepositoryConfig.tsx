interface RepositoryConfigProps {
  repoUrl: string
  createRepo: boolean
  projectName: string
  onRepoUrlChange: (url: string) => void
  onCreateRepoChange: (create: boolean) => void
}

export function RepositoryConfig({
  repoUrl,
  createRepo,
  projectName,
  onRepoUrlChange,
  onCreateRepoChange,
}: RepositoryConfigProps) {
  return (
    <>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Repository URL
        </label>
        <input
          type="text"
          value={repoUrl}
          onChange={(e) => onRepoUrlChange(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder={`https://github.com/username/${projectName || 'my-project'}`}
        />
      </div>

      <label className="flex items-center gap-2 cursor-pointer">
        <input
          type="checkbox"
          checked={createRepo}
          onChange={(e) => onCreateRepoChange(e.target.checked)}
          className="w-4 h-4 text-blue-600 rounded"
        />
        <span className="text-sm">Create repository if it doesn't exist</span>
      </label>
    </>
  )
}
