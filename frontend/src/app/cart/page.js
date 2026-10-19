'use client'
import React from 'react'
import { IntegralCF } from '@/components/fonts'
import CartCard from './CartCard'
import OrderSummary from './OrderSummary'
import { useQuery } from '@tanstack/react-query'
import { getCart } from '@/services/cart.service'

const CartPage = () => {

  const {data:cart={},isLoading} = useQuery({
    queryKey:['cart'],
    queryFn:getCart
  })
  console.log(cart);
    
  if(isLoading) return <div className='w-full flex items-center justify-center h-screen'>CART PAGE LOADING</div>

  return (
    <div className="md:px-12 p-7">
      <p
        className={`${IntegralCF.className} lg:text-5xl md:text-4xl  sm:text-3xl text-2xl`}
      >
        YOUR CART
      </p>
      <div className="flex flex-col lg:items-start gap-5 mt-4 md:mt-6 lg:flex-row">
        <div className="border-2 border-gray-200 flex-1 rounded-2xl h-130 overflow-y-auto">
          {(!cart?.items || cart.items.length === 0) ? (
            <div className="h-full flex flex-col items-center justify-center p-8 text-center text-gray-500">
              <p className="text-xl font-bold text-black mb-2">Your cart is empty</p>
              <p className="text-sm">Browse our store and add items to your cart.</p>
            </div>
          ) : (
            cart.items.map((item) => {
              const sizeStockMap = item.product?.specifications?.size_stock || {}
              const sizeStock =
                item.size && sizeStockMap[item.size] !== undefined
                  ? sizeStockMap[item.size]
                  : (item.product?.stock?.stock ?? 99)

              return (
                <CartCard
                  key={item.id}
                  name={item.product?.name || 'Product'}
                  price={Number(item.product?.price || 0) * item.quantity}
                  quantity={item.quantity}
                  color={item.color}
                  size={item.size}
                  photo={item.product?.images?.[0]?.image || item.product?.image || ''}
                  max={sizeStock}
                  stock={sizeStock}
                  product_id={item.product?.id}
                />
              )
            })
          )}
        </div>
        <div className="border-2 border-gray-200 flex-1 lg:flex-0 rounded-2xl">
          <OrderSummary />
        </div>
      </div>
    </div>
  )
}

export default CartPage
