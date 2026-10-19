'use client'

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useEffect, useState } from 'react'
import { Toaster } from 'sonner'

export default function Providers({ children }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 5 * 60 * 1000,
          },
        },
      })
  )

  useEffect(() => {
    fetch('http://127.0.0.1:8000/csrf/', {
      credentials: 'include',
    })
  }, [])

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      <Toaster position="bottom-right" richColors closeButton />
    </QueryClientProvider>
  )
}