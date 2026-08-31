"use client"

import * as React from "react"
import * as SwitchPrimitive from "@radix-ui/react-switch"
import { cn } from "@/lib/utils"
import "@/components/ui/8bit/styles/retro.css"

function Switch({
  className,
  ...props
}: React.ComponentProps<typeof SwitchPrimitive.Root>) {
  return (
    <SwitchPrimitive.Root
      data-slot="switch"
      className={cn(
        "relative inline-flex h-[18px] w-[34px] shrink-0 cursor-pointer items-center p-[2px] border border-[#000000] bg-input shadow-[2px_2px_0px_#000000] transition-colors outline-none data-[state=checked]:bg-poke-yellow data-[state=unchecked]:bg-input disabled:cursor-not-allowed disabled:opacity-40",
        className
      )}
      {...props}
    >
      <SwitchPrimitive.Thumb
        data-slot="switch-thumb"
        className={cn(
          "pointer-events-none block size-3 border border-[#000000] bg-foreground transition-transform data-[state=checked]:translate-x-4 data-[state=checked]:bg-[#0f380f] data-[state=unchecked]:translate-x-0"
        )}
      />

      <span
        className="pointer-events-none absolute inset-0 -my-0.5 border-y-2 border-[#000000]"
        aria-hidden="true"
      />
      <span
        className="pointer-events-none absolute inset-0 -mx-0.5 border-x-2 border-[#000000]"
        aria-hidden="true"
      />
    </SwitchPrimitive.Root>
  )
}

export { Switch }
