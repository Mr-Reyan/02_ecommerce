import React from 'react'
import RevCard from './reviews/RevCard'

function Reviews() {
  return (
    <div>
      <RevCard
        description="I absolutely love this t-shirt! The design is unique and the fabric feels so comfortable. As a fellow designer, I appreciate the attention to detail. It's become my favorite go-to shirt."
        rating={3}
        user={'Radclife M.'}
        created_at={'August 16, 2026'}
      />
    </div>
  )
}

export default Reviews
