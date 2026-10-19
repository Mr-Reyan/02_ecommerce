'use client'

import React, { useState } from 'react'
import {
  SlidersHorizontal,
  ChevronRight,
  ChevronUp,
  ChevronDown,
  Check,
  X,
  RotateCcw,
} from 'lucide-react'
import { Slider } from '@/components/ui/slider'
import { Separator } from '@/components/ui/separator'
import { Button } from '@/components/ui/button'

const COLOR_OPTIONS = [
  { name: 'green', bg: '#00C12B', label: 'Green' },
  { name: 'red', bg: '#F50606', label: 'Red' },
  { name: 'yellow', bg: '#F5DD06', label: 'Yellow' },
  { name: 'orange', bg: '#F57906', label: 'Orange' },
  { name: 'cyan', bg: '#06CAF5', label: 'Cyan' },
  { name: 'blue', bg: '#063AF5', label: 'Blue' },
  { name: 'purple', bg: '#7D06F5', label: 'Purple' },
  { name: 'pink', bg: '#F506A4', label: 'Pink' },
  { name: 'white', bg: '#FFFFFF', border: true, label: 'White' },
  { name: 'black', bg: '#000000', label: 'Black' },
]

const SIZE_OPTIONS = [
  'XX-Small',
  'X-Small',
  'Small',
  'Medium',
  'Large',
  'X-Large',
  'XX-Large',
  '3X-Large',
  '4X-Large',
]

const CATEGORY_OPTIONS = [
  { label: 'T-shirts', value: 'T-Shirts' },
  { label: 'Shorts', value: 'Shorts & Activewear' },
  { label: 'Shirts', value: 'Casual Shirts' },
  { label: 'Hoodie', value: 'Hoodies & Sweatshirts' },
  { label: 'Jeans', value: 'Baggy Trousers' },
]

const DRESS_STYLE_OPTIONS = [
  { label: 'Casual', value: 'Casual' },
  { label: 'Formal', value: 'Formal' },
  { label: 'Party', value: 'Party' },
  { label: 'Gym', value: 'Gym' },
]

export function ItemFilters({
  initialFilters = {},
  onApply,
  onClose,
  isMobile = false,
}) {
  const [selectedCategory, setSelectedCategory] = useState(
    initialFilters.category || ''
  )
  const [priceRange, setPriceRange] = useState([
    initialFilters.min_price ? Number(initialFilters.min_price) : 0,
    initialFilters.max_price ? Number(initialFilters.max_price) : 200,
  ])
  const [selectedColor, setSelectedColor] = useState(initialFilters.color || '')
  const [selectedSize, setSelectedSize] = useState(initialFilters.size || '')
  const [selectedStyle, setSelectedStyle] = useState(initialFilters.style || '')

  // Accordion section collapse state
  const [isPriceOpen, setIsPriceOpen] = useState(true)
  const [isColorOpen, setIsColorOpen] = useState(true)
  const [isSizeOpen, setIsSizeOpen] = useState(true)
  const [isStyleOpen, setIsStyleOpen] = useState(true)

  const handleApply = () => {
    onApply({
      category: selectedCategory,
      min_price: priceRange[0] > 0 ? priceRange[0] : '',
      max_price: priceRange[1] < 200 ? priceRange[1] : '',
      color: selectedColor,
      size: selectedSize,
      style: selectedStyle,
    })
    if (onClose) onClose()
  }

  const handleReset = () => {
    setSelectedCategory('')
    setPriceRange([0, 200])
    setSelectedColor('')
    setSelectedSize('')
    setSelectedStyle('')
    onApply({
      category: '',
      min_price: '',
      max_price: '',
      color: '',
      size: '',
      style: '',
    })
    if (onClose) onClose()
  }

  const hasActiveFilters =
    Boolean(selectedCategory) ||
    priceRange[0] > 0 ||
    priceRange[1] < 200 ||
    Boolean(selectedColor) ||
    Boolean(selectedSize) ||
    Boolean(selectedStyle)

  return (
    <div className="flex flex-col gap-5 w-full">
      {/* Header */}
      <div className="flex items-center justify-between pb-1">
        <h2 className="text-xl font-bold text-black tracking-tight">Filters</h2>
        <div className="flex items-center gap-2">
          {hasActiveFilters && (
            <button
              type="button"
              onClick={handleReset}
              className="text-xs text-muted-foreground hover:text-black flex items-center gap-1 transition-colors mr-1"
              title="Reset all filters"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Reset</span>
            </button>
          )}
          {isMobile ? (
            <button
              type="button"
              onClick={onClose}
              aria-label="Close filters"
              className="p-1 text-gray-500 hover:text-black transition-colors rounded-full"
            >
              <X className="w-5 h-5" />
            </button>
          ) : (
            <SlidersHorizontal className="w-5 h-5 text-gray-400" />
          )}
        </div>
      </div>

      <Separator />

      {/* Category List */}
      <div className="flex flex-col gap-3">
        {CATEGORY_OPTIONS.map((cat) => {
          const isActive = selectedCategory === cat.value
          return (
            <button
              key={cat.value}
              type="button"
              onClick={() =>
                setSelectedCategory(isActive ? '' : cat.value)
              }
              className={`flex items-center justify-between py-1 text-left text-base transition-colors ${
                isActive
                  ? 'font-bold text-black'
                  : 'text-gray-500 hover:text-black'
              }`}
            >
              <span>{cat.label}</span>
              <ChevronRight
                className={`w-4 h-4 transition-transform ${
                  isActive ? 'translate-x-1 text-black font-bold' : 'text-gray-400'
                }`}
              />
            </button>
          )
        })}
      </div>

      <Separator />

      {/* Price Filter Section */}
      <div className="flex flex-col gap-4">
        <button
          type="button"
          onClick={() => setIsPriceOpen(!isPriceOpen)}
          className="flex items-center justify-between w-full font-bold text-lg text-black"
        >
          <span>Price</span>
          {isPriceOpen ? (
            <ChevronUp className="w-4 h-4 text-black" />
          ) : (
            <ChevronDown className="w-4 h-4 text-black" />
          )}
        </button>

        {isPriceOpen && (
          <div className="flex flex-col gap-3 pt-1">
            <Slider
              min={0}
              max={200}
              step={5}
              value={priceRange}
              onValueChange={setPriceRange}
              className="py-2"
            />
            <div className="flex items-center justify-between text-sm font-semibold text-black">
              <span>${priceRange[0]}</span>
              <span>${priceRange[1]}</span>
            </div>
          </div>
        )}
      </div>

      <Separator />

      {/* Colors Section */}
      <div className="flex flex-col gap-4">
        <button
          type="button"
          onClick={() => setIsColorOpen(!isColorOpen)}
          className="flex items-center justify-between w-full font-bold text-lg text-black"
        >
          <span>Colors</span>
          {isColorOpen ? (
            <ChevronUp className="w-4 h-4 text-black" />
          ) : (
            <ChevronDown className="w-4 h-4 text-black" />
          )}
        </button>

        {isColorOpen && (
          <div className="grid grid-cols-5 gap-3 pt-1">
            {COLOR_OPTIONS.map((color) => {
              const isSelected = selectedColor.toLowerCase() === color.name
              return (
                <button
                  key={color.name}
                  type="button"
                  onClick={() =>
                    setSelectedColor(isSelected ? '' : color.name)
                  }
                  style={{ backgroundColor: color.bg }}
                  title={color.label}
                  className={`relative h-9 w-9 rounded-full flex items-center justify-center transition-transform hover:scale-105 ${
                    color.border ? 'border border-gray-300' : ''
                  } ${
                    isSelected
                      ? 'ring-2 ring-offset-2 ring-black shadow-sm scale-105'
                      : ''
                  }`}
                >
                  {isSelected && (
                    <Check
                      className={`w-4 h-4 ${
                        color.name === 'white' || color.name === 'yellow'
                          ? 'text-black'
                          : 'text-white'
                      }`}
                      strokeWidth={3}
                    />
                  )}
                </button>
              )
            })}
          </div>
        )}
      </div>

      <Separator />

      {/* Size Section */}
      <div className="flex flex-col gap-4">
        <button
          type="button"
          onClick={() => setIsSizeOpen(!isSizeOpen)}
          className="flex items-center justify-between w-full font-bold text-lg text-black"
        >
          <span>Size</span>
          {isSizeOpen ? (
            <ChevronUp className="w-4 h-4 text-black" />
          ) : (
            <ChevronDown className="w-4 h-4 text-black" />
          )}
        </button>

        {isSizeOpen && (
          <div className="flex flex-wrap gap-2 pt-1">
            {SIZE_OPTIONS.map((size) => {
              const isSelected = selectedSize === size
              return (
                <button
                  key={size}
                  type="button"
                  onClick={() =>
                    setSelectedSize(isSelected ? '' : size)
                  }
                  className={`rounded-full px-4 py-2 text-sm font-medium transition-colors ${
                    isSelected
                      ? 'bg-black text-white'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  {size}
                </button>
              )
            })}
          </div>
        )}
      </div>

      <Separator />

      {/* Dress Style Section */}
      <div className="flex flex-col gap-4">
        <button
          type="button"
          onClick={() => setIsStyleOpen(!isStyleOpen)}
          className="flex items-center justify-between w-full font-bold text-lg text-black"
        >
          <span>Dress Style</span>
          {isStyleOpen ? (
            <ChevronUp className="w-4 h-4 text-black" />
          ) : (
            <ChevronDown className="w-4 h-4 text-black" />
          )}
        </button>

        {isStyleOpen && (
          <div className="flex flex-col gap-3 pt-1">
            {DRESS_STYLE_OPTIONS.map((style) => {
              const isSelected = selectedStyle === style.value
              return (
                <button
                  key={style.value}
                  type="button"
                  onClick={() =>
                    setSelectedStyle(isSelected ? '' : style.value)
                  }
                  className={`flex items-center justify-between py-1 text-left text-base transition-colors ${
                    isSelected
                      ? 'font-bold text-black'
                      : 'text-gray-500 hover:text-black'
                  }`}
                >
                  <span>{style.label}</span>
                  <ChevronRight
                    className={`w-4 h-4 transition-transform ${
                      isSelected ? 'translate-x-1 text-black font-bold' : 'text-gray-400'
                    }`}
                  />
                </button>
              )
            })}
          </div>
        )}
      </div>

      {/* Apply Filter Button */}
      <div className="pt-2">
        <Button
          type="button"
          onClick={handleApply}
          className="w-full bg-black text-white rounded-full py-6 font-medium text-sm hover:bg-black/90 cursor-pointer shadow-md transition-all active:scale-[0.98]"
        >
          Apply Filter
        </Button>
      </div>
    </div>
  )
}
