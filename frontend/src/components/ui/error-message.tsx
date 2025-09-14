interface ErrorMessageProps {
  message: string
  title?: string
}

export function ErrorMessage({ message, title = "Error" }: ErrorMessageProps) {
  return (
    <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
      {title}: {message}
    </div>
  )
}