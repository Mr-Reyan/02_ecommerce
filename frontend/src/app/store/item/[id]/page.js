'use client'
import { Star, Check, Loader2 } from 'lucide-react'
import Image from 'next/image'
import React, { useEffect, useState } from 'react'
import { IntegralCF, SatoshiThin } from '@/components/fonts'
import { Separator } from '@/components/ui/separator'
import { ToggleGroup, ToggleGroupItem } from '@/components/ui/toggle-group'
import Counter from '../counter'
import Reviews from '../Reviews'
import { useParams } from 'next/navigation'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { getInventory, getProduct } from '@/services/product.service'
import ProductSkeleton from './skeleton'
import { Controller, useForm, useWatch } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { ProductSchema } from '@/lib/validations/product.schema'
import { addToCart } from '@/services/cart.service'
import { toast } from 'sonner'
const COLOR_CLASSES = {
    blue: 'bg-blue-600',
    green: 'bg-green-600',
    red: 'bg-red-600',
    black: 'bg-black',
    white: 'bg-white shadow-md',
}

const ProductDetailPage = () => {
    const [picture, setPicture] = useState('')
    const params = useParams('id')

    const { data: product = {}, isLoading, isError } = useQuery({
        queryKey: ['product', params.id],
        queryFn: () => getProduct(params.id)
    })




    const SIZES = product?.specifications?.sizes ?? []

    // const COLORS = product?.specifications?.color?.map((clr) => ({
    //         name: clr,
    //         className: COLOR_CLASSES[clr.toLowerCase()] ?? 'bg-gray-600',
    //     })) ?? []

    const COLOR = {
        name: product?.specifications?.color,
        className: COLOR_CLASSES[product?.specifications?.color?.toLowerCase()] ?? 'bg-gray-600'
    }

    const selectedPicture = picture || product?.images?.[0]?.image || ''

    const queryClient = useQueryClient()

    const {
        handleSubmit,
        reset,
        control,
        setValue,
    } = useForm({
        resolver: zodResolver(ProductSchema),
        defaultValues: {
            size: '',
            color: '',
            quantity: 1,
        },
    })

    const selectedSize = useWatch({ control, name: 'size' })
    const sizeStockMap = product?.specifications?.size_stock || {}
    const currentStock = selectedSize
        ? (sizeStockMap[selectedSize] !== undefined ? sizeStockMap[selectedSize] : (product?.stock?.stock ?? 0))
        : (product?.stock?.stock ?? 0)



    const [isAddedSuccess, setIsAddedSuccess] = useState(false)
    const [isSubmitting, setIsSubmitting] = useState(false)

    if (isLoading) {
        return <ProductSkeleton />
    }

    if (isError) {
        return <div>Failed to load product</div>
    }

    if (!product) {
        return <div>Product not found</div>
    }

    const onSubmit = async (data) => {
        if (isAddedSuccess || isSubmitting) return
        setIsSubmitting(true)
        try {
            const res = await addToCart(data, params.id)
            queryClient.invalidateQueries({ queryKey: ['cart'] })
            setIsAddedSuccess(true)
            toast.success(res?.info || res?.message || 'Added to cart!')
            setTimeout(() => {
                setIsAddedSuccess(false)
            }, 2000)
        } catch (err) {
            toast.error(err?.message || 'Could not add item to cart. Please try again.')
        } finally {
            setIsSubmitting(false)
        }
    }



    return (
        <div>
            {/* <ProductSkeleton/> */}
            <div className="mt-6 flex w-full flex-col gap-6 px-4 sm:px-6 md:mt-10 md:flex-row md:px-8 lg:gap-8 lg:px-12 xl:px-20">
                <div className="hidden shrink-0 md:block">
                    <div className="flex flex-col gap-3">
                        {product?.images?.map((img) => {
                            console.log(img);

                            return (

                                <Image
                                    alt="ONE LIFE GRAPHIC SHIRT"
                                    key={img.image}
                                    src={img.image}
                                    width={160}
                                    height={200}
                                    onClick={(e) => setPicture(img.image)}
                                    className="cursor-pointer hover:border-2 transition-all h-auto w-24 rounded-lg object-cover lg:w-32"
                                />
                            )
                        })}


                    </div>
                </div>

                <div className="w-full md:w-[45%] lg:w-[42%]">
                    {selectedPicture && (
                        <Image
                            alt={product.name || "Product image"}
                            src={selectedPicture}
                            width={520}
                            height={650}
                            className="w-full h-[600px] md:h-[500px] rounded-lg object-cover"
                            priority
                        />
                    )}

                </div>

                <div className="md:hidden shrink-0 block">
                    <div className="flex flex-row overflow-x-auto gap-3">
                        {product?.images?.map((img) => {
                            return (

                                <Image
                                    alt="ONE LIFE GRAPHIC SHIRT"
                                    key={img.image}
                                    src={img.image}
                                    width={160}
                                    height={200}
                                    onClick={(e) => setPicture(img.image)}
                                    className="cursor-pointer hover:border-2 transition-all h-auto w-24 rounded-lg object-cover lg:w-32"
                                />
                            )
                        })}
                    </div>
                </div>

                <form onSubmit={handleSubmit(onSubmit)} className="flex w-full flex-col gap-4 md:w-[45%] lg:w-[42%]">
                    <p
                        className={`${IntegralCF.className} text-2xl leading-tight sm:text-4xl lg:text-5xl`}
                    >
                        {product.name}
                    </p>

                    <div className="flex items-center">
                        <Star
                            fill="gold"
                            strokeWidth={0}
                            className="h-5 w-5 text-yellow-300"
                        />
                        <Star
                            fill="gold"
                            strokeWidth={0}
                            className="h-5 w-5 text-yellow-300"
                        />
                        <Star
                            fill="gold"
                            strokeWidth={0}
                            className="h-5 w-5 text-yellow-300"
                        />
                        <span className="ml-2 text-gray-500">
                            <span className="text-black">3/</span>5
                        </span>
                    </div>

                    <p className="text-xl font-bold sm:text-2xl flex items-center gap-3">
                        ${product.price}
                        <span className={`text-sm ${SatoshiThin.className} ${currentStock > 0 ? 'text-gray-600' : 'text-red-500 font-semibold'}`}>
                            {selectedSize
                                ? currentStock > 0
                                    ? `(${currentStock} in Stock for ${selectedSize})`
                                    : `(Out of Stock for ${selectedSize})`
                                : product?.stock?.stock !== undefined
                                    ? `(${product.stock.stock} in Stock)`
                                    : 'Stock Unavailable'}
                        </span>
                    </p>

                    <p className="text-sm leading-6 text-gray-400 sm:text-base">
                        {product.description}
                    </p>

                    <Separator />

                    <div className="flex flex-col gap-3">
                        <p className="font-medium">Select Colors</p>
                        <Controller
                            name="color"
                            control={control}
                            render={({ field, fieldState }) => (
                                <div>

                                    <ToggleGroup
                                        type="single"
                                        value={field.value}
                                        onValueChange={field.onChange}
                                    >
                                        <ToggleGroupItem
                                            key={COLOR.name}
                                            value={COLOR.name}
                                            aria-label={`Select ${COLOR.name}`}
                                            className={`group relative h-9 w-9 rounded-full ${COLOR.className}
                                        hover:${COLOR.className}
                                        hover:opacity-70
                                        transition-opacity
                                        data-[state=on]:${COLOR.className}
                                        `}
                                        >
                                            <Check
                                                stroke="green"
                                                strokeWidth={3}
                                                className="
                                            absolute -right-1 -top-1
                                            h-4 w-4 rounded-full
                                            bg-white p-0.5 text-black
                                            opacity-0
                                            group-data-[state=on]:opacity-100
                                            "
                                            />
                                        </ToggleGroupItem>

                                    </ToggleGroup>
                                    {fieldState.error && (
                                        <p className="mt-1 text-sm text-red-500">
                                            {fieldState.error.message}
                                        </p>
                                    )}
                                </div>
                            )}
                        />
                    </div>

                    <Separator />

                    <div className="flex flex-col gap-3">
                        <div className="flex items-center justify-between">
                            <p className="font-medium">Choose Size</p>
                            {selectedSize && sizeStockMap[selectedSize] !== undefined && (
                                <span className="text-xs text-gray-400">
                                    {sizeStockMap[selectedSize] > 0 ? `${sizeStockMap[selectedSize]} left` : 'Out of stock'}
                                </span>
                            )}
                        </div>
                        <Controller
                            name="size"
                            control={control}
                            render={({ field, fieldState }) => (
                                <div>
                                    <ToggleGroup
                                        className="flex flex-wrap gap-2"
                                        type="single"
                                        value={field.value}
                                        onValueChange={(val) => {
                                            field.onChange(val)
                                            setValue('quantity', 1)
                                        }}
                                    >
                                        {SIZES.map((size) => {
                                            const sizeStock = sizeStockMap[size] !== undefined ? sizeStockMap[size] : (product?.stock?.stock ?? 10)
                                            const isOutOfStock = sizeStock === 0

                                            return (
                                                <ToggleGroupItem
                                                    key={size}
                                                    value={size}
                                                    disabled={isOutOfStock}
                                                    title={isOutOfStock ? `${size} is Out of Stock` : `${size} (${sizeStock} available)`}
                                                    className={`
                                                    rounded-full
                                                    px-4 py-2
                                                    text-sm
                                                    sm:text-base
                                                    transition-all
                                                    ${
                                                        isOutOfStock
                                                            ? 'bg-gray-100 text-gray-400 opacity-40 line-through cursor-not-allowed border border-dashed border-gray-300 pointer-events-none'
                                                            : 'bg-gray-200 text-gray-700 hover:bg-gray-300 data-[state=on]:bg-black data-[state=on]:text-white cursor-pointer'
                                                    }
                                                `}
                                                >
                                                    {size}
                                                </ToggleGroupItem>
                                            )
                                        })}
                                    </ToggleGroup>
                                    {fieldState.error && (
                                        <p className="mt-1 text-sm text-red-500">
                                            {fieldState.error.message}
                                        </p>
                                    )}
                                </div>
                            )}
                        />
                    </div>

                    <Separator />

                    <div className="flex w-full gap-3">
                        <Controller
                            name="quantity"
                            control={control}
                            render={({ field, fieldState }) => (
                                <div>
                                    <Counter
                                        value={field.value}
                                        onChange={field.onChange}
                                        max={currentStock > 0 ? currentStock : 1}
                                    />
                                    {fieldState.error && (
                                        <p className="mt-1 text-sm text-red-500">
                                            {fieldState.error.message}
                                        </p>
                                    )}
                                </div>
                            )}
                        />


                        <button
                            type='submit'
                            disabled={(currentStock === 0 && Boolean(selectedSize)) || isAddedSuccess || isSubmitting}
                            className={`
                                h-12 flex-1
                                rounded-full
                                px-6
                                text-sm font-medium
                                transition-all duration-300
                                flex items-center justify-center gap-2
                                ${
                                    isAddedSuccess
                                        ? 'bg-emerald-600 text-white scale-[0.99] shadow-inner'
                                        : (currentStock === 0 && Boolean(selectedSize))
                                            ? 'bg-gray-400 cursor-not-allowed opacity-60 text-white'
                                            : 'bg-black hover:opacity-85 text-white active:scale-[0.98] cursor-pointer'
                                }
                            `}
                        >
                            {isAddedSuccess ? (
                                <span className="flex items-center gap-2 animate-in zoom-in-50 duration-200">
                                    <Check className="w-5 h-5 text-white stroke-[3]" />
                                    <span>Added to Cart</span>
                                </span>
                            ) : isSubmitting ? (
                                <span className="flex items-center gap-2">
                                    <Loader2 className="w-5 h-5 animate-spin" />
                                    <span>Adding...</span>
                                </span>
                            ) : currentStock === 0 && Boolean(selectedSize) ? (
                                'Out of Stock'
                            ) : (
                                'Add to Cart'
                            )}
                        </button>

                    </div>
                </form>
            </div>

            {/* <div>
                <Reviews/>
            </div> */}
        </div>
    )
}

export default ProductDetailPage
