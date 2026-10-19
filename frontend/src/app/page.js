import { Hero } from './home/hero'
import { NewArrivals } from './home/NewArrivals'

export default function Home() {
  return (
    <main className="min-h-screen bg-white">
      <header>
        <Hero />
      </header>
      <NewArrivals />
    </main>
  )
}
