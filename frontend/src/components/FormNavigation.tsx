interface FormNavigationProps {
  currentStep: number
  totalSteps: number
  onPrevious: () => void
  onNext: () => void
}

export function FormNavigation({
  currentStep,
  totalSteps,
  onPrevious,
  onNext,
}: FormNavigationProps) {
  const isFirstStep = currentStep === 1
  const isLastStep = currentStep === totalSteps

  return (
    <div className="flex justify-between">
      <button
        type="button"
        onClick={onPrevious}
        disabled={isFirstStep}
        className="px-4 py-2 text-gray-600 hover:text-gray-900 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        Previous
      </button>

      {isLastStep ? (
        <button
          type="submit"
          className="px-6 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
        >
          Generate Project
        </button>
      ) : (
        <button
          type="button"
          onClick={onNext}
          className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          Next
        </button>
      )}
    </div>
  )
}
