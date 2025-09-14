import { signOut } from "next-auth/react"

interface ActionButtonsProps {
  hasProfile: boolean
  onUpdatePreferences: () => void
}

export function ActionButtons({ hasProfile, onUpdatePreferences }: ActionButtonsProps) {
  return (
    <div className="flex space-x-4">
      {hasProfile && (
        <button
          onClick={onUpdatePreferences}
          className="rounded-full border border-solid border-blue-600 transition-colors flex items-center justify-center bg-white hover:bg-blue-50 text-blue-600 font-medium text-lg h-12 px-8"
        >
          Update Preferences
        </button>
      )}
      <button
        onClick={() => signOut()}
        className="rounded-full border border-solid border-transparent transition-colors flex items-center justify-center bg-red-600 hover:bg-red-700 text-white font-medium text-lg h-12 px-8"
      >
        Sign Out
      </button>
    </div>
  )
}