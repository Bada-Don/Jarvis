"use client"

import { useEffect, useRef, useState } from "react"
import { AnimatePresence, motion } from "motion/react"
import { useOnClickOutside } from "usehooks-ts"

export interface TechItem {
  name: string
  category: string
  logo: React.ReactNode
  description: string
  details: string
  useCase: string
}

export interface TechStackListingProps {
  items: TechItem[]
  className?: string
  onItemClick?: (item: TechItem) => void
}

export default function TechStackListing({
  items,
  className,
  onItemClick,
}: TechStackListingProps) {
  const [activeItem, setActiveItem] = useState<TechItem | null>(null)
  const ref = useRef<HTMLDivElement>(null) as React.RefObject<HTMLDivElement>

  useOnClickOutside(ref, () => setActiveItem(null))

  useEffect(() => {
    function onKeyDown(event: { key: string }) {
      if (event.key === "Escape") {
        setActiveItem(null)
      }
    }

    window.addEventListener("keydown", onKeyDown)
    return () => window.removeEventListener("keydown", onKeyDown)
  }, [])

  return (
    <>
      <AnimatePresence>
        {activeItem ? (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="pointer-events-none fixed inset-0 z-10 bg-black/60 backdrop-blur-sm"
          />
        ) : null}
      </AnimatePresence>

      <AnimatePresence>
        {activeItem ? (
          <>
            <div className="fixed inset-0 z-10 grid place-items-center p-4">
              <motion.div
                className="flex h-fit w-[90%] max-w-lg cursor-pointer flex-col items-start gap-4 overflow-hidden rounded-xl border border-neutral-700 bg-neutral-900 p-6 shadow-xl"
                ref={ref}
                layoutId={`techItem-${activeItem.name}`}
                style={{ borderRadius: 12 }}
              >
                <div className="flex w-full items-center gap-4">
                  <motion.div 
                    layoutId={`techItemLogo-${activeItem.name}`}
                    className="flex h-12 w-12 items-center justify-center rounded-lg bg-neutral-800 text-2xl"
                  >
                    {activeItem.logo}
                  </motion.div>
                  <div className="flex grow items-center justify-between">
                    <div className="flex w-full flex-col gap-0.5">
                      <motion.div
                        className="text-lg font-semibold text-white"
                        layoutId={`techItemName-${activeItem.name}`}
                      >
                        {activeItem.name}
                      </motion.div>
                      <motion.p
                        layoutId={`techItemCategory-${activeItem.name}`}
                        className="text-sm text-gray-400"
                      >
                        {activeItem.category}
                      </motion.p>
                    </div>
                  </div>
                </div>
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0, transition: { duration: 0.05 } }}
                  className="space-y-3"
                >
                  <p className="text-sm text-gray-300">{activeItem.description}</p>
                  <div className="rounded-lg bg-neutral-800 p-3">
                    <p className="text-xs font-medium text-gray-400 mb-1">Technical Details</p>
                    <p className="text-sm text-gray-300">{activeItem.details}</p>
                  </div>
                  <div className="rounded-lg bg-neutral-800 p-3">
                    <p className="text-xs font-medium text-gray-400 mb-1">Use Case in JARVIS</p>
                    <p className="text-sm text-gray-300">{activeItem.useCase}</p>
                  </div>
                </motion.div>
              </motion.div>
            </div>
          </>
        ) : null}
      </AnimatePresence>

      <div className={`relative flex items-start ${className || ""}`}>
        <div className="relative grid w-full grid-cols-2 md:grid-cols-3 gap-4">
          {items.map((item) => (
            <motion.div
              layoutId={`techItem-${item.name}`}
              key={item.name}
              className="group flex cursor-pointer flex-col items-center gap-3 rounded-xl border border-neutral-800 bg-neutral-900 p-6 shadow-sm hover:border-neutral-700 hover:bg-neutral-800/50 transition-colors"
              onClick={() => {
                setActiveItem(item)
                if (onItemClick) onItemClick(item)
              }}
              style={{ borderRadius: 12 }}
            >
              <motion.div 
                layoutId={`techItemLogo-${item.name}`}
                className="flex h-12 w-12 items-center justify-center rounded-lg bg-neutral-800 text-2xl group-hover:bg-neutral-700 transition-colors"
              >
                {item.logo}
              </motion.div>
              <div className="text-center">
                <motion.div
                  className="font-semibold text-white"
                  layoutId={`techItemName-${item.name}`}
                >
                  {item.name}
                </motion.div>
                <motion.div
                  className="text-xs text-gray-500"
                  layoutId={`techItemCategory-${item.name}`}
                >
                  {item.category}
                </motion.div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </>
  )
}
