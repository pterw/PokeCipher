import * as React from "react"
import { cn } from "@/lib/utils"
import "@/components/ui/8bit/styles/retro.css"

export interface BitCardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "card" | "void" | "secondary"
  font?: "normal" | "retro"
}

export const BitCard = React.forwardRef<HTMLDivElement, BitCardProps>(
  ({ className, variant = "card", font, children, ...props }, ref) => {
    const bgClass =
      variant === "void"
        ? "bg-terminal-void text-foreground"
        : variant === "secondary"
          ? "bg-secondary text-foreground"
          : "bg-card text-card-foreground"

    return (
      <div className="relative mx-1.5 my-1.5">
        <div
          ref={ref}
          className={cn(
            "relative",
            bgClass,
            font === "retro" && "retro",
            className
          )}
          {...props}
        >
          {children}

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
BitCard.displayName = "BitCard"

export const Card = BitCard

export const CardHeader = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex flex-col space-y-1.5 border-b-2 border-[#000000] bg-secondary p-2.5", className)}
    {...props}
  />
))
CardHeader.displayName = "CardHeader"

export const CardTitle = React.forwardRef<
  HTMLHeadingElement,
  React.HTMLAttributes<HTMLHeadingElement>
>(({ className, ...props }, ref) => (
  <h3
    ref={ref}
    className={cn("font-pixel text-xs leading-none tracking-wider text-foreground", className)}
    {...props}
  />
))
CardTitle.displayName = "CardTitle"

export const CardDescription = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLParagraphElement>
>(({ className, ...props }, ref) => (
  <p
    ref={ref}
    className={cn("font-terminal text-sm text-muted-foreground", className)}
    {...props}
  />
))
CardDescription.displayName = "CardDescription"

export const CardContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div ref={ref} className={cn("p-3.5 sm:p-4", className)} {...props} />
))
CardContent.displayName = "CardContent"

export const CardFooter = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex items-center border-t-2 border-[#000000] p-2.5", className)}
    {...props}
  />
))
CardFooter.displayName = "CardFooter"
