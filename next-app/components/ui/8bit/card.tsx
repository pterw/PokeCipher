import * as React from "react"

import { cn } from "@/lib/utils"

export interface BitCardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "card" | "void" | "secondary"
}

export const BitCard = React.forwardRef<HTMLDivElement, BitCardProps>(
  ({ className, variant = "card", children, ...props }, ref) => {
    const bgClass =
      variant === "void"
        ? "bg-terminal-void text-foreground"
        : variant === "secondary"
          ? "bg-secondary text-foreground"
          : "bg-card text-card-foreground"

    return (
      <div className="relative mx-1.5 my-1.5 shadow-[4px_4px_0px_#000000]">
        <div
          ref={ref}
          className={cn(
            "relative border-y-4 border-[#000000] p-4",
            bgClass,
            className
          )}
          {...props}
        >
          {children}
          {/* 8-bit stepped pixel corner overlay */}
          <div
            className="pointer-events-none absolute inset-0 -mx-1 border-x-4 border-[#000000]"
            aria-hidden="true"
          />
        </div>
      </div>
    )
  }
)

BitCard.displayName = "BitCard"
