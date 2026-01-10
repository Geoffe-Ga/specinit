interface FormProgressIndicatorProps {
  currentStep: number
  totalSteps: number
}

export function FormProgressIndicator({ currentStep, totalSteps }: FormProgressIndicatorProps) {
  return (
    <div className="flex items-center justify-between mb-8">
      {Array.from({ length: totalSteps }, (_, i) => (
        <div
          key={i}
          className={`flex items-center ${i < totalSteps - 1 ? 'flex-1' : ''}`}
        >
          <StepCircle stepNumber={i + 1} currentStep={currentStep} />
          {i < totalSteps - 1 && (
            <StepConnector isComplete={currentStep > i + 1} />
          )}
        </div>
      ))}
    </div>
  )
}

interface StepCircleProps {
  stepNumber: number
  currentStep: number
}

function StepCircle({ stepNumber, currentStep }: StepCircleProps) {
  const isComplete = currentStep > stepNumber
  const isCurrent = currentStep === stepNumber

  let className = 'w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium '

  if (isComplete) {
    className += 'bg-green-500 text-white'
  } else if (isCurrent) {
    className += 'bg-blue-600 text-white'
  } else {
    className += 'bg-gray-200 text-gray-600'
  }

  return <div className={className}>{stepNumber}</div>
}

interface StepConnectorProps {
  isComplete: boolean
}

function StepConnector({ isComplete }: StepConnectorProps) {
  return (
    <div
      className={`h-1 flex-1 mx-2 ${isComplete ? 'bg-green-500' : 'bg-gray-200'}`}
    />
  )
}
