"use client"

import { ReactNode } from "react"

interface MobileLayoutProps {
  children: ReactNode
  showStatusBar?: boolean
}

export function MobileLayout({ children, showStatusBar = true }: MobileLayoutProps) {
  const StatusBar = () => (
    <div className="flex justify-between items-center h-[54px] px-4 bg-[#f5f6f8]">
      <div className="w-[138px] flex justify-center">
        <span className="font-semibold text-[17px] text-black">9:41</span>
      </div>
      <div className="w-[143px]"></div>
    </div>
  )

  return (
    <div className="mobile-container">
      {showStatusBar && <StatusBar />}
      <div className="flex-1 flex flex-col">
        {children}
      </div>
      {/* Home indicator */}
      <div className="w-[115px] h-[5px] bg-[#212528] rounded-[25px] mx-auto mt-auto mb-4"></div>
    </div>
  )
}