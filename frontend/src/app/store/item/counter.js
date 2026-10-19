'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Minus, Plus, Scale } from 'lucide-react'
export default function Counter({value=1,onChange,max=Infinity}) {
  return (
    <div
      className={`flex gap-1 items-center p-0.5 sm:gap-4 sm:p-2 border rounded-4xl max-w-fit bg-gray-100`}
    >
      <Button
        type="button"
        variant="outline"
        size="icon"
        disabled={value <= 1}
        className="border-0 sm:w-7 sm:h-7 w-4 h-4 disabled:opacity-30 disabled:cursor-not-allowed"
        onClick={() => onChange(Math.max(1, value - 1))}
        aria-label="Decrease count"
      >
        <Minus className=" sm:w-4 sm:h-4 w-3 h-3" />
      </Button>

      <span className="sm:w-12 w-7 text-center text-md sm:text-xl font-bold ">
        {value}
      </span>

      <Button
        type="button"
        variant="outline"
        disabled={value >= max}
        className="border-0 sm:w-7 sm:h-7 w-4 h-4 disabled:opacity-30 disabled:cursor-not-allowed"
        size="icon"
        onClick={() => {
          if (value < max) {
            onChange(value + 1)
          }
        }}
        aria-label="Increase count"
      >
        <Plus className="h-4 w-4 " />
      </Button>
    </div>
  )
}
