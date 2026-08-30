import * as React from "react"

import { cn } from "@/lib/utils"

export interface BitTextareaProps
  extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  autoGrow?: boolean
  minHeight?: number
}

export const BitTextarea = React.forwardRef<
  HTMLTextAreaElement,
  BitTextareaProps
>(
  (
    {
      className,
      autoGrow = true,
      minHeight = 120,
      value,
      onChange,
      ...props
    },
    ref
  ) => {
    const internalRef = React.useRef<HTMLTextAreaElement>(null)
    const combinedRef = (ref || internalRef) as React.MutableRefObject<HTMLTextAreaElement | null>

    React.useEffect(() => {
      if (!autoGrow) return
      const el = combinedRef.current
      if (!el) return
      el.style.height = "auto"
      el.style.height = `${Math.max(minHeight, el.scrollHeight)}px`
    }, [value, autoGrow, minHeight, combinedRef])

    return (
      <div className="relative mx-1.5 my-1.5 shadow-[4px_4px_0px_#000000]">
        <div className="relative border-y-4 border-[#000000] bg-input transition-colors focus-within:border-poke-yellow">
          <textarea
            ref={combinedRef}
            value={value}
            onChange={onChange}
            className={cn(
              "w-full resize-none overflow-hidden bg-transparent p-3 font-mono text-lg text-foreground placeholder:text-muted-foreground focus:outline-none [scrollbar-width:none] [&::-webkit-scrollbar]:hidden",
              className
            )}
            {...props}
          />
          {/* 8-bit stepped pixel corner overlay */}
          <div
            className="pointer-events-none absolute inset-0 -mx-1 border-x-4 border-[#000000] transition-colors focus-within:border-poke-yellow"
            aria-hidden="true"
          />
        </div>
      </div>
    )
  }
)

BitTextarea.displayName = "BitTextarea"
