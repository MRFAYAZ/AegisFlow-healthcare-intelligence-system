import { useState } from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ToastProvider } from '../components/ui/Toast'
import { AppRouter } from '../routes/AppRouter'
import { SplashScreen } from '../pages/auth/SplashScreen'
import { OnboardingPage } from '../pages/auth/OnboardingPage'

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: 1, staleTime: 30000 } }
})

type AppPhase = 'splash' | 'onboarding' | 'app'

export function App() {
  const [phase, setPhase] = useState<AppPhase>(() => {
    // Only show splash+onboarding on first ever visit
    const seen = localStorage.getItem('aegisflow_onboarded')
    return seen ? 'app' : 'splash'
  })

  function onSplashDone() {
    setPhase('onboarding')
  }

  function onOnboardingDone() {
    localStorage.setItem('aegisflow_onboarded', 'true')
    setPhase('app')
  }

  return (
    <QueryClientProvider client={queryClient}>
      {phase === 'splash' && <SplashScreen onDone={onSplashDone} />}
      {phase === 'onboarding' && <OnboardingPage onDone={onOnboardingDone} />}
      {phase === 'app' && <AppRouter />}
      <ToastProvider />
    </QueryClientProvider>
  )
}
