import { apiFetch } from "./auth.service"

const BASE_URL = process.env.NEXT_PUBLIC_API_URL

export const getProducts = async (page = 1, pageSize = 20, filters = {}) => {
    const params = new URLSearchParams()
    params.set('page', page)
    params.set('page_size', pageSize)
    if (filters.min_price !== undefined && filters.min_price !== null && filters.min_price !== '') {
        params.set('min_price', filters.min_price)
    }
    if (filters.max_price !== undefined && filters.max_price !== null && filters.max_price !== '') {
        params.set('max_price', filters.max_price)
    }
    if (filters.color) {
        params.set('color', filters.color)
    }
    if (filters.category) {
        params.set('category', filters.category)
    }
    const response = await apiFetch(`${BASE_URL}/products/?${params.toString()}`, {
        method: 'GET',
    })
    return await response.json()
}
export const getProduct = async (id)=>{
    const response = await apiFetch(`${BASE_URL}/products/${id}/`,{
        method:'GET'
    })
    return await response.json()
}

export const getInventory = async (id) =>{
    const response = await apiFetch(`${BASE_URL}/inventory/${id}/`,{
        method:'GET'
    })
    const data = await response.json()
    return data.stock
}