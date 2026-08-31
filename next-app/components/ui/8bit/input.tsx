import * as React from "react"
import { type VariantProps, cva } from "class-variance-authority"
import { cn } from "@/lib/utils"
import "@/components/ui/8bit/styles/retro.css"

export const inputVariants = cva("", {
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

export interface BitInputProps
  extends React.InputHTMLAttributes<HTMLInputElement>,
    VariantProps<typeof inputVariants> {}

export const BitInput = React.forwardRef<HTMLInputElement, BitInputProps>(
  ({ className, font, variant, ...props }, ref) => {
    return (
      <div className="relative mx-1.5 my-1.5">
        <div
          className={cn(
            "relative p-0!",
            variant === "void" ? "bg-terminal-void text-foreground" : "bg-input text-foreground",
            font === "retro" && "retro"
          )}
        >
          <input
            ref={ref}
            className={cn(
              "w-full bg-transparent p-3 font-terminal text-xl text-foreground placeholder:text-muted-foreground/60 focus:outline-none",
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

BitInput.displayName = "BitInput"
export { BitInput as Input }

