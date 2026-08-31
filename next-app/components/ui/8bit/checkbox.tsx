import * as React from "react"

import { cn } from "@/lib/utils"

export interface BitCheckboxProps
  extends Omit<React.InputHTMLAttributes<HTMLInputElement>, "type"> {
  label?: string
}

export const BitCheckbox = React.forwardRef<HTMLInputElement, BitCheckboxProps>(
  ({ className, checked, onChange, disabled, id, ...props }, ref) => {
    return (
      <label
        htmlFor={id}
        className={cn(
          "relative inline-flex cursor-pointer items-center justify-center select-none",
          disabled && "cursor-not-allowed opacity-40",
          className
        )}
      >
        <input
          ref={ref}
          id={id}
          type="checkbox"
          checked={checked}
          onChange={onChange}
          disabled={disabled}
          className="peer sr-only"
          {...props}
        />

        {/* 8-bit stepped pixel frame */}
        <div className="relative flex h-5 w-5 items-center justify-center border-y-2 border-[#000000] bg-input shadow-[2px_2px_0px_#000000] transition-colors peer-focus-visible:ring-2 peer-focus-visible:ring-primary">
          {/* Extended X borders for stepped pixel corners */}
          <div
            className="pointer-events-none absolute inset-0 -mx-0.5 border-x-2 border-[#000000]"
            aria-hidden="true"
          />

          {/* 8-bit pixel checkmark fill */}
          {checked && (
            <span className="size-2.5 bg-primary shadow-[1px_1px_0px_#000000]" />
          )}
        </div>
      </label>
    )
  }
)

BitCheckbox.displayName = "BitCheckbox"
