'use client'
import { Skeleton } from '@/components/ui/skeleton'

export default function ProductSkeleton() {
    return (
        <div>
            <div className="mt-6 flex w-full flex-col gap-6 px-4 sm:px-6 md:mt-10 md:flex-row md:px-8 lg:gap-8 lg:px-12 xl:px-20">
                <div className="hidden shrink-0 md:block">
                    <div className="flex flex-col gap-3">

                        <Skeleton
                            className="cursor-pointer hover:border-2 transition-all  w-24 rounded-lg object-cover lg:w-32 h-40"
                        ></Skeleton>
                        <Skeleton
                            className="cursor-pointer hover:border-2 transition-all  w-24 rounded-lg object-cover lg:w-32 h-40"
                        ></Skeleton>


                    </div>
                </div>

                <div className="w-full md:w-[45%] lg:w-[42%]">
                    <Skeleton
                        className="h-130 w-130 rounded-lg object-cover"
                    ></Skeleton>

                </div>



                <div className="flex w-full flex-col gap-4 md:w-[45%] lg:w-[42%]">
                    

                    <Skeleton className="w-full h-10"></Skeleton>
                    <Skeleton className="w-20 h-10"></Skeleton>

                    <Skeleton className="h-10 w-18"></Skeleton>
                </div>

            </div>
        </div>
    )
}

