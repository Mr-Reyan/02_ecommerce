'use client'

import React, { useState } from 'react'
import Image from 'next/image'
import Link from 'next/link'
import {
  ChevronDown,
  Package,
  Calendar,
  Clock,
  CheckCircle2,
  AlertCircle,
  Truck,
  Layers,
} from 'lucide-react'
import { Separator } from '@/components/ui/separator'

const BASE_URL = process.env.NEXT_PUBLIC_API_URL

const STATUS_CONFIG = {
  PAID: {
    label: 'Paid',
    color: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    icon: CheckCircle2,
  },
  DELIVERED: {
    label: 'Delivered',
    color: 'bg-blue-50 text-blue-700 border-blue-200',
    icon: Package,
  },
  SHIPPED: {
    label: 'Shipped',
    color: 'bg-purple-50 text-purple-700 border-purple-200',
    icon: Truck,
  },
  PENDING: {
    label: 'Pending',
    color: 'bg-amber-50 text-amber-700 border-amber-200',
    icon: Clock,
  },
  CANCELLED: {
    label: 'Cancelled',
    color: 'bg-rose-50 text-rose-700 border-rose-200',
    icon: AlertCircle,
  },
}

export default function OrderCard({ order }) {
  const [isOpen, setIsOpen] = useState(false)

  const statusConfig = STATUS_CONFIG[order.status] || STATUS_CONFIG.PENDING
  const StatusIcon = statusConfig.icon

  const formattedDate = order.created_at
    ? new Date(order.created_at).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
      })
    : 'Recent'

  const formattedTime = order.created_at
    ? new Date(order.created_at).toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
      })
    : ''

  const subtotal = Number(order.total_price || 0)

  return (
    <div className="border border-gray-200 rounded-2xl bg-white shadow-xs overflow-hidden transition-all duration-200 hover:border-gray-300">
      {/* Accordion Header / Trigger */}
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        aria-expanded={isOpen}
        className="w-full text-left p-4 sm:p-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4 cursor-pointer hover:bg-gray-50/50 transition-colors"
      >
        <div className="flex items-start sm:items-center gap-3 sm:gap-4 flex-1 min-w-0">
          <div className="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center text-black shrink-0">
            <Package className="w-5 h-5 text-gray-700" />
          </div>

          <div className="flex flex-col min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="font-bold text-base sm:text-lg text-black">
                Order #{order.id}
              </span>
              <span
                className={`inline-flex items-center gap-1 text-xs font-semibold px-2.5 py-0.5 rounded-full border ${statusConfig.color}`}
              >
                <StatusIcon className="w-3 h-3" />
                <span>{statusConfig.label}</span>
              </span>
            </div>

            <div className="flex items-center gap-3 text-xs sm:text-sm text-gray-500 mt-1">
              <span className="flex items-center gap-1">
                <Calendar className="w-3.5 h-3.5" />
                {formattedDate} {formattedTime && `• ${formattedTime}`}
              </span>
              <span>•</span>
              <span className="flex items-center gap-1">
                <Layers className="w-3.5 h-3.5" />
                {order.item_count || order.items?.length || 0} items
              </span>
            </div>
          </div>
        </div>

        <div className="flex items-center justify-between sm:justify-end gap-4 shrink-0 border-t sm:border-t-0 pt-3 sm:pt-0 border-gray-100">
          <div className="text-left sm:text-right">
            <p className="text-xs text-gray-400 font-medium">Total Amount</p>
            <p className="text-lg sm:text-xl font-bold text-black">
              ${subtotal.toFixed(2)}
            </p>
          </div>

          <div
            className={`w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center text-gray-600 transition-transform duration-300 ${
              isOpen ? 'rotate-180 bg-gray-200 text-black' : ''
            }`}
          >
            <ChevronDown className="w-4 h-4" />
          </div>
        </div>
      </button>

      {/* Accordion Collapsible Content */}
      <div
        className={`grid transition-all duration-300 ease-in-out ${
          isOpen ? 'grid-rows-[1fr] opacity-100' : 'grid-rows-[0fr] opacity-0'
        }`}
      >
        <div className="overflow-hidden">
          <div className="px-4 sm:px-6 pb-6 pt-2">
            <Separator className="mb-4" />

            <h3 className="text-xs uppercase font-semibold text-gray-400 tracking-wider mb-3">
              Items in this order
            </h3>

            {/* Items List */}
            <div className="flex flex-col divide-y divide-gray-100">
              {order.items?.map((item) => {
                const rawImg = item.product_image
                const picUrl = rawImg?.startsWith('http')
                  ? rawImg
                  : rawImg
                    ? `${BASE_URL || ''}${rawImg.startsWith('/') ? '' : '/'}${rawImg}`
                    : '/img/newarrivals/shirt1.png'

                const itemPrice = Number(item.price_at_purchase || 0)
                const lineTotal = item.line_total || itemPrice * item.quantity

                return (
                  <div
                    key={item.id}
                    className="py-3.5 first:pt-1 last:pb-1 flex items-center gap-3 sm:gap-4 justify-between"
                  >
                    {/* Item Image + Details */}
                    <div className="flex items-center gap-3 sm:gap-4 min-w-0 flex-1">
                      <Link
                        href={`/store/item/${item.product}`}
                        className="shrink-0 relative overflow-hidden rounded-xl bg-gray-100 hover:opacity-90 transition-opacity border border-gray-100"
                      >
                        <Image
                          src={picUrl}
                          alt={item.product_name || 'Product'}
                          width={72}
                          height={72}
                          className="w-14 h-14 sm:w-16 sm:h-16 object-cover"
                        />
                      </Link>

                      <div className="flex flex-col min-w-0 flex-1">
                        <Link
                          href={`/store/item/${item.product}`}
                          className="font-bold text-sm sm:text-base text-black hover:underline truncate"
                        >
                          {item.product_name}
                        </Link>

                        <div className="flex items-center gap-2 text-xs sm:text-sm text-gray-500 mt-1 flex-wrap">
                          {item.size && (
                            <span className="bg-gray-100 px-2 py-0.5 rounded-md font-medium text-gray-700">
                              Size: {item.size}
                            </span>
                          )}
                          {item.color && (
                            <span className="bg-gray-100 px-2 py-0.5 rounded-md font-medium text-gray-700 capitalize">
                              Color: {item.color}
                            </span>
                          )}
                          <span className="text-gray-400">
                            Qty: <strong className="text-gray-700">{item.quantity}</strong>
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* Pricing */}
                    <div className="text-right shrink-0">
                      <p className="font-bold text-sm sm:text-base text-black">
                        ${lineTotal.toFixed(2)}
                      </p>
                      <p className="text-xs text-gray-400">
                        ${itemPrice.toFixed(2)} each
                      </p>
                    </div>
                  </div>
                )
              })}
            </div>

            {/* Order Cost Breakdown */}
            <div className="mt-4 pt-4 border-t border-gray-100 flex flex-col gap-2">
              <div className="flex justify-between text-xs sm:text-sm text-gray-500">
                <span>Subtotal</span>
                <span className="font-medium text-black">${subtotal.toFixed(2)}</span>
              </div>
              <div className="flex justify-between text-xs sm:text-sm text-gray-500">
                <span>Delivery Fee</span>
                <span className="font-medium text-green-600">Free</span>
              </div>
              <Separator className="my-1" />
              <div className="flex justify-between text-sm sm:text-base font-bold text-black">
                <span>Order Total</span>
                <span>${subtotal.toFixed(2)}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
