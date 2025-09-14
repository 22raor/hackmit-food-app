"use client"

import React, { useState, useEffect } from 'react';
import Vapi from '@vapi-ai/web';
import { useSession } from 'next-auth/react';
import { getUserProfile } from '@/lib/api';
import { components } from '@/types/api-types';

type TasteProfileResponse = components["schemas"]["TasteProfileResponse"];

interface VapiWidgetProps {
  apiKey: string;
  assistantId: string;
  userId?: string;
  config?: Record<string, unknown>;
}

const VapiWidget: React.FC<VapiWidgetProps> = ({
  apiKey,
  assistantId,
  userId,
  config = {}
}) => {
  const { data: session } = useSession();
  const [vapi, setVapi] = useState<Vapi | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [callStatus, setCallStatus] = useState<'idle' | 'connecting' | 'active' | 'ended'>('idle');
  const [tasteProfile, setTasteProfile] = useState<TasteProfileResponse | null>(null);
  const [cartData, setCartData] = useState<any>(null);
  const [showCart, setShowCart] = useState(false);

  // Fetch taste profile when component mounts
  useEffect(() => {
    if (session?.access_token && userId) {
      getUserProfile(session.access_token, userId)
        .then(setTasteProfile)
        .catch(console.error);
    }
  }, [session?.access_token, userId]);

  useEffect(() => {
    const vapiInstance = new Vapi(apiKey);
    setVapi(vapiInstance);

    // Event listeners
    vapiInstance.on('call-start', () => {
      console.log('Call started');
      setIsConnected(true);
      setCallStatus('active');
    });

    vapiInstance.on('call-end', () => {
      console.log('Call ended');
      setIsConnected(false);
      setIsSpeaking(false);
      setCallStatus('ended');
      // Use the authenticated user ID if available, otherwise generate a session ID
      const finalUserId = userId || `session_${Date.now()}`;
      fetchUserCart(finalUserId);
    });

    vapiInstance.on('speech-start', () => {
      console.log('Assistant started speaking');
      setIsSpeaking(true);
    });

    vapiInstance.on('speech-end', () => {
      console.log('Assistant stopped speaking');
      setIsSpeaking(false);
    });

    vapiInstance.on('message', (message) => {
      console.log('VAPI message:', message);
      // Handle call end and extract user_id if provided
      if (message.type === 'function-call' && message.functionCall?.name === 'endCall') {
        const args = message.functionCall.parameters;
        // Prefer the authenticated user ID, then the message user_id, then fallback
        const finalUserId = userId || args?.user_id || `session_${Date.now()}`;
        fetchUserCart(finalUserId);
      }
    });

    vapiInstance.on('error', (error) => {
      console.error('Vapi error:', error);
      setCallStatus('idle');
      setIsConnected(false);
      setIsSpeaking(false);
    });

    return () => {
      vapiInstance?.stop();
    };
  }, [apiKey]);

  const fetchUserCart = async (userId: string) => {
    try {
      const response = await fetch(`/api/item-cart?user_id=${userId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        console.log('Cart data:', data);
        setCartData(data.user_cart);
        setShowCart(true);
      }
    } catch (error) {
      console.error('Failed to fetch cart:', error);
    }
  };

  const createPersonalizedSystemPrompt = (profile: TasteProfileResponse) => {
    const { profile: tasteProfile } = profile;

    let personalizedPrompt = `You are an AI voice assistant that helps someone order a meal. You have access to the user's taste profile and should use it to provide personalized recommendations.

USER'S TASTE PROFILE:
`;

    if (tasteProfile.dietary_restrictions?.length) {
      const restrictions = tasteProfile.dietary_restrictions.map(r =>
        typeof r === 'string' ? r : r.name || String(r)
      );
      personalizedPrompt += `- Dietary Restrictions: ${restrictions.join(', ')}\n`;
    }

    if (tasteProfile.cuisine_preferences?.length) {
      const cuisines = tasteProfile.cuisine_preferences.map(c =>
        typeof c === 'string' ? c : `${c.cuisine_type} (${c.preference_level}/5)`
      );
      personalizedPrompt += `- Preferred Cuisines: ${cuisines.join(', ')}\n`;
    }

    if (tasteProfile.flavor_profile) {
      const flavorProfile = typeof tasteProfile.flavor_profile === 'string'
        ? tasteProfile.flavor_profile
        : `Spicy: ${tasteProfile.flavor_profile.spicy_tolerance}/5, Sweet: ${tasteProfile.flavor_profile.sweet_preference}/5, Salty: ${tasteProfile.flavor_profile.salty_preference}/5, Sour: ${tasteProfile.flavor_profile.sour_preference}/5, Umami: ${tasteProfile.flavor_profile.umami_preference}/5, Bitter: ${tasteProfile.flavor_profile.bitter_tolerance}/5`;
      personalizedPrompt += `- Flavor Profile: ${flavorProfile}\n`;
    }

    if (tasteProfile.liked_foods?.length) {
      const likedFoods = tasteProfile.liked_foods.map(f =>
        typeof f === 'string' ? f : f.name || String(f)
      );
      personalizedPrompt += `- Liked Foods: ${likedFoods.join(', ')}\n`;
    }

    if (tasteProfile.disliked_foods?.length) {
      const dislikedFoods = tasteProfile.disliked_foods.map(f =>
        typeof f === 'string' ? f : f.name || String(f)
      );
      personalizedPrompt += `- Disliked Foods: ${dislikedFoods.join(', ')}\n`;
    }

    if (tasteProfile.price_range_preference) {
      personalizedPrompt += `- Price Range Preference: ${tasteProfile.price_range_preference}\n`;
    }

    personalizedPrompt += `
INSTRUCTIONS:
IMMEDIATELY START WITH RESTAURANT RECOMMENDATIONS: Based on the user's taste profile above, immediately suggest 2-3 specific restaurants that match their preferences. Say something like "Based on your taste preferences, I have some great restaurant suggestions for you!" Then list restaurants with cuisine type and brief description.

Restaurant selection: Once the user picks a restaurant, recommend 1–2 top items first that align with their preferences. If they say no, adjust and suggest different items — but never overwhelm them with too many choices at once.

Building the meal: Add items to cart as they confirm, and guide them toward a complete meal (main, side, drink, or dessert if they want). Make sure to capture the user_id when adding items to cart.

Finishing up: Once they're satisfied, confirm the order clearly and finalize. Before ending the call, make sure you have a user_id ${userId ? `(use "${userId}")` : '(create one if needed like "session_" + timestamp)'} and end the call with that user_id so the frontend can fetch their cart.

Style rules:
- LEAD WITH RESTAURANT RECOMMENDATIONS based on their profile - don't ask what they want first
- Keep recommendations short and conversational (avoid technical junk like image URLs, IDs, or long descriptions)
- Personalize based on their taste profile and what they say yes/no to
- Never list more than 2–3 options at once
- Keep the focus on food, not filler details
- Do not make up restaurant names - use real restaurants when possible
- Do not repeat ratings or the same info multiple times
- ALWAYS respect their dietary restrictions and preferences
- When ending the call, pass along the user_id so the frontend can display their cart`;

    console.log("Personalized Prompt:", personalizedPrompt);
    return personalizedPrompt;
  };

  const startCall = async () => {
    if (vapi) {
      try {
        setCallStatus('connecting');

        if (tasteProfile) {
          // Create personalized assistant with taste profile
          const personalizedConfig = {
            name: "Restaurant Picker",
            model: {
              provider: "openai" as const,
              model: "gpt-4.1" as const,
              maxTokens: 5000,
              toolIds: [
                "fa2e0a34-2513-4a91-b17d-35ae3995c40e",
                      "fbe04aae-1d00-4445-ae69-c74725738add",
                      "e5dfc3c4-297d-4b9c-9455-c0e166281ec0",
                      "211b0c10-d5cb-4713-b795-f11423b9ce85"
              ],
              messages: [
                {
                  role: "system" as const,
                  content: createPersonalizedSystemPrompt(tasteProfile)
                }
              ]
            },
            voice: {
              provider: "vapi" as const,
              voiceId: "Cole" as const
            },
            firstMessage: "Hi! I'm your personal food assistant and I know your taste preferences. Based on your profile, I have some great restaurant recommendations for you!",
            voicemailMessage: "Please call back when you're available.",
            endCallFunctionEnabled: true,
            endCallMessage: "Goodbye.",
            transcriber: {
              provider: "deepgram" as const,
              model: "nova-2" as const,
              language: "en" as const
            },
            firstMessageMode: "assistant-speaks-first-with-model-generated-message" as const
          };

          await vapi.start(personalizedConfig);
        } else {
          // Fallback to default assistant if no taste profile
          await vapi.start(assistantId);
        }
      } catch (error) {
        console.error('Failed to start call:', error);
        setCallStatus('idle');
      }
    }
  };

  const endCall = () => {
    if (vapi) {
      vapi.stop();
    }
    setCallStatus('ended');
    setIsConnected(false);
    setIsSpeaking(false);
  };

  return (
    <div className="flex-1 flex flex-col">
      {/* Status Display */}
      <div className="flex-1 flex flex-col items-center justify-center px-8 py-12">
        <div className="text-center mb-8">
          <div className="w-24 h-24 bg-[#212528] rounded-full mx-auto mb-6 flex items-center justify-center relative">
            {/* Pulse animation for active call */}
            {isConnected && (
              <div className="absolute inset-0 bg-[#212528] rounded-full animate-ping opacity-20"></div>
            )}

            <svg viewBox="0 0 24 24" fill="white" className="w-12 h-12 relative z-10">
              {callStatus === 'active' ? (
                isSpeaking ? (
                  // Microphone with sound waves
                  <g>
                    <path d="M12 2a3 3 0 0 0-3 3v6a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/>
                    <path d="M19 10v1a7 7 0 0 1-14 0v-1"/>
                    <line x1="12" x2="12" y1="19" y2="23"/>
                    <line x1="8" x2="16" y1="23" y2="23"/>
                    {/* Sound waves */}
                    <path d="M15 8c0-1.7-1.3-3-3-3s-3 1.3-3 3" className="animate-pulse"/>
                    <path d="M17 6c0-2.8-2.2-5-5-5s-5 2.2-5 5" className="animate-pulse" style={{animationDelay: '0.2s'}}/>
                  </g>
                ) : (
                  // Regular microphone
                  <g>
                    <path d="M12 2a3 3 0 0 0-3 3v6a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/>
                    <path d="M19 10v1a7 7 0 0 1-14 0v-1"/>
                    <line x1="12" x2="12" y1="19" y2="23"/>
                    <line x1="8" x2="16" y1="23" y2="23"/>
                  </g>
                )
              ) : (
                // Phone icon
                <path d="M6.62 10.79c1.44 2.83 3.76 5.14 6.59 6.59l2.2-2.2c.27-.27.67-.36 1.02-.24 1.12.37 2.33.57 3.57.57.55 0 1 .45 1 1V20c0 .55-.45 1-1 1-9.39 0-17-7.61-17-17 0-.55.45-1 1-1h3.5c.55 0 1 .45 1 1 0 1.25.2 2.45.57 3.57.11.35.03.74-.25 1.02l-2.2 2.2z"/>
              )}
            </svg>
          </div>

          <h2 className="text-[24px] font-semibold text-black mb-2">
            {callStatus === 'idle' && "Ready to Help"}
            {callStatus === 'connecting' && "Connecting..."}
            {callStatus === 'active' && (isSpeaking ? "Assistant Speaking" : "Listening...")}
            {callStatus === 'ended' && "Call Ended"}
          </h2>

          <p className="text-[#555555] text-[16px] max-w-xs mx-auto">
            {callStatus === 'idle' && "Start a voice conversation to get personalized food recommendations"}
            {callStatus === 'connecting' && "Setting up your food assistant..."}
            {callStatus === 'active' && (isSpeaking ? "Your assistant is speaking" : "Speak naturally about what you want to eat")}
            {callStatus === 'ended' && "Thanks for using our service!"}
          </p>
        </div>

        {/* Cart Display */}
        {showCart && cartData && (
          <div className="w-full max-w-md mb-6">
            <div className="bg-white border border-[#e6e6e6] rounded-[13px] p-4">
              <div className="flex justify-between items-center mb-3">
                <h3 className="text-[16px] font-semibold text-black">Your Order</h3>
                <button
                  onClick={() => setShowCart(false)}
                  className="text-[#555555] hover:text-black"
                >
                  ×
                </button>
              </div>
              {cartData.cart_items && cartData.cart_items.length > 0 ? (
                <div className="space-y-2">
                  {cartData.cart_items.map((item: any, i: number) => (
                    <div key={i} className="flex justify-between items-center py-2 border-b border-[#f5f6f8] last:border-b-0">
                      <div>
                        <div className="font-medium text-black text-[14px]">{item.name || `Item ${i + 1}`}</div>
                        {item.restaurant && (
                          <div className="text-[#555555] text-[12px]">{item.restaurant}</div>
                        )}
                      </div>
                      {item.price && (
                        <div className="text-black font-medium text-[14px]">${item.price}</div>
                      )}
                    </div>
                  ))}
                  <div className="pt-2 flex justify-between items-center font-semibold">
                    <span>Total Items: {cartData.total_items}</span>
                  </div>
                </div>
              ) : (
                <p className="text-[#555555] text-[14px]">No items in cart yet.</p>
              )}
            </div>
          </div>
        )}

        {/* Action Button */}
        <div className="w-full max-w-sm">
          {!isConnected ? (
            <button
              onClick={startCall}
              disabled={callStatus === 'connecting'}
              className="w-full h-[56px] bg-[#212528] text-white rounded-[13px] font-medium text-[16px] hover:bg-[#313538] disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-3"
            >
              <svg viewBox="0 0 24 24" fill="currentColor" className="w-6 h-6">
                <path d="M12 2a3 3 0 0 0-3 3v6a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/>
                <path d="M19 10v1a7 7 0 0 1-14 0v-1"/>
                <line x1="12" x2="12" y1="19" y2="23" stroke="currentColor" strokeWidth="2"/>
                <line x1="8" x2="16" y1="23" y2="23" stroke="currentColor" strokeWidth="2"/>
              </svg>
              {callStatus === 'connecting' ? "Connecting..." : "Start Voice Order"}
            </button>
          ) : (
            <button
              onClick={endCall}
              className="w-full h-[56px] bg-red-600 text-white rounded-[13px] font-medium text-[16px] hover:bg-red-700 transition-colors flex items-center justify-center gap-3"
            >
              <svg viewBox="0 0 24 24" fill="currentColor" className="w-6 h-6">
                <path d="M16 8v8a1 1 0 01-1 1H9a1 1 0 01-1-1V8a1 1 0 011-1h6a1 1 0 011 1z"/>
              </svg>
              End Call
            </button>
          )}
        </div>

        {/* Instructions */}
        {callStatus === 'idle' && (
          <div className="mt-8 text-center">
            <p className="text-[#555555] text-[14px] mb-2">How it works:</p>
            <ul className="text-[#555555] text-[12px] space-y-1">
              <li>• Speak naturally about what you want to eat</li>
              <li>• Share your preferences and dietary needs</li>
              <li>• Get personalized recommendations</li>
              <li>• Make your final selection</li>
            </ul>
          </div>
        )}

        {/* Connection Status Indicator */}
        {isConnected && (
          <div className="mt-4 flex items-center gap-2">
            <div
              className={`w-2 h-2 rounded-full ${isSpeaking ? 'bg-red-500 animate-pulse' : 'bg-green-500'}`}
            ></div>
            <span className="text-[12px] text-[#555555]">
              {isSpeaking ? 'Assistant speaking' : 'Ready to listen'}
            </span>
          </div>
        )}
      </div>
    </div>
  );
};

export default VapiWidget;
