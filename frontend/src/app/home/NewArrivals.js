import React from 'react'
import Card from './card'
import { IntegralCF } from '@/components/fonts'
export function NewArrivals() {
  return (
    <div className="mt-17 flex flex-col md:px-20 px-5 ">
      <h1
        className={`${IntegralCF.className} text-3xl md:text-5xl text-center`}
      >
        NEW ARRIVALS
      </h1>
      <div className="mt-10 flex gap-3  overflow-y-auto">
        <Card
          img={'/img/newarrivals/shirt1.png'}
          title={'Sleeve Stripped T-shirt'}
          price={130}
          rating={4.5}
        />
        <Card
          img={'/img/newarrivals/shirt1.png'}
          title={'Sleeve Stripped T-shirt'}
          price={130}
          rating={4.5}
        />
        <Card
          img={'/img/newarrivals/shirt1.png'}
          title={'Sleeve Stripped T-shirt'}
          price={130}
          rating={4.5}
        />
        <Card
          img={'/img/newarrivals/shirt1.png'}
          title={'Sleeve Stripped T-shirt'}
          price={130}
          rating={4.5}
        />
        <Card
          img={'/img/newarrivals/shirt1.png'}
          title={'Sleeve Stripped T-shirt'}
          price={130}
          rating={4.5}
        />
      </div>
    </div>
  )
}
