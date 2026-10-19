'use client'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Separator } from '@/components/ui/separator'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Tag, Loader2, ArrowRight, CreditCard } from 'lucide-react'
import React, { useRef, useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getCart } from '@/services/cart.service'
import { checkoutOrder } from '@/services/order.service'
import { toast } from 'sonner'

export default function OrderSummary() {
  const queryClient = useQueryClient()
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [selectedPaymentToken, setSelectedPaymentToken] = useState('tok_success')
  const idempotencyKeyRef = useRef(null)

  const { data: cart, isLoading } = useQuery({
    queryKey: ['cart'],
    queryFn: getCart,
  })

  const placeOrderMutation = useMutation({
    mutationFn: async () => {
      const [result] = await Promise.all([
        checkoutOrder(idempotencyKeyRef.current, selectedPaymentToken),
        new Promise((resolve) => setTimeout(resolve, 1000)),
      ])
      return result
    },
    onSuccess: (data) => {
      toast.success(data?.message || 'Order placed successfully!')
      setIsDialogOpen(false)
      // Invalidate cart and products queries so inventory updates everywhere
      queryClient.invalidateQueries({ queryKey: ['cart'] })
      queryClient.invalidateQueries({ queryKey: ['products'] })
      queryClient.invalidateQueries({ queryKey: ['product'] })
      queryClient.invalidateQueries({ queryKey: ['orders'] })
      // Reset for next order
      idempotencyKeyRef.current = null
      setSelectedPaymentToken('tok_success')
    },
    onError: (err) => {
      const errorMsg = err?.message || 'Failed to place order. Please try again.'
      toast.error(errorMsg)
      setIsDialogOpen(false)
      // Don't reset idempotency key on error - user might want to retry
    },
  })

  const items = cart?.items || []
  const hasItems = items.length > 0

  const subtotal = items.reduce(
    (sum, item) => sum + Number(item.product?.price || 0) * (item.quantity || 1),
    0
  )

  // As requested: 0% discount and $0 delivery fee
  const discount = 0
  const deliveryFee = 0
  const total = hasItems ? subtotal - discount + deliveryFee : 0

  const handlePlaceOrder = () => {
    if (!hasItems) {
      toast.error('Your cart is empty. Please add items before placing an order!')
      return
    }

    // Client-side pre-check for any out-of-stock items before checkout
    for (const item of items) {
      const sizeStockMap = item.product?.specifications?.size_stock || {}
      const availableStock =
        item.size && sizeStockMap[item.size] !== undefined
          ? sizeStockMap[item.size]
          : (item.product?.stock?.stock ?? 99)

      if (availableStock <= 0) {
        toast.error(
          `Cannot place order: "${item.product?.name || 'Item'}" (${item.size || 'Standard'}) is out of stock. Please remove it from your cart.`
        )
        return
      }

      if (item.quantity > availableStock) {
        toast.error(
          `Cannot place order: "${item.product?.name || 'Item'}" quantity (${item.quantity}) exceeds available stock (${availableStock}).`
        )
        return
      }
    }

    // Generate a new idempotency key for this checkout attempt
    idempotencyKeyRef.current = crypto.randomUUID()
    setIsDialogOpen(true)
  }

  const handleConfirmPayment = () => {
    placeOrderMutation.mutate()
  }

  return (
    <div className="text-md sm:text-lg p-5 md:min-w-100 flex flex-col justify-between gap-6">
      <p className="font-bold sm:text-2xl text-xl">Order Summary</p>

      <div className="flex flex-col gap-4">
        <p className="flex justify-between">
          <span className="text-gray-500">Subtotal</span>
          <span className="font-bold">${subtotal.toFixed(2)}</span>
        </p>
        <p className="flex justify-between">
          <span className="text-gray-500">Discount (-0%)</span>
          <span className="font-bold text-gray-500">-${discount.toFixed(2)}</span>
        </p>
        <p className="flex justify-between">
          <span className="text-gray-500">Delivery Fee</span>
          <span className="font-bold text-green-600">
            {deliveryFee === 0 ? 'Free' : `$${deliveryFee.toFixed(2)}`}
          </span>
        </p>
      </div>

      <Separator />

      <p className="flex justify-between items-baseline">
        <span className="text-gray-700 font-medium">Total</span>
        <span className="font-bold text-2xl">${total.toFixed(2)}</span>
      </p>

      <div className="flex gap-2">
        <div className="flex flex-1 items-center rounded-full bg-gray-100 px-3 sm:px-4 py-1 sm:py-2">
          <Tag className="h-4 w-4 text-gray-500" />
          <Input
            type="text"
            placeholder="Add promo code"
            className="flex-1 border-0 bg-transparent sm:text-md text-sm focus-visible:ring-0 focus-visible:ring-offset-0"
          />
        </div>

        <button
          type="button"
          onClick={() => toast.info('Promo code feature coming soon!')}
          className="rounded-full bg-black px-6 sm:text-md text-sm text-white hover:bg-black/80 transition-colors cursor-pointer"
        >
          Apply
        </button>
      </div>

      <Button
        type="button"
        disabled={!hasItems || placeOrderMutation.isPending || isLoading}
        onClick={handlePlaceOrder}
        className="w-full bg-black text-white rounded-full py-6 font-medium text-base hover:bg-black/90 cursor-pointer shadow-md transition-all active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
      >
        {placeOrderMutation.isPending ? (
          <>
            <Loader2 className="w-5 h-5 animate-spin" />
            <span>Placing Order...</span>
          </>
        ) : (
          <>
            <span>Place Order</span>
            <ArrowRight className="w-5 h-5" />
          </>
        )}
      </Button>

      {/* Payment Confirmation Dialog */}
      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <CreditCard className="w-5 h-5" />
              Confirm Payment
            </DialogTitle>
            <DialogDescription className="text-left pt-2">
              You are about to place an order for <strong>${total.toFixed(2)}</strong>.
              <br />
              Please select a payment method to continue.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            <div className="space-y-3">
              <label className="text-sm font-medium text-gray-700">
                Payment Method (Test Mode)
              </label>
              <div className="space-y-2">
                <label className="flex items-center space-x-3 p-3 border rounded-lg cursor-pointer hover:bg-gray-50 transition-colors">
                  <input
                    type="radio"
                    name="payment"
                    value="tok_success"
                    checked={selectedPaymentToken === 'tok_success'}
                    onChange={(e) => setSelectedPaymentToken(e.target.value)}
                    className="w-4 h-4 text-black focus:ring-black"
                  />
                  <div className="flex-1">
                    <div className="font-medium text-sm">✅ Successful Payment</div>
                    <div className="text-xs text-gray-500">
                      Payment will be processed successfully
                    </div>
                  </div>
                </label>

                <label className="flex items-center space-x-3 p-3 border rounded-lg cursor-pointer hover:bg-gray-50 transition-colors">
                  <input
                    type="radio"
                    name="payment"
                    value="tok_declined"
                    checked={selectedPaymentToken === 'tok_declined'}
                    onChange={(e) => setSelectedPaymentToken(e.target.value)}
                    className="w-4 h-4 text-black focus:ring-black"
                  />
                  <div className="flex-1">
                    <div className="font-medium text-sm">❌ Card Declined</div>
                    <div className="text-xs text-gray-500">Simulate a declined payment</div>
                  </div>
                </label>

                <label className="flex items-center space-x-3 p-3 border rounded-lg cursor-pointer hover:bg-gray-50 transition-colors">
                  <input
                    type="radio"
                    name="payment"
                    value="tok_insufficient_funds"
                    checked={selectedPaymentToken === 'tok_insufficient_funds'}
                    onChange={(e) => setSelectedPaymentToken(e.target.value)}
                    className="w-4 h-4 text-black focus:ring-black"
                  />
                  <div className="flex-1">
                    <div className="font-medium text-sm">💳 Insufficient Funds</div>
                    <div className="text-xs text-gray-500">
                      Simulate insufficient balance
                    </div>
                  </div>
                </label>
              </div>
            </div>

            <div className="bg-gray-50 p-3 rounded-lg">
              <div className="flex justify-between text-sm mb-1">
                <span className="text-gray-600">Subtotal:</span>
                <span className="font-medium">${subtotal.toFixed(2)}</span>
              </div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-gray-600">Delivery:</span>
                <span className="font-medium text-green-600">Free</span>
              </div>
              <Separator className="my-2" />
              <div className="flex justify-between font-bold">
                <span>Total:</span>
                <span className="text-lg">${total.toFixed(2)}</span>
              </div>
            </div>
          </div>

          <DialogFooter className="gap-2">
            <Button
              type="button"
              variant="outline"
              onClick={() => setIsDialogOpen(false)}
              disabled={placeOrderMutation.isPending}
              className="rounded-full"
            >
              Cancel
            </Button>
            <Button
              type="button"
              onClick={handleConfirmPayment}
              disabled={placeOrderMutation.isPending}
              className="bg-black text-white rounded-full hover:bg-black/90 flex items-center gap-2"
            >
              {placeOrderMutation.isPending ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Processing...</span>
                </>
              ) : (
                <>
                  <CreditCard className="w-4 h-4" />
                  <span>Confirm & Pay ${total.toFixed(2)}</span>
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
