import * as React from "react"
import { type VariantProps, cva } from "class-variance-authority"
import { cn } from "@/lib/utils"
import "@/components/ui/8bit/styles/retro.css"

export const textareaVariants = cva("", {
  variants: {
    font: {
      normal: "",
      retro: "retro",
    },
    variant: {
      default: "bg-input",
      void: "bg-terminal-void",
    },
  },
  defaultVariants: {
    font: "normal",
    variant: "default",
  },
})

export interface BitTextareaProps
  extends React.TextareaHTMLAttributes<HTMLTextAreaElement>,
    VariantProps<typeof textareaVariants> {
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
      font,
      variant,
      autoGrow = true,
      minHeight = 96,
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
      <div className="relative mx-1.5 my-1.5">
        <div
          className={cn(
            // The field itself clears its outline, so focus has to be drawn
            // here or keyboard users get no indicator at all. Same ring the
            // buttons use, square because the system has no radius.
            "relative p-0! focus-within:ring-2 focus-within:ring-primary",
            variant === "void" ? "bg-terminal-void text-foreground" : "bg-input text-foreground",
            font === "retro" && "retro"
          )}
        >
          <textarea
            ref={combinedRef}
            value={value}
            onChange={onChange}
            style={{ minHeight: `${minHeight}px` }}
            className={cn(
              "w-full resize-none overflow-hidden bg-transparent p-4 font-terminal text-xl text-foreground placeholder:text-muted-foreground focus:outline-none [scrollbar-width:none] [&::-webkit-scrollbar]:hidden",
              className
            )}
            {...props}
          />

          {/* Stepped 8-bit outer borders (4px = 1 unit) */}
          <span className="pointer-events-none absolute -top-1 left-1 right-1 h-1 bg-[#000000]" aria-hidden="true" />
          <span className="pointer-events-none absolute -bottom-1 left-1 right-1 h-1 bg-[#000000]" aria-hidden="true" />
          <span className="pointer-events-none absolute top-1 bottom-1 -left-1 w-1 bg-[#000000]" aria-hidden="true" />
          <span className="pointer-events-none absolute top-1 bottom-1 -right-1 w-1 bg-[#000000]" aria-hidden="true" />

          {/* 8-bit stepped corner pixels - fully connecting border to green background */}
          <span className="pointer-events-none absolute top-0 left-0 size-1 bg-[#000000]" aria-hidden="true" />
          <span className="pointer-events-none absolute top-0 right-0 size-1 bg-[#000000]" aria-hidden="true" />
          <span className="pointer-events-none absolute bottom-0 left-0 size-1 bg-[#000000]" aria-hidden="true" />
          <span className="pointer-events-none absolute bottom-0 right-0 size-1 bg-[#000000]" aria-hidden="true" />

          {/* 8-bit hard drop shadow */}
          <span className="pointer-events-none absolute -bottom-2 left-2 right-0 h-1 bg-[#000000]" aria-hidden="true" />
          <span className="pointer-events-none absolute top-2 bottom-0 -right-2 w-1 bg-[#000000]" aria-hidden="true" />
          <span className="pointer-events-none absolute -bottom-1 -right-1 size-1 bg-[#000000]" aria-hidden="true" />
        </div>
      </div>
    )
  }
)

BitTextarea.displayName = "BitTextarea"
export { BitTextarea as Textarea }
