'use client'
import { Trash2 } from 'lucide-react'
import Image from 'next/image'
import Counter from '../store/item/counter'
import { deleteCartItem, updateCart } from '@/services/cart.service'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
const BASE_URL = process.env.NEXT_PUBLIC_API_URL
export default function CartCard({
  photo,
  name,
  price,
  quantity,
  size,
  color,
  max,
  stock,
  product_id,
}) {
  const queryClient = useQueryClient()
  const availableStock = stock !== undefined ? stock : (max ?? 99)

  const PicURL = photo?.startsWith('http')
    ? photo
    : photo
      ? `${BASE_URL || ''}${photo}`
      : '/img/newarrivals/shirt1.png'

  const updateMutation = useMutation({
    mutationFn: ({ newQuantity, product_id }) =>
      updateCart(newQuantity, product_id),
    onMutate: async ({ newQuantity, product_id }) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: ['cart'] })

      // Snapshot previous cart
      const previousCart = queryClient.getQueryData(['cart'])

      // Optimistically update quantity in query cache immediately (0ms)
      queryClient.setQueryData(['cart'], (old) => {
        if (!old || !old.items) return old
        return {
          ...old,
          items: old.items.map((item) =>
            item.product?.id === product_id
              ? { ...item, quantity: newQuantity }
              : item
          ),
        }
      })

      return { previousCart }
    },
    onError(err, variables, context) {
      // Rollback on error
      if (context?.previousCart) {
        queryClient.setQueryData(['cart'], context.previousCart)
      }
      toast.error(err?.message || 'Error updating cart!')
    },
    onSettled() {
      // Ensure synchronized state with backend
      queryClient.invalidateQueries({ queryKey: ['cart'] })
    },
  })

  const deleteMutation = useMutation({
    mutationFn: () => deleteCartItem(product_id),
    onMutate: async () => {
      await queryClient.cancelQueries({ queryKey: ['cart'] })
      const previousCart = queryClient.getQueryData(['cart'])

      queryClient.setQueryData(['cart'], (old) => {
        if (!old || !old.items) return old
        return {
          ...old,
          items: old.items.filter((item) => item.product?.id !== product_id),
        }
      })

      return { previousCart }
    },
    onSuccess() {
      toast.success('Item removed from cart!')
    },
    onError(err, variables, context) {
      if (context?.previousCart) {
        queryClient.setQueryData(['cart'], context.previousCart)
      }
      toast.error('Error removing item!')
    },
    onSettled() {
      queryClient.invalidateQueries({ queryKey: ['cart'] })
    },
  })

  const updateQuantity = (newQuantity) => {
    if (newQuantity > availableStock) {
      toast.error(`Only ${availableStock} items left in stock for size ${size || ''}`)
      return
    }
    updateMutation.mutate({
      newQuantity: newQuantity,
      product_id: product_id,
    })
  }

  const deleteItem = () => {
    deleteMutation.mutate()
  }

  return (
    <div className="flex gap-3 sm:gap-4 p-4 border-b border-gray-100 last:border-0">
      {/* Product Image */}
      <div className="shrink-0">
        <Image
          src={PicURL}
          width={180}
          height={240}
          className="sm:h-[150px] sm:w-[135px] h-full w-[80px] rounded-lg object-cover"
          loading="eager"
          alt={name || 'Cart item'}
        />
      </div>

      <div className="flex min-w-0 flex-1 flex-col justify-between">
        <div>
          <div className="flex items-start justify-between gap-4">
            <p className="text-sm sm:text-xl font-bold whitespace-nowrap text-ellipsis overflow-hidden">
              {name}
            </p>

            <button
              type="button"
              aria-label="Remove item"
              className="shrink-0"
              onClick={deleteItem}
              disabled={deleteMutation.isPending}
            >
              <Trash2 className="w-4 h-4 md:w-5 md:h-5 cursor-pointer text-red-500 hover:text-red-700 transition-colors" />
            </button>
          </div>

          <div className="sm:mt-2 mt-0.5 flex flex-wrap items-center gap-x-4 gap-y-1">
            <p className="text-sm sm:text-base text-gray-500">
              <span className="text-black font-medium">Size:</span> {size || 'Standard'}
            </p>

            <p className="text-sm sm:text-base text-gray-500">
              <span className="text-black font-medium">Color:</span> {color || 'Default'}
            </p>

            {availableStock !== undefined && (
              <span
                className={`text-xs font-medium ${
                  availableStock > 0
                    ? availableStock <= 5
                      ? 'text-amber-600 bg-amber-50 px-2 py-0.5 rounded-full'
                      : 'text-gray-500'
                    : 'text-red-500 bg-red-50 px-2 py-0.5 rounded-full'
                }`}
              >
                {availableStock > 0 ? `${availableStock} left in stock` : 'Out of stock'}
              </span>
            )}
          </div>
        </div>

        <div className="flex items-center justify-between sm:mt-4 mt-2">
          <p className="text-md sm:text-2xl font-bold">${price.toFixed(2)}</p>

          <Counter
            onChange={updateQuantity}
            value={quantity}
            max={availableStock > 0 ? availableStock : 1}
          />
        </div>
      </div>
    </div>
  )
}
