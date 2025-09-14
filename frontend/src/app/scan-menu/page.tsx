"use client"

import { useState, useRef, useCallback } from "react"
import { useRouter } from "next/navigation"
import { useSession } from "next-auth/react"
import { MobileLayout } from "@/components/ui/mobile-layout"
import { LoadingSpinner } from "@/components/ui/loading-spinner"
import { ErrorMessage } from "@/components/ui/error-message"
import { RecommendationDisplay } from "@/components/recommendation-display"


interface MenuUploadResponse {
  success: boolean
  message: string
  restaurant_id: string
  restaurant_data: {
    id: string
    name: string
    menu_items: Array<{
      name: string
      price: string
      category: string
    }>
  }
}

import { components } from "@/types/api-types"
type RecommendationResponse = components["schemas"]["RecommendationResponse"]
type FoodItemRecommendation = components["schemas"]["FoodItemRecommendation"]

export default function ScanMenuPage() {
  const { data: session } = useSession()
  const router = useRouter()
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  
  const [isProcessing, setIsProcessing] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [cameraActive, setCameraActive] = useState(false)
  const [capturedImage, setCapturedImage] = useState<string | null>(null)
  const [stream, setStream] = useState<MediaStream | null>(null)
  const [restaurantName, setRestaurantName] = useState("")
  const [scannedRestaurant, setScannedRestaurant] = useState<{id: string, name: string} | null>(null)

  const startCamera = useCallback(async () => {
    setCameraActive(true);
    try {
      setError(null)
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: { 
          facingMode: 'environment', 
          width: { ideal: 1920 },
          height: { ideal: 1080 }
        }
        // video: true
      })
      
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream
        // Force playback for Safari/Chrome mobile
        await videoRef.current.play().catch(err => {
          console.error("Video play failed:", err)
          setError("Unable to start video preview.")
        })
        setStream(mediaStream)
        setCameraActive(true)
      }
    } catch (err) {
      setError("Camera access denied. Please enable camera permissions or upload an image instead.")
      console.error("Camera error:", err)
    }
  }, [])

  const stopCamera = useCallback(() => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop())
      setStream(null)
    }
    setCameraActive(false)
  }, [stream])

  const scanMenu = useCallback(async () => {
    if (!videoRef.current || !canvasRef.current || !session?.access_token) return

    if (!restaurantName.trim()) {
      setError("Please enter a restaurant name")
      return
    }

    setIsProcessing(true)
    setError(null)

    try {
      const video = videoRef.current
      const canvas = canvasRef.current
      const context = canvas.getContext('2d')

      if (!context) return

      canvas.width = video.videoWidth
      canvas.height = video.videoHeight
      context.drawImage(video, 0, 0, canvas.width, canvas.height)

      canvas.toBlob(async (blob) => {
        if (!blob) return

        try {
          const formData = new FormData()
          formData.append('image', blob, 'menu.jpg')
          formData.append('name', restaurantName.trim())
          formData.append('latitude', '42.3601') 
          formData.append('longitude', '-71.0589')
          formData.append('city', 'Boston')

          const uploadResponse = await fetch('/api/upload-menu', {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${session.access_token}`
            },
            body: formData
          })

          if (!uploadResponse.ok) {
            throw new Error(`Upload failed: ${uploadResponse.statusText}`)
          }

          const result: MenuUploadResponse = await uploadResponse.json()
          
          if (result.success) {
            stopCamera();
            setIsProcessing(false);
            setScannedRestaurant({
              id: result.restaurant_id,
              name: result.restaurant_data.name
            });
          } else {
            throw new Error(result.message || 'Upload failed')
          }
        } catch (err) {
          setError(err instanceof Error ? err.message : 'Failed to process menu')
          setIsProcessing(false)
        }
      }, 'image/jpeg', 0.8)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to capture image')
      setIsProcessing(false)
    }
  }, [session?.access_token, router, stopCamera, restaurantName])

  const handleFileUpload = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file && file.type.startsWith('image/')) {
      const imageUrl = URL.createObjectURL(file)
      setCapturedImage(imageUrl)
      setError(null)
    } else {
      setError("Please select a valid image file")
    }
  }, [])

  const uploadMenu = useCallback(async () => {
    if (!capturedImage || !session?.access_token) return

    setIsProcessing(true)
    setError(null)

    try {
      const response = await fetch(capturedImage)
      const blob = await response.blob()
      
      const formData = new FormData()
      formData.append('image', blob, 'menu.jpg')
      formData.append('name', restaurantName.trim()) //up
      formData.append('latitude', '42.3601') 
      formData.append('longitude', '-71.0589')
      formData.append('city', 'Boston')

      const uploadResponse = await fetch('/api/upload-menu', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${session.access_token}`
        },
        body: formData
      })

      if (!uploadResponse.ok) {
        throw new Error(`Upload failed: ${uploadResponse.statusText}`)
      }

      const result: MenuUploadResponse = await uploadResponse.json()
      
      if (result.success) {
        stopCamera();
        setIsProcessing(false);
        setScannedRestaurant({
          id: result.restaurant_id,
          name: result.restaurant_data.name
        });
      } else {
        throw new Error(result.message || 'Upload failed')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to process menu')
      setIsProcessing(false)
    }
  
  }, [capturedImage, session?.access_token, router])

  const retakePhoto = useCallback(() => {
    if (capturedImage) {
      URL.revokeObjectURL(capturedImage)
      setCapturedImage(null)
    }
    setError(null)
  }, [capturedImage])

  const handleRecommendationClose = () => {
    setScannedRestaurant(null)
  }

  const handleRecommendationApprove = (item: FoodItemRecommendation) => {
    localStorage.setItem(`recommendation_${item.id}`, JSON.stringify(item))
    router.push(`/recommendation/${item.id}`)
  }

  if (isProcessing) {
    return (
      <MobileLayout>
        <div className="flex-1 flex items-center justify-center">
          <LoadingSpinner message="Processing your menu..." />
        </div>
      </MobileLayout>
    )
  }

  return (
    <MobileLayout>
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
        <button
          onClick={() => router.back()}
          className="p-2 hover:bg-gray-100 rounded-full transition-colors"
        >
          <svg viewBox="0 0 24 24" fill="none" className="w-6 h-6">
            <path d="M19 12H5M12 19l-7-7 7-7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </button>
        <h1 className="text-xl font-semibold">Scan Menu</h1>
        <div className="w-10"></div>
      </div>

      <div className="flex-1 px-6 py-6">
        {error && (
          <div className="mb-6">
            <ErrorMessage message={error} title="Camera Error" />
          </div>
        )}

        {!capturedImage && !cameraActive && (
          <div className="text-center space-y-6">
            <div>
              <h2 className="text-2xl font-semibold text-black mb-2">Scan a Menu</h2>
              <p className="text-gray-600">Take a photo of a restaurant menu to get AI-powered recommendations</p>
            </div>

            <div className="space-y-4">
              <div className="text-left">
                <label htmlFor="restaurant-name" className="block text-sm font-medium text-gray-700 mb-2">
                  Restaurant Name
                </label>
                <input
                  id="restaurant-name"
                  type="text"
                  value={restaurantName}
                  onChange={(e) => setRestaurantName(e.target.value)}
                  placeholder="Enter restaurant name..."
                  className="w-full px-4 py-3 border border-gray-300 rounded-[13px] focus:ring-2 focus:ring-[#212528] focus:border-transparent outline-none"
                />
              </div>

              <button
                onClick={startCamera}
                disabled={!restaurantName.trim()}
                className="w-full bg-[#212528] text-white py-4 px-6 rounded-[13px] font-semibold hover:bg-[#2a2f33] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Open Camera
              </button>
              
              <div className="text-center text-gray-500">or</div>
              
              <button
                onClick={() => fileInputRef.current?.click()}
                disabled={!restaurantName.trim()}
                className="w-full bg-white border-2 border-[#212528] text-[#212528] py-4 px-6 rounded-[13px] font-semibold hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed disabled:border-gray-300 disabled:text-gray-400"
              >
                Upload from Gallery
              </button>
              
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={handleFileUpload}
                className="hidden"
              />
            </div>
          </div>
        )}

        {cameraActive && (
          <div className="space-y-6">
            <div className="mb-4">
              <p className="text-sm text-gray-600 text-center">
                Scanning menu for: <span className="font-semibold text-black">{restaurantName}</span>
              </p>
            </div>
            
            <div className="relative bg-black rounded-[13px] overflow-hidden">
              <video
                ref={videoRef}
                autoPlay
                playsInline
                muted
                className="w-full h-80 object-cover"
              />
              <div className="absolute inset-0 border-2 border-white/30 rounded-[13px] pointer-events-none">
                <div className="absolute top-4 left-4 w-8 h-8 border-l-2 border-t-2 border-white"></div>
                <div className="absolute top-4 right-4 w-8 h-8 border-r-2 border-t-2 border-white"></div>
                <div className="absolute bottom-4 left-4 w-8 h-8 border-l-2 border-b-2 border-white"></div>
                <div className="absolute bottom-4 right-4 w-8 h-8 border-r-2 border-b-2 border-white"></div>
              </div>
            </div>
            
            <div className="flex gap-4">
              <button
                onClick={stopCamera}
                className="flex-1 bg-gray-200 text-gray-700 py-3 px-6 rounded-[13px] font-semibold hover:bg-gray-300 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={scanMenu}
                disabled={isProcessing}
                className="flex-1 bg-[#212528] text-white py-3 px-6 rounded-[13px] font-semibold hover:bg-[#2a2f33] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isProcessing ? 'Scanning...' : 'Scan'}
              </button>
            </div>
          </div>
        )}

        {capturedImage && (
          <div className="space-y-6">
            <div className="bg-gray-100 rounded-[13px] overflow-hidden">
              <img
                src={capturedImage}
                alt="Captured menu"
                className="w-full h-80 object-cover"
              />
            </div>
            
            <div className="flex gap-4">
              <button
                onClick={retakePhoto}
                className="flex-1 bg-gray-200 text-gray-700 py-3 px-6 rounded-[13px] font-semibold hover:bg-gray-300 transition-colors"
              >
                Retake
              </button>
              <button
                onClick={uploadMenu}
                className="flex-1 bg-[#212528] text-white py-3 px-6 rounded-[13px] font-semibold hover:bg-[#2a2f33] transition-colors"
              >
                Process Menu
              </button>
            </div>
          </div>
        )}

        <canvas ref={canvasRef} className="hidden" />

        {scannedRestaurant && (
          <RecommendationDisplay
            restaurantId={scannedRestaurant.id}
            restaurantName={scannedRestaurant.name}
            onClose={handleRecommendationClose}
            onApprove={handleRecommendationApprove}
          />
        )}
      </div>
    </MobileLayout>
  )
}
