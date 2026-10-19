// import React from 'react'
// import Card from '../home/card'

// import {
//   Select,
//   SelectContent,
//   SelectGroup,
//   SelectItem,
//   SelectLabel,
//   SelectTrigger,
//   SelectValue,
// } from "@/components/ui/select"
// import Link from 'next/link'

// const items = [
//   { label: "Most Popular", value: "popular" },
//   // { label: "Banana", value: "banana" },
//   // { label: "Blueberry", value: "blueberry" },
//   // { label: "Grapes", value: "grapes" },
//   // { label: "Pineapple", value: "pineapple" },
// ]

// // export function Select() {
// //   return (
// //     <Select items={items}>
// //       <SelectTrigger className="w-full max-w-48">
// //         <SelectValue />
// //       </SelectTrigger>
// //       <SelectContent>
// //         <SelectGroup>
// //           <SelectLabel>Fruits</SelectLabel>
// //           {items.map((item) => (
// //             <SelectItem key={item.value} value={item.value}>
// //               {item.label}
// //             </SelectItem>
// //           ))}
// //         </SelectGroup>
// //       </SelectContent>
// //     </Select>
// //   )
// // }

// export function ShopItems() {
//   return (
//     <div className="w-full">
//   {/* Header */}
//   <div className="mb-6 flex items-center justify-between">
//     <p className="text-[32px] font-bold">Casual</p>

//     <div className="flex items-center gap-3">
//       <p className="whitespace-nowrap text-gray-400">
//         Showing 1-10 of 100 Products
//       </p>

//       <p className="whitespace-nowrap text-gray-400">
//         Sort by:
//       </p>

//       <Select defaultValue="popular" items={items}>
//         <SelectTrigger className="w-48">
//           <SelectValue />
//         </SelectTrigger>

//         <SelectContent>
//           <SelectGroup>
//             <SelectLabel>Sort By</SelectLabel>

//             {items.map((item) => (
//               <SelectItem key={item.value} value={item.value}>
//                 {item.label}
//               </SelectItem>
//             ))}
//           </SelectGroup>
//         </SelectContent>
//       </Select>
//     </div>
//   </div>

//   {/* Products */}
//   <div className="flex flex-wrap gap-5">
//     <Link href="/store/item">
//       <Card
//         img="/img/newarrivals/shirt1.png"
//         title="Sleeve Stripped T-shirt"
//         price={130}
//         rating={4.5}
//       />
//     </Link>

//     <Card
//       img="/img/newarrivals/shirt1.png"
//       title="Sleeve Stripped T-shirt"
//       price={130}
//       rating={4.5}
//     />

//     <Card
//       img="/img/newarrivals/shirt1.png"
//       title="Sleeve Stripped T-shirt"
//       price={130}
//       rating={4.5}
//     />

//     <Card
//       img="/img/newarrivals/shirt1.png"
//       title="Sleeve Stripped T-shirt"
//       price={130}
//       rating={4.5}
//     />

//     <Card
//       img="/img/newarrivals/shirt1.png"
//       title="Sleeve Stripped T-shirt"
//       price={130}
//       rating={4.5}
//     />

//     <Card
//       img="/img/newarrivals/shirt1.png"
//       title="Sleeve Stripped T-shirt"
//       price={130}
//       rating={4.5}
//     />

//     <Card
//       img="/img/newarrivals/shirt1.png"
//       title="Sleeve Stripped T-shirt"
//       price={130}
//       rating={4.5}
//     />

//     <Card
//       img="/img/newarrivals/shirt1.png"
//       title="Sleeve Stripped T-shirt"
//       price={130}
//       rating={4.5}
//     />
//   </div>
// </div>
//   )
// }

import React from 'react'
import Card from '../home/card'

import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import Link from 'next/link'

import { SlidersHorizontal } from 'lucide-react'

const items = [{ label: 'Most Popular', value: 'popular' }]

export function ShopItems({
  totalPages,
  totalProd = 0,
  currentPage = 1,
  pageSize = 20,
  items: products = [],
  onOpenMobileFilters,
}) {
  const total = totalProd || 0
  const start = total > 0 ? (currentPage - 1) * pageSize + 1 : 0
  const end = total > 0 ? Math.min(currentPage * pageSize, total) : 0
  const showingText =
    total === 0
      ? 'Showing 0 Products'
      : `Showing ${start}-${end} of ${total} Products`

  return (
    <div className="w-full">
      <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center justify-between w-full sm:w-auto">
          <p className="text-2xl font-bold md:text-[32px]">Casual</p>
          {/* Mobile Filter Button next to title or count */}
          <div className="flex items-center gap-3 sm:hidden">
            <p className="text-xs text-gray-400">{showingText}</p>
            <button
              type="button"
              onClick={onOpenMobileFilters}
              aria-label="Open filters"
              className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center text-black hover:bg-gray-200 transition-colors shrink-0"
            >
              <SlidersHorizontal className="w-4 h-4" />
            </button>
          </div>
        </div>

        <div className="hidden sm:flex items-center justify-between gap-2 sm:justify-end sm:gap-3">
          <p className="whitespace-nowrap text-sm text-gray-400">
            {showingText}
          </p>

          <button
            type="button"
            onClick={onOpenMobileFilters}
            aria-label="Open filters"
            className="lg:hidden w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center text-black hover:bg-gray-200 transition-colors shrink-0"
          >
            <SlidersHorizontal className="w-4 h-4" />
          </button>

          <p className="whitespace-nowrap text-sm text-gray-400 hidden md:block">
            Sort by:
          </p>

          <Select defaultValue="popular">
            <SelectTrigger className="w-36 sm:w-44">
              <SelectValue />
            </SelectTrigger>

            <SelectContent>
              <SelectGroup>
                <SelectLabel>Sort By</SelectLabel>

                {items.map((item) => (
                  <SelectItem key={item.value} value={item.value}>
                    {item.label}
                  </SelectItem>
                ))}
              </SelectGroup>
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Empty State */}
      {products.length === 0 && (
        <div className="py-20 text-center flex flex-col items-center justify-center gap-3 bg-gray-50 rounded-2xl border border-dashed border-gray-200">
          <p className="text-lg font-bold text-gray-700">No products found</p>
          <p className="text-sm text-gray-400">Try adjusting your filters or price range</p>
        </div>
      )}

      {/* Products */}
      <div className="flex flex-wrap gap-x-4 gap-y-8 sm:gap-x-5">
        {products.map((product) => (
          <Link
            key={product.id}
            href={`/store/item/${product.id}`}
            // href="/store/item"
            className="
            w-[calc(50%-8px)]
            sm:w-[calc(50%-10px)]
            md:w-[calc(31%)]
            lg:w-[calc(33.333%-14px)]
            xl:w-[calc(25%-15px)]
            "
          >
            <Card
              img={product.images?.[0]?.image || product.image || '/img/newarrivals/shirt1.png'}
              title={product.name}
              price={product.price}
              rating={product.rating}
            />
          </Link>
        ))}
      </div>
    </div>
  )
}
