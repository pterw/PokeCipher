import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"

import { cn } from "@/lib/utils"

// Hard edges throughout: the retro Game Boy look allows no rounded corners.
const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap border font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        default: "border-poke-yellow bg-poke-yellow text-primary-foreground hover:bg-poke-yellow/90",
        secondary: "border-border bg-secondary text-secondary-foreground hover:bg-secondary/80",
        outline: "border-border bg-transparent text-foreground hover:bg-secondary",
        ghost: "border-transparent bg-transparent text-foreground hover:bg-secondary",
      },
      size: {
        default: "h-9 px-4 text-sm",
        sm: "h-8 px-3 text-xs",
        lg: "h-10 px-6 text-sm",
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
