import { HeroSection } from '../components/home/HeroSection'
import { RecommendedCategories } from '../components/home/RecommendedCategories'
import { FeaturedProducts } from '../components/home/FeaturedProducts'
import { HolidaySection } from '../components/home/HolidaySection'
import { Footer } from '../components/Footer'

export function Home() {
    return (
        <>
            <HeroSection />
            <RecommendedCategories />
            <FeaturedProducts />
            <HolidaySection />
            <Footer />
        </>
    )
}
