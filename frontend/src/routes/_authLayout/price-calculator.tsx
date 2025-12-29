import { createFileRoute } from '@tanstack/react-router'
import PricingCalculator from '@/containers/priceCalculator'

export const Route = createFileRoute('/_authLayout/price-calculator')({
  component: HomeComponent,
})

function HomeComponent() {
  return <PricingCalculator />
}
