'use client'
import { useQuery } from "@tanstack/react-query"
import z from "zod"



export const ProductSchema = z.object({
    size: z.string().min(1, "Please select a size"),
    color: z.string().min(1, "Please select a color"),
    quantity: z.number().min(1, "Quantity must be at least 1"),
})
