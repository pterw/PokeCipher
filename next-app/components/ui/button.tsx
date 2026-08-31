import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"

import { cn } from "@/lib/utils"

// Hard edges throughout: the retro Game Boy look allows no rounded corners.
const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap border font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        default: "border-transparent bg-poke-yellow text-primary-foreground hover:bg-poke-yellow/90",
        secondary: "border-border bg-secondary text-secondary-foreground hover:bg-secondary/80",
        outline: "border-border bg-transparent text-foreground hover:bg-secondary",
        ghost: "border-transparent bg-transparent text-foreground hover:bg-secondary",
      },
      size: {
        // VT323 has an x-height near half its em, so it reads far smaller than the
        // nominal size: text-sm renders like ~10px of a normal face. DESIGN.md's
        // body scale is 18-20px and the hero already follows it; these sizes are
        // what made the tool below look like a different, smaller application.
        default: "h-10 px-4 text-lg",
        sm: "h-9 px-3 text-base",
        lg: "h-11 px-6 text-xl",
        icon: "size-9",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, type = "button", ...props }, ref) => (
    <button
      ref={ref}
      type={type}
      className={cn(buttonVariants({ variant, size, className }))}
      {...props}
    />
  )
)
Button.displayName = "Button"

export { Button, buttonVariants }
