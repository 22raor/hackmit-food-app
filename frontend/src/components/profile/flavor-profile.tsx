import { components } from "@/types/api-types"

interface FlavorProfileProps {
  flavorProfile: components["schemas"]["FlavorProfile"]
}

export function FlavorProfile({ flavorProfile }: FlavorProfileProps) {
  return (
    <div className="mt-3 pt-3 border-t border-gray-200">
      <p className="text-gray-600 mb-2">Flavor Profile:</p>
      <div className="grid grid-cols-2 gap-2 text-xs">
        <div className="flex justify-between">
          <span>Spicy:</span>
          <span className="font-medium">{flavorProfile.spicy_tolerance}/10</span>
        </div>
        <div className="flex justify-between">
          <span>Sweet:</span>
          <span className="font-medium">{flavorProfile.sweet_preference}/10</span>
        </div>
        <div className="flex justify-between">
          <span>Salty:</span>
          <span className="font-medium">{flavorProfile.salty_preference}/10</span>
        </div>
        <div className="flex justify-between">
          <span>Sour:</span>
          <span className="font-medium">{flavorProfile.sour_preference}/10</span>
        </div>
        <div className="flex justify-between">
          <span>Umami:</span>
          <span className="font-medium">{flavorProfile.umami_preference}/10</span>
        </div>
        <div className="flex justify-between">
          <span>Bitter:</span>
          <span className="font-medium">{flavorProfile.bitter_tolerance}/10</span>
        </div>
      </div>
    </div>
  )
}