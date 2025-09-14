import { ProfileSummary } from "./profile-summary"
import { FlavorProfile } from "./flavor-profile"
import { components } from "@/types/api-types"

interface UserWelcomeProps {
  user: {
    first_name: string
  }
  profile?: components["schemas"]["TasteProfileResponse"] | null
}

export function UserWelcome({ user, profile }: UserWelcomeProps) {
  return (
    <div className="bg-white text-gray-900 rounded-lg p-6 shadow-lg mb-6">
      <h2 className="text-2xl font-semibold mb-4">Welcome back, {user.first_name}!</h2>
      {profile && (
        <div>
          <ProfileSummary profile={profile.profile} />
          {profile.profile.flavor_profile && (
            <FlavorProfile flavorProfile={profile.profile.flavor_profile} />
          )}
        </div>
      )}
    </div>
  )
}