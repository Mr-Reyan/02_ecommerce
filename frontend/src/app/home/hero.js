import React from 'react'
import { IntegralCF } from '@/components/fonts'

import { Button } from '@/components/ui/button'
import Image from 'next/image'
import HeroImage from '@/../public/img/hero-img.png'
import Link from 'next/link'

export function Hero() {
  return (
    <div className="bg-[#F3F0F1]">
      <section className="container mx-auto px-4 pt-10 lg:pt-18 ">
        <div className="grid lg:grid-cols-2 gap-12 items-center ">
          <div>
            <h1
              className={`sm:text-4xl text-3xl lg:text-5xl ${IntegralCF.className} font-bold  leading-tight mb-6`}
            >
              FIND CLOTHES&nbsp;
              <br className="hidden md:block" />
              THAT MATCHES&nbsp;
              <br className="hidden md:block" />
              YOUR STYLE
            </h1>
            <p className="text-gray-600 text-lg mb-8  max-w-lg">
              Browse through our diverse range of meticulously crafted garments,
              designed to bring out your individuality and cater to your sense
              of style.
            </p>
            <Link href='/store'>
            <Button size="lg" className="cursor-pointer rounded-full px-8 py-6 text-base">
              Shop Now
            </Button>
            </Link>

            <div className="flex flex-wrap gap-8 mt-12">
              <div className="w-37.5">
                <p className="text-2xl font-bold">200+</p>
                <p className="text-sm text-gray-500">International Brands</p>
              </div>
              <div className="w-37.5">
                <p className="text-2xl font-bold">2,000+</p>
                <p className="text-sm text-gray-500">High-Quality Products</p>
              </div>
              <div className="w-37.5">
                <p className="text-2xl font-bold">30,000+</p>
                <p className="text-sm text-gray-500">Happy Customers</p>
              </div>
            </div>
          </div>

          <div className="relative">
            <div className="rounded-3xl relative h-[300px] md:h-[500px] overflow-hidden flex items-center justify-center">
              <Image
                src={HeroImage}
                fill
                priority
                // sizes='(max-width:768px) 100vw ,50vw'
                alt="Hero-section-image"
                className="h-full object-cover object-[95%] "
              />
            </div>
          </div>
        </div>
      </section>

      <section className="bg-black py-8">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-8">
            {['VERSACE', 'ZARA', 'GUCCI', 'PRADA', 'CALVIN KLEIN'].map(
              (brand) => (
                <div
                  key={brand}
                  className="text-white text-xl font-bold text-center opacity-70 hover:opacity-100 transition-opacity"
                >
                  {brand}
                </div>
              ),
            )}
          </div>
        </div>
      </section>
    </div>
  )
}
