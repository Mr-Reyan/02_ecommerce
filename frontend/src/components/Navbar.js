'use client'

import React, { useCallback, useEffect, useState } from 'react'
import { ShoppingBag, Menu, UserCircle2, X, LogOut, LogIn } from 'lucide-react'
import { IntegralCF } from '@/components/fonts'
import Link from 'next/link'
import { useQuery } from '@tanstack/react-query'
import { getCart } from '@/services/cart.service'
import { useRouter, usePathname } from 'next/navigation'
import { toast } from 'sonner'

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const Navbar = () => {
  const router = useRouter()
  const pathname = usePathname()
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)
  const [showUserMenu, setShowUserMenu] = useState(false)

  const checkAuth = useCallback(async () => {
    try {
      const response = await fetch(`${BASE_URL}/status/`, {
        credentials: 'include',
      })

      if (response.ok) {
        const data = await response.json()
        console.log('Auth status response:', data) // remove once working
        setIsAuthenticated(
          Boolean(
            data.authenticated ??
              data.isAuthenticated ??
              data.is_authenticated ??
              data.user
          )
        )
      } else {
        console.warn('Auth status request failed:', response.status)
        setIsAuthenticated(false)
      }
    } catch (error) {
      console.error('Auth check failed:', error)
      setIsAuthenticated(false)
    }
  }, [])

  // Re-check on mount, on every route change (e.g. after login redirect),
  // and when the tab regains focus
  useEffect(() => {
    checkAuth()
  }, [checkAuth, pathname])

  useEffect(() => {
    window.addEventListener('focus', checkAuth)
    return () => window.removeEventListener('focus', checkAuth)
  }, [checkAuth])

  const { data: cart } = useQuery({
    queryKey: ['cart'],
    queryFn: getCart,
    staleTime: 1000 * 30,
    enabled: isAuthenticated,
    retry: false,
  })

  const totalCartCount =
    cart?.items?.reduce((total, item) => total + (item.quantity || 1), 0) || 0

  const handleLogout = async () => {
    try {
      const response = await fetch(`${BASE_URL}/logout/`, {
        method: 'POST',
        credentials: 'include',
      })

      if (response.ok) {
        toast.success('Logged out successfully!')
        setIsAuthenticated(false)
        setShowUserMenu(false)
        router.push('/login')
      } else {
        toast.error('Logout failed')
      }
    } catch (error) {
      toast.error('Logout failed')
    }
  }

  return (
    <header className="border-b relative">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between gap-4">
          <button
            className="lg:hidden"
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            aria-label="Toggle menu"
          >
            {isMobileMenuOpen ? (
              <X className="h-6 w-6" />
            ) : (
              <Menu className="h-6 w-6" />
            )}
          </button>

          <Link href="/" className={`${IntegralCF.className} text-2xl font-bold`}>
            SHOP.CO
          </Link>

          <nav className="hidden lg:flex items-center min-w-80 gap-5">
            <Link href="/store" className="text-md hover:text-gray-600 transition-colors">
              Store
            </Link>
            {isAuthenticated && (
              <Link href="/orders" className="text-md hover:text-gray-600 transition-colors">
                Orders
              </Link>
            )}
          </nav>

          <div className="flex items-center gap-2">
            {isAuthenticated && (
              <Link
                href="/cart"
                aria-label="View Shopping Cart"
                className="relative flex h-10 w-10 items-center justify-center rounded-full text-black hover:bg-gray-100 transition-colors"
              >
                <ShoppingBag className="w-5 h-5" />
                {totalCartCount > 0 && (
                  <span className="absolute top-1 right-1 flex h-4 min-w-4 items-center justify-center rounded-full bg-black px-1 text-[10px] font-bold text-white leading-none">
                    {totalCartCount > 99 ? '99+' : totalCartCount}
                  </span>
                )}
              </Link>
            )}

            {/* User Menu */}
            <div className="relative">
              <button
                type="button"
                onClick={() => setShowUserMenu(!showUserMenu)}
                aria-label="User menu"
                className="flex h-10 w-10 items-center justify-center rounded-full text-black hover:bg-gray-100 transition-colors"
              >
                <UserCircle2 className="w-5 h-5" />
              </button>

              {/* Dropdown Menu */}
              {showUserMenu && (
                <>
                  {/* Backdrop for user menu only */}
                  <div
                    className="fixed inset-0 z-40"
                    onClick={() => setShowUserMenu(false)}
                  />
                  <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-2 z-50">
                    {isAuthenticated ? (
                      <>
                        <Link
                          href="/orders"
                          className="flex items-center gap-2 px-4 py-2 text-sm hover:bg-gray-100 transition-colors"
                          onClick={() => setShowUserMenu(false)}
                        >
                          <ShoppingBag className="w-4 h-4" />
                          My Orders
                        </Link>
                        <button
                          onClick={handleLogout}
                          className="w-full flex items-center gap-2 px-4 py-2 text-sm hover:bg-gray-100 transition-colors text-red-600"
                        >
                          <LogOut className="w-4 h-4" />
                          Logout
                        </button>
                      </>
                    ) : (
                      <>
                        <Link
                          href="/login"
                          className="flex items-center gap-2 px-4 py-2 text-sm hover:bg-gray-100 transition-colors"
                          onClick={() => setShowUserMenu(false)}
                        >
                          <LogIn className="w-4 h-4" />
                          Login
                        </Link>
                        <Link
                          href="/signup"
                          className="flex items-center gap-2 px-4 py-2 text-sm hover:bg-gray-100 transition-colors"
                          onClick={() => setShowUserMenu(false)}
                        >
                          <UserCircle2 className="w-4 h-4" />
                          Sign Up
                        </Link>
                      </>
                    )}
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Mobile Menu Dropdown */}
      {isMobileMenuOpen && (
        <div className="lg:hidden absolute top-full left-0 right-0 bg-white border-b shadow-lg z-50">
          <nav className="container mx-auto px-4 py-4 flex flex-col gap-3">
            <Link
              href="/store"
              className="text-lg py-2 hover:text-gray-600 transition-colors"
              onClick={() => setIsMobileMenuOpen(false)}
            >
              Store
            </Link>
            {isAuthenticated && (
              <Link
                href="/orders"
                className="text-lg py-2 hover:text-gray-600 transition-colors"
                onClick={() => setIsMobileMenuOpen(false)}
              >
                Orders
              </Link>
            )}
            <div className="border-t pt-3 mt-2">
              {isAuthenticated ? (
                <button
                  onClick={() => {
                    handleLogout()
                    setIsMobileMenuOpen(false)
                  }}
                  className="flex items-center gap-2 text-lg py-2 text-red-600 hover:text-red-700 transition-colors"
                >
                  <LogOut className="w-5 h-5" />
                  Logout
                </button>
              ) : (
                <>
                  <Link
                    href="/login"
                    className="flex items-center gap-2 text-lg py-2 hover:text-gray-600 transition-colors"
                    onClick={() => setIsMobileMenuOpen(false)}
                  >
                    <LogIn className="w-5 h-5" />
                    Login
                  </Link>
                  <Link
                    href="/signup"
                    className="flex items-center gap-2 text-lg py-2 hover:text-gray-600 transition-colors"
                    onClick={() => setIsMobileMenuOpen(false)}
                  >
                    <UserCircle2 className="w-5 h-5" />
                    Sign Up
                  </Link>
                </>
              )}
            </div>
          </nav>
        </div>
      )}

      {/* Mobile menu backdrop */}
      {isMobileMenuOpen && (
        <div
          className="fixed inset-0 z-40 lg:hidden"
          onClick={() => setIsMobileMenuOpen(false)}
        />
      )}
    </header>
  )
}

export default Navbar