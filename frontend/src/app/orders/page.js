'use client'

import React from 'react'
import Link from 'next/link'
import { ChevronRight, ShoppingBag, PackageOpen, ArrowRight } from 'lucide-react'
import { IntegralCF } from '@/components/fonts'
import { useQuery } from '@tanstack/react-query'
import { getOrders } from '@/services/order.service'
import OrderCard from './OrderCard'
import { Button } from '@/components/ui/button'

export default function OrdersPage() {
  const { data: orders = [], isLoading, isError } = useQuery({
    queryKey: ['orders'],
    queryFn: getOrders,
    staleTime: 1000 * 60 * 5, // 5 minutes fresh in client cache
  })

  return (
    <div className="w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 flex flex-col gap-6">
      {/* Breadcrumbs */}
      <nav
        aria-label="Breadcrumb"
        className="flex items-center gap-1.5 text-sm text-gray-500"
      >
        <Link href="/" className="hover:text-black transition-colors">
          Home
        </Link>
        <ChevronRight className="w-4 h-4 text-gray-400" />
        <span className="text-black font-medium">Orders</span>
      </nav>

      {/* Page Title */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
        <h1
          className={`${IntegralCF.className} text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-bold tracking-tight text-black`}
        >
          YOUR ORDERS
        </h1>

        {!isLoading && orders.length > 0 && (
          <p className="text-sm text-gray-500">
            Total Orders: <strong className="text-black">{orders.length}</strong>
          </p>
        )}
      </div>

      {/* Main Content */}
      {isLoading ? (
        <div className="flex flex-col gap-4">
          {[1, 2, 3].map((n) => (
            <div
              key={n}
              className="h-28 w-full rounded-2xl bg-gray-100 animate-pulse border border-gray-200"
            />
          ))}
        </div>
      ) : isError ? (
        <div className="py-20 text-center flex flex-col items-center justify-center gap-4 bg-gray-50 rounded-3xl border border-dashed border-gray-200 p-8">
          <div className="w-14 h-14 rounded-full bg-red-50 flex items-center justify-center text-red-500">
            <ShoppingBag className="w-7 h-7" />
          </div>
          <p className="text-lg font-bold text-black">Unable to load orders</p>
          <p className="text-sm text-gray-500 max-w-md">
            There was an error fetching your orders. Please check your connection and try again.
          </p>
          <Button
            onClick={() => window.location.reload()}
            className="rounded-full bg-black text-white px-6"
          >
            Retry
          </Button>
        </div>
      ) : orders.length === 0 ? (
        /* Zero / Empty State */
        <div className="py-20 text-center flex flex-col items-center justify-center gap-4 bg-gray-50 rounded-3xl border border-dashed border-gray-200 p-8">
          <div className="w-16 h-16 rounded-full bg-gray-100 flex items-center justify-center text-gray-400">
            <PackageOpen className="w-8 h-8" />
          </div>
          <div className="flex flex-col gap-1 max-w-sm">
            <p className="text-xl font-bold text-black">No orders found</p>
            <p className="text-sm text-gray-500">
              You haven&apos;t placed any orders yet. Start exploring our store to find clothes you love.
            </p>
          </div>
          <Button
            asChild
            className="mt-2 rounded-full bg-black text-white px-8 py-6 text-sm font-medium hover:bg-black/90 shadow-sm"
          >
            <Link href="/store" className="flex items-center gap-2">
              <span>Start Shopping</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
          </Button>
        </div>
      ) : (
        /* Orders List */
        <div className="flex flex-col gap-4">
          {orders.map((order) => (
            <OrderCard key={order.id} order={order} />
          ))}
        </div>
      )}
    </div>
  )
}
