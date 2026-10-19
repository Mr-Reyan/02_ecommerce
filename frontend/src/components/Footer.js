import { Mail, X } from 'lucide-react'
import { Button } from '@/components/ui/button'
import React from 'react'
import { Input } from './ui/input'
import { IntegralCF, SatoshiThin } from './fonts'
import { FaFacebook, FaGithub, FaInstagram, FaTwitter } from 'react-icons/fa'
import { Visa, Mastercard, Paypal } from 'react-payment-logos/dist/flat'
import Link from 'next/link'
import { Separator } from '@/components/ui/separator'

export default function Footer() {
  return (
    <div className="relative mt-30 bg-gray-200">
      <div className="absolute -top-20 bg-black flex flex-col gap-6 lg:gap-0 lg:flex-row p-6 lg:p-8 mx-5 sm:mx-10 md:mx-22 rounded-3xl">
        <p
          className={`text-white ${IntegralCF.className} text-2xl sm:text-3xl lg:text-4xl`}
        >
          STAY UP TO DATE ABOUT OUR LATEST OFFERS
        </p>
        <div className="flex flex-col gap-4">
          <div className="flex items-center w-full  sm:min-w-100  bg-gray-100 rounded-full px-4 py-2">
            <Mail className="h-4 w-4 text-gray-500" />
            <Input
              type="text"
              placeholder="Enter your email address"
              className="border-0 bg-transparent focus-visible:ring-0 focus-visible:ring-offset-0 text-md flex-1 w-auto lg:w-full"
            />
          </div>
          <Button
            variant="outline"
            className="py-6 rounded-full font-bold text-md lg:text-lg border-0"
          >
            Subscribe to Newsletter
          </Button>
        </div>
      </div>
      <div className="lg:pt-40 pt-50 flex lg:flex-row flex-col  gap-5 md:px-20 sm:px-15 px-10 ">
        <div className=" max-w-270 mb-2 pr-5">
          <p className={`${IntegralCF.className}  text-4xl font-bold`}>
            SHOP.CO
          </p>
          <p className="mt-5 text-gray-500">
            We have clothes that suit your style and which you&apos;re proud to wear.
            From women to men.
          </p>
          <div className="flex gap-2 mt-10">
            <Link href="#">
              <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center">
                <FaTwitter size={25} />
              </div>
            </Link>
            <Link href="#">
              <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center">
                <FaFacebook size={25} />
              </div>
            </Link>
            <Link href="#">
              <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center">
                <FaInstagram size={25} />
              </div>
            </Link>
            <Link href="#">
              <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center">
                <FaGithub size={25} />
              </div>
            </Link>
          </div>
        </div>
        <div className="sm:flex sm:justify-between grid grid-cols-2 gap-7 w-full ">
          <div className="flex text-gray-600  flex-col gap-5">
            <p className="text-xl text-black font-bold tracking-widest">
              COMPANY
            </p>
            <Link href="#" className="hover:underline">
              About
            </Link>
            <Link href="#" className="hover:underline">
              Features
            </Link>
            <Link href="#" className="hover:underline">
              Works
            </Link>
            <Link href="#" className="hover:underline">
              Career
            </Link>
          </div>
          <div className="flex text-gray-600  flex-col gap-5">
            <p className="text-xl text-black font-bold tracking-widest">
              COMPANY
            </p>
            <Link href="#" className="hover:underline">
              About
            </Link>
            <Link href="#" className="hover:underline">
              Features
            </Link>
            <Link href="#" className="hover:underline">
              Works
            </Link>
            <Link href="#" className="hover:underline">
              Career
            </Link>
          </div>
          <div className="flex text-gray-600  flex-col gap-5">
            <p className="text-xl text-black font-bold tracking-widest">
              COMPANY
            </p>
            <Link href="#" className="hover:underline">
              About
            </Link>
            <Link href="#" className="hover:underline">
              Features
            </Link>
            <Link href="#" className="hover:underline">
              Works
            </Link>
            <Link href="#" className="hover:underline">
              Career
            </Link>
          </div>
          <div className="flex text-gray-600  flex-col gap-5">
            <p className="text-xl text-black font-bold tracking-widest">
              COMPANY
            </p>
            <Link href="#" className="hover:underline">
              About
            </Link>
            <Link href="#" className="hover:underline">
              Features
            </Link>
            <Link href="#" className="hover:underline">
              Works
            </Link>
            <Link href="#" className="hover:underline">
              Career
            </Link>
          </div>
        </div>
      </div>
      <div className="my-10 px-10">
        <Separator className="bg-gray-400 " />
        <div className="flex flex-col sm:flex-row justify-between items-center">
          <p className={`sm:text-xl text-xs py-2 sm:py-0 text-gray-500 ${SatoshiThin.className}`}>
            Shop.co &copy; 2026-Present, All Rights Reserved
          </p>
          <div className="flex items-center gap-4">
            <Visa width={60} />
            <Mastercard width={60} />
            <Paypal width={60} />
          </div>
        </div>
      </div>
    </div>
  )
}
