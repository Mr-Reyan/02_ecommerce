import { apiFetch } from './auth.service'

const BASE_URL = process.env.NEXT_PUBLIC_API_URL

export const addToCart = async (data, id) => {
  const response = await apiFetch(`${BASE_URL}/cart/add/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ product_id: id, ...data }),
  })
  const resData = await response.json().catch(() => ({}))
  if (!response.ok) {
    throw new Error(
      resData.error || resData.message || resData.detail || 'Failed to add item to cart'
    )
  }
  return resData
}

export const getCart = async () => {
  const response = await apiFetch(`${BASE_URL}/cart/`, {
    method: 'GET',
  })
  const resData = await response.json().catch(() => ({}))
  if (!response.ok) {
    throw new Error(
      resData.error || resData.message || resData.detail || 'Failed to fetch cart'
    )
  }
  return resData
}

export const updateCart = async (newQuantity, id) => {
  const response = await apiFetch(`${BASE_URL}/cart/items/${id}/`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ quantity: newQuantity }),
  })
  const resData = await response.json().catch(() => ({}))
  if (!response.ok) {
    throw new Error(
      resData.error || resData.message || resData.detail || 'Failed to update cart'
    )
  }
  return resData
}

export const deleteCartItem = async (prod_id) => {
  const response = await apiFetch(`${BASE_URL}/cart/${prod_id}/`, {
    method: 'DELETE',
  })
  const resData = await response.json().catch(() => ({}))
  if (!response.ok) {
    throw new Error(
      resData.error || resData.message || resData.detail || 'Failed to delete item from cart'
    )
  }
  return resData
}