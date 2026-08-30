import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"

import { cn } from "@/lib/utils"

export const bitButtonVariants = cva(
  "relative inline-flex items-center justify-center font-pixel text-xs tracking-wider uppercase select-none transition-transform active:translate-y-1 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-poke-yellow disabled:opacity-40 disabled:pointer-events-none",
  {
    variants: {
      variant: {
        yellow:
          "bg-poke-yellow text-[#0f380f] hover:brightness-105",
        secondary:
          "bg-secondary text-foreground hover:bg-muted",
        outline:
          "bg-card text-foreground hover:bg-secondary hover:text-poke-yellow",
        ghost:
          "bg-transparent text-foreground hover:bg-secondary hover:text-poke-yellow",
      },
      size: {
        default: "px-4 py-2.5 h-11",
        sm: "px-3 py-1.5 h-9 text-[10px]",
        lg: "px-6 py-3 h-13 text-sm",
        icon: "h-10 w-10 p-0",
      },
    },
    defaultVariants: {
      variant: "secondary",
      size: "default",
    },
  }
)

export interface BitButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof bitButtonVariants> {
  asChild?: boolean
}

function ButtonDecorations({
  variant,
}: {
  variant: BitButtonProps["variant"]
}) {
  if (variant === "ghost") return null

  return (
    <span
      aria-hidden="true"
      className="pointer-events-none contents"
      data-slot="button-decorations"
    >
      {/* Outer 8-bit pixel stepped border */}
      <span className="absolute -top-1 left-1 right-1 h-1 bg-[#000000]" />
      <span className="absolute -bottom-1 left-1 right-1 h-1 bg-[#000000]" />
      <span className="absolute top-1 bottom-1 -left-1 w-1 bg-[#000000]" />
      <span className="absolute top-1 bottom-1 -right-1 w-1 bg-[#000000]" />

      {/* 8-bit Corner pixels */}
      <span className="absolute top-0 left-0 size-1 bg-[#000000]" />
      <span className="absolute top-0 right-0 size-1 bg-[#000000]" />
      <span className="absolute bottom-0 left-0 size-1 bg-[#000000]" />
      <span className="absolute bottom-0 right-0 size-1 bg-[#000000]" />

      {/* 8-bit Hard Drop Shadow */}
      <span className="absolute -bottom-2 left-2 right-0 h-1 bg-[#000000]" />
      <span className="absolute top-2 bottom-0 -right-2 w-1 bg-[#000000]" />
      <span className="absolute -bottom-1 -right-1 size-1 bg-[#000000]" />

      {/* Bevel Highlights / Shadows */}
      {variant === "yellow" ? (
        <>
          <span className="absolute top-0 left-0 right-0 h-1 bg-white/30" />
          <span className="absolute top-1 left-0 w-1 h-2 bg-white/30" />
          <span className="absolute bottom-0 left-0 right-0 h-1 bg-black/25" />
          <span className="absolute bottom-1 right-0 w-1 h-2 bg-black/25" />
        </>
      ) : variant === "secondary" ? (
        <>
          <span className="absolute top-0 left-0 right-0 h-1 bg-[#477d47]/60" />
          <span className="absolute bottom-0 left-0 right-0 h-1 bg-[#071a07]/60" />
        </>
      ) : null}
    </span>
  )
}

export const BitButton = React.forwardRef<HTMLButtonElement, BitButtonProps>(
  ({ className, variant, size, children, ...props }, ref) => {
    return (
      <button
        ref={ref}
        className={cn(bitButtonVariants({ variant, size, className }), "mx-1 my-1")}
        {...props}
      >
        <span className="relative z-10 flex items-center justify-center gap-2">
          {children}
        </span>
        <ButtonDecorations variant={variant} />
      </button>
    )
  }
)

BitButton.displayName = "BitButton"
