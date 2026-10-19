// import { Star } from 'lucide-react'
// import Image from 'next/image'
// import React from 'react'

// export default function Card({ img, title, price, rating }) {
//     return (
//         <div className='flex flex-col md:gap-1 '>
//             <div className="md:w-75 sm:w-65 w-50 h-74 overflow-hidden rounded-2xl bg-amber-200 shadow-md">
//                 <Image
//                     src={img}
//                     width={100}
//                     height={100}
//                     className="w-full h-full object-cover transition-transform duration-300 hover:scale-110"
//                     loading="eager"
//                     alt={title}
//                 />
//             </div>
//             <p className='font-bold mt-2 tracking-wide md:text-[20px] text-[16px] hover:underline'>
//                 {title}
//             </p>
//             <div className='flex'>
//                 <Star fill='gold' strokeWidth={0} className='text-yellow-300' />
//                 <Star fill='gold' strokeWidth={0} className='text-yellow-300' />
//                 <Star fill='gold' strokeWidth={0} className='text-yellow-300' />
//             </div>
//             <div>
//                 <p className='font-extrabold md:text-[24px] text-[18px] '>
//                     ${price}
//                 </p>
//             </div>
//         </div>
//     )
// }

import { Star } from 'lucide-react'
import Image from 'next/image'
import React from 'react'

export default function Card({ img, title, price, rating }) {
  return (
    <div className="flex w-full min-w-30 flex-col">
      {/* Image */}
      <div className="aspect-3/4 w-full overflow-hidden rounded-2xl bg-gray-200 shadow-md">
        <Image
          src={img || '/img/newarrivals/shirt1.png'}
          width={600}
          height={800}
        //   unoptimized
          className="h-full w-full object-cover transition-transform duration-300 hover:scale-110"
          alt={title || 'Product image'}
        />
      </div>

      {/* Title */}
      <p className="mt-2 truncate text-base font-bold tracking-wide hover:underline sm:text-lg md:text-xl ">
        {title}
      </p>

      {/* Rating */}
      <div className="flex">
        <Star
          fill="gold"
          strokeWidth={0}
          className="h-4 w-4 text-yellow-300 sm:h-5 sm:w-5"
        />
        <Star
          fill="gold"
          strokeWidth={0}
          className="h-4 w-4 text-yellow-300 sm:h-5 sm:w-5"
        />
        <Star
          fill="gold"
          strokeWidth={0}
          className="h-4 w-4 text-yellow-300 sm:h-5 sm:w-5"
        />
      </div>

      {/* Price */}
      <p className="text-lg font-extrabold sm:text-xl md:text-xl lg:text-2xl">
        ${price}
      </p>
    </div>
  )
}
