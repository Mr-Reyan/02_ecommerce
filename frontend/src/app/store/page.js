'use client'

import React, { useState, Suspense } from 'react'
import Link from 'next/link'
import { ChevronRight } from 'lucide-react'
import { ShopItems } from './shopItems'
import { ItemFilters } from './ItemFilters'
import PaginationBtns from './pagination/pagination'
import { useQuery } from '@tanstack/react-query'
import { getProducts } from '@/services/product.service'
import { useSearchParams, useRouter } from 'next/navigation'
import { Sheet, SheetContent } from '@/components/ui/sheet'

const StoreContent = () => {
  const searchParams = useSearchParams()
  const router = useRouter()
  const [isMobileFilterOpen, setIsMobileFilterOpen] = useState(false)

  const pageParam = Number(searchParams.get('page'))
  const currentPage = !isNaN(pageParam) && pageParam > 0 ? pageParam : 1

  const pageSizeParam = Number(searchParams.get('page_size'))
  const currentPageSize =
    !isNaN(pageSizeParam) && pageSizeParam > 0 ? pageSizeParam : 20

  const minPrice = searchParams.get('min_price') || ''
  const maxPrice = searchParams.get('max_price') || ''
  const color = searchParams.get('color') || ''
  const category = searchParams.get('category') || ''
  const size = searchParams.get('size') || ''
  const style = searchParams.get('style') || ''

  const currentFilters = {
    min_price: minPrice,
    max_price: maxPrice,
    color,
    category,
    size,
    style,
  }

  const { data, isLoading } = useQuery({
    queryKey: [
      'products',
      currentPage,
      currentPageSize,
      minPrice,
      maxPrice,
      color,
      category,
      size,
      style,
    ],
    queryFn: () =>
      getProducts(currentPage, currentPageSize, currentFilters),
  })

  // Helper to build URL with query params
  const buildPageUrl = (pageNumber) => {
    const params = new URLSearchParams()
    params.set('page', pageNumber)
    params.set('page_size', currentPageSize)
    if (minPrice) params.set('min_price', minPrice)
    if (maxPrice) params.set('max_price', maxPrice)
    if (color) params.set('color', color)
    if (category) params.set('category', category)
    if (size) params.set('size', size)
    if (style) params.set('style', style)
    return `/store?${params.toString()}`
  }

  const prevLink = currentPage > 1 ? buildPageUrl(currentPage - 1) : null
  const nextLink =
    data?.next || (data?.total_pages && currentPage < data.total_pages)
      ? buildPageUrl(currentPage + 1)
      : null

  const handlePageSizeChange = (newPageSize) => {
    const params = new URLSearchParams(searchParams.toString())
    params.set('page', '1')
    params.set('page_size', newPageSize)
    router.push(`/store?${params.toString()}`)
  }

  const handleApplyFilters = (newFilters) => {
    const params = new URLSearchParams()
    params.set('page', '1')
    params.set('page_size', currentPageSize)

    if (newFilters.min_price) params.set('min_price', newFilters.min_price)
    if (newFilters.max_price) params.set('max_price', newFilters.max_price)
    if (newFilters.color) params.set('color', newFilters.color)
    if (newFilters.category) params.set('category', newFilters.category)
    if (newFilters.size) params.set('size', newFilters.size)
    if (newFilters.style) params.set('style', newFilters.style)

    router.push(`/store?${params.toString()}`)
  }

  return (
    <div className="w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 flex flex-col gap-6">
      {/* Breadcrumbs */}
      <nav aria-label="Breadcrumb" className="flex items-center gap-1.5 text-sm text-gray-500">
        <Link href="/" className="hover:text-black transition-colors">
          Home
        </Link>
        <ChevronRight className="w-4 h-4 text-gray-400" />
        <span className="text-black font-medium">Casual</span>
      </nav>

      {/* Main Content Layout (Sidebar + Products Grid) */}
      <div className="flex flex-col lg:flex-row gap-6 lg:gap-8 items-start">
        {/* Desktop Filter Sidebar */}
        <aside className="hidden lg:block w-[280px] xl:w-[295px] shrink-0 border border-gray-200 rounded-3xl p-5 bg-white shadow-xs">
          <ItemFilters
            key={`desktop-${JSON.stringify(currentFilters)}`}
            initialFilters={currentFilters}
            onApply={handleApplyFilters}
          />
        </aside>

        {/* Mobile Filter Bottom Sheet */}
        <Sheet open={isMobileFilterOpen} onOpenChange={setIsMobileFilterOpen}>
          <SheetContent
            side="bottom"
            showCloseButton={false}
            className="rounded-t-[32px] max-h-[85vh] overflow-y-auto px-5 py-6 bg-white border-t border-gray-200"
          >
            <ItemFilters
              key={`mobile-${JSON.stringify(currentFilters)}`}
              isMobile
              initialFilters={currentFilters}
              onApply={handleApplyFilters}
              onClose={() => setIsMobileFilterOpen(false)}
            />
          </SheetContent>
        </Sheet>

        {/* Products Grid & Pagination */}
        <main className="flex-1 min-w-0 flex flex-col gap-8 w-full">
          {isLoading ? (
            <div className="py-24 flex items-center justify-center text-gray-400">
              Loading products...
            </div>
          ) : (
            <ShopItems
              totalPages={data?.total_pages}
              totalProd={data?.total}
              currentPage={currentPage}
              pageSize={currentPageSize}
              items={data?.results}
              onOpenMobileFilters={() => setIsMobileFilterOpen(true)}
            />
          )}

          <PaginationBtns
            nextLink={nextLink}
            prevLink={prevLink}
            pageSize={currentPageSize}
            onPageSizeChange={handlePageSizeChange}
          />
        </main>
      </div>
    </div>
  )
}

const StorePage = () => {
  return (
    <Suspense fallback={<div className="p-10 text-center">Loading store...</div>}>
      <StoreContent />
    </Suspense>
  )
}

export default StorePage